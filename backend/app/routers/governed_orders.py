from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json, re, uuid
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..auth_utils import decode_token, security
from ..database import get_db
from ..order_domain import evaluate_order, can_transition

router = APIRouter(prefix="/api/governed-orders", tags=["Governed orders"])
KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
PROVIDERS = {"inventory", "tax", "payment", "shipping", "fulfillment", "notification", "webhook"}

class OrderRequest(BaseModel):
    subject_id: str; customer_actor_id: str; merchant_id: str; inventory_snapshot_version: str; tax_quote_ref: str
    items: list[dict]; tax: float = 0; shipping: float = 0; discount: float = 0; total: float

class TransitionRequest(BaseModel):
    from_state: str; to_state: str; version: int = Field(ge=1); reason: str = Field(min_length=1, max_length=500)

class ResultRequest(BaseModel):
    result: str; receipt: dict | None = None; error_code: str | None = None

def context(credentials: HTTPAuthorizationCredentials = Depends(security)):
    claims = decode_token(credentials.credentials)
    actor, tenant, role = str(claims.get("sub", "")), str(claims.get("tenantId", "")), str(claims.get("role", ""))
    subjects = claims.get("subjectIds", [])
    if not actor or not tenant or not role or not isinstance(subjects, list) or not subjects:
        raise HTTPException(403, "signed actor, tenant, role, and subject scope required")
    if role == "admin": subjects = ["*"]
    return {"actor": actor, "tenant": tenant, "role": role, "subjects": set(map(str, subjects))}

def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def allowed(ctx, subject): return "*" in ctx["subjects"] or subject in ctx["subjects"]

@router.post("", status_code=201)
def create_order(data: OrderRequest, response: Response, idempotency_key: str = Header(alias="Idempotency-Key"), ctx=Depends(context), db: Session=Depends(get_db)):
    if not KEY.match(idempotency_key or "") or not allowed(ctx, data.subject_id): raise HTTPException(403, "valid idempotency key and subject scope required")
    body = data.model_dump(); evaluation = evaluate_order(body, ctx["actor"])
    if evaluation["errors"]: raise HTTPException(422, evaluation)
    request_hash, order_id = digest(body), str(uuid.uuid4())
    row = db.execute(text("""INSERT INTO governed_orders(tenant_id,id,subject_id,customer_actor_id,merchant_id,state,request,totals,idempotency_key,request_hash)
      VALUES(:tenant,CAST(:id AS uuid),:subject,:actor,:merchant,'reservation_pending',CAST(:request AS jsonb),CAST(:totals AS jsonb),:key,:hash)
      ON CONFLICT(tenant_id,idempotency_key) DO NOTHING RETURNING *"""), {"tenant":ctx["tenant"],"id":order_id,"subject":data.subject_id,"actor":ctx["actor"],"merchant":data.merchant_id,"request":json.dumps(body),"totals":json.dumps(evaluation["result"]),"key":idempotency_key,"hash":request_hash}).mappings().first()
    if not row:
        row=db.execute(text("SELECT * FROM governed_orders WHERE tenant_id=:tenant AND idempotency_key=:key AND request_hash=:hash"),{"tenant":ctx["tenant"],"key":idempotency_key,"hash":request_hash}).mappings().first()
        if not row: db.rollback(); raise HTTPException(409,"idempotency key reused for another request")
        response.status_code=200; db.rollback(); return dict(row)
    db.execute(text("INSERT INTO governed_order_events(tenant_id,order_id,actor_id,event_type) VALUES(:tenant,CAST(:id AS uuid),:actor,'created')"),{"tenant":ctx["tenant"],"id":order_id,"actor":ctx["actor"]})
    db.execute(text("""INSERT INTO governed_order_outbox(tenant_id,order_id,provider,operation,payload,idempotency_key,request_hash)
      VALUES(:tenant,CAST(:id AS uuid),'inventory','reserve',CAST(:payload AS jsonb),:key,:hash)"""),{"tenant":ctx["tenant"],"id":order_id,"payload":json.dumps({"items":body["items"],"snapshotVersion":body["inventory_snapshot_version"]}),"key":f"{idempotency_key}:reserve","hash":digest(body["items"])})
    db.commit(); return dict(row)

@router.get("/{order_id}")
def get_order(order_id: str, ctx=Depends(context), db: Session=Depends(get_db)):
    row=db.execute(text("SELECT * FROM governed_orders WHERE tenant_id=:tenant AND id=CAST(:id AS uuid)"),{"tenant":ctx["tenant"],"id":order_id}).mappings().first()
    if not row or not allowed(ctx,row["subject_id"]): raise HTTPException(404,"not found")
    return dict(row)

