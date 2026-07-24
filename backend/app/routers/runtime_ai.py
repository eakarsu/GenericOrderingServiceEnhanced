import json
import os
import urllib.error
import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..auth_utils import get_current_user
from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api/runtime-ai", tags=["Runtime AI"])


@router.post("/ordering-advice")
def ordering_advice(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload:
        raise HTTPException(status_code=400, detail="ordering_context_required")
    base = os.getenv("OPENROUTER_BASE_URL", "")
    key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("OPENROUTER_MODEL", "")
    if base != "https://openrouter.ai/api/v1" or not key or not model:
        raise HTTPException(status_code=503, detail="OpenRouter runtime configuration is incomplete")
    request_body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "Give concise ordering, inventory, payment, and fulfillment advice with clear operational checks."},
            {"role": "user", "content": json.dumps(payload, separators=(",", ":"))},
        ],
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/chat/completions", data=request_body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            provider_body = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as error:
        raise HTTPException(status_code=502, detail="provider_request_failed") from error
    result = ((provider_body.get("choices") or [{}])[0].get("message") or {}).get("content")
    if not result:
        raise HTTPException(status_code=502, detail="provider_returned_no_content")
    provider_model = provider_body.get("model") or model
    saved = db.execute(text(
        """INSERT INTO ordering_runtime_ai_results(user_id,input,result,model)
           VALUES(:user_id,CAST(:input AS JSONB),CAST(:result AS JSONB),:model)
           RETURNING id,created_at"""
    ), {"user_id": current_user.id, "input": json.dumps(payload), "result": json.dumps({"text": result}), "model": provider_model}).mappings().one()
    db.commit()
    return {"success": True, "result": result, "model": provider_model,
            "persisted": {"id": str(saved["id"]), "created_at": saved["created_at"].isoformat()}}