@router.post("/{order_id}/transition")
def transition(order_id: str, data: TransitionRequest, ctx=Depends(context), db: Session=Depends(get_db)):
    if not can_transition(data.from_state,data.to_state): raise HTTPException(422,"invalid state transition")
    worker_states={"reserved","reservation_failed","payment_authorized","payment_failed","refunded","fulfilled","fulfillment_failed"}
    if data.to_state in worker_states and ctx["role"] not in {"integration_worker","operator","admin"}: raise HTTPException(403,"provider/operator role required")
    if data.to_state in {"payment_pending","fulfillment_pending","refund_pending"} and ctx["role"] not in {"customer","operator","admin"}: raise HTTPException(403,"customer/operator role required")
    row=db.execute(text("""UPDATE governed_orders SET state=:to,version=version+1,updated_at=NOW() WHERE tenant_id=:tenant AND id=CAST(:id AS uuid) AND state=:from AND version=:version RETURNING *"""),{"to":data.to_state,"tenant":ctx["tenant"],"id":order_id,"from":data.from_state,"version":data.version}).mappings().first()
    if not row or not allowed(ctx,row["subject_id"]): db.rollback(); raise HTTPException(409,"missing, stale, or unauthorized order")
    db.execute(text("INSERT INTO governed_order_events(tenant_id,order_id,actor_id,event_type,details) VALUES(:tenant,CAST(:id AS uuid),:actor,:event,CAST(:details AS jsonb))"),{"tenant":ctx["tenant"],"id":order_id,"actor":ctx["actor"],"event":data.to_state,"details":json.dumps({"reason":data.reason})})
    operation={"payment_pending":("payment","authorize"),"refund_pending":("payment","refund"),"fulfillment_pending":("fulfillment","fulfill")}.get(data.to_state)
    if operation:
        provider,op=operation; key=f"{order_id}:{row['version']}:{op}"; payload={"orderId":order_id,"totals":row["totals"]}
        db.execute(text("""INSERT INTO governed_order_outbox(tenant_id,order_id,provider,operation,payload,idempotency_key,request_hash) VALUES(:tenant,CAST(:id AS uuid),:provider,:operation,CAST(:payload AS jsonb),:key,:hash) ON CONFLICT DO NOTHING"""),{"tenant":ctx["tenant"],"id":order_id,"provider":provider,"operation":op,"payload":json.dumps(payload,default=str),"key":key,"hash":digest(payload)})
    db.commit(); return dict(row)

@router.post("/workers/{provider}/claim")
def claim(provider: str, ctx=Depends(context), db: Session=Depends(get_db)):
    if provider not in PROVIDERS or ctx["role"] not in {"integration_worker","admin"}: raise HTTPException(403,"worker role and allow-listed provider required")
    token=str(uuid.uuid4()); row=db.execute(text("""WITH picked AS (SELECT id FROM governed_order_outbox WHERE tenant_id=:tenant AND provider=:provider AND status IN('pending','failed') AND next_attempt_at<=NOW() AND (lease_expires_at IS NULL OR lease_expires_at<NOW()) ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1) UPDATE governed_order_outbox o SET status='processing',lease_token=CAST(:token AS uuid),lease_expires_at=NOW()+INTERVAL '2 minutes' FROM picked WHERE o.id=picked.id RETURNING o.*"""),{"tenant":ctx["tenant"],"provider":provider,"token":token}).mappings().first();db.commit()
    if not row: return Response(status_code=204)
    return {**dict(row),"claimToken":token}

@router.post("/workers/outbox/{outbox_id}/result")
def worker_result(outbox_id: int, data: ResultRequest, claim_token: str=Header(alias="X-Claim-Token"), ctx=Depends(context), db: Session=Depends(get_db)):
    if ctx["role"] not in {"integration_worker","admin"}: raise HTTPException(403,"worker role required")
    if data.result not in {"delivered","failed"}: raise HTTPException(422,"delivered or failed result required")
    if data.result=="delivered" and (not data.receipt or not data.receipt.get("receiptRef") or not data.receipt.get("receivedAt")): raise HTTPException(422,"typed receipt required")
    if data.result=="failed" and not re.match(r"^[A-Z0-9][A-Z0-9._:-]{1,63}$",data.error_code or ""): raise HTTPException(422,"bounded error code required")
    row=db.execute(text("""UPDATE governed_order_outbox SET attempts=attempts+1,status=CASE WHEN :result='delivered' THEN 'delivered' WHEN attempts+1>=5 THEN 'dead_letter' ELSE 'failed' END,provider_receipt=CASE WHEN :result='delivered' THEN CAST(:receipt AS jsonb) ELSE provider_receipt END,delivered_at=CASE WHEN :result='delivered' THEN NOW() ELSE delivered_at END,next_attempt_at=NOW()+(LEAST(3600,POWER(2,attempts+1))::text||' seconds')::interval,lease_token=NULL,lease_expires_at=NULL WHERE id=:id AND tenant_id=:tenant AND status='processing' AND lease_token=CAST(:token AS uuid) RETURNING *"""),{"result":data.result,"receipt":json.dumps(data.receipt or {}),"id":outbox_id,"tenant":ctx["tenant"],"token":claim_token}).mappings().first();db.commit()
    if not row: raise HTTPException(409,"stale claim")
    return dict(row)
