BEGIN;
CREATE TABLE IF NOT EXISTS governed_orders (
  tenant_id TEXT NOT NULL, id UUID NOT NULL, subject_id TEXT NOT NULL, customer_actor_id TEXT NOT NULL,
  merchant_id TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN('reservation_pending','reserved','reservation_failed','payment_pending','payment_authorized','payment_failed','cancelled','refund_pending','refunded','fulfillment_pending','fulfilled','fulfillment_failed')),
  request JSONB NOT NULL, totals JSONB NOT NULL, idempotency_key TEXT NOT NULL, request_hash CHAR(64) NOT NULL,
  version INTEGER NOT NULL DEFAULT 1, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY(tenant_id,id), UNIQUE(tenant_id,idempotency_key)
);
CREATE TABLE IF NOT EXISTS governed_order_events (
  id BIGSERIAL PRIMARY KEY, tenant_id TEXT NOT NULL, order_id UUID NOT NULL, actor_id TEXT NOT NULL,
  event_type TEXT NOT NULL, details JSONB NOT NULL DEFAULT '{}', created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY(tenant_id,order_id) REFERENCES governed_orders(tenant_id,id)
);
CREATE TABLE IF NOT EXISTS governed_order_outbox (
  id BIGSERIAL PRIMARY KEY, tenant_id TEXT NOT NULL, order_id UUID NOT NULL, provider TEXT NOT NULL,
  operation TEXT NOT NULL, payload JSONB NOT NULL, idempotency_key TEXT NOT NULL, request_hash CHAR(64) NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN('pending','processing','failed','delivered','dead_letter')),
  attempts INTEGER NOT NULL DEFAULT 0, next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), lease_token UUID,
  lease_expires_at TIMESTAMPTZ, provider_receipt JSONB, delivered_at TIMESTAMPTZ,
  FOREIGN KEY(tenant_id,order_id) REFERENCES governed_orders(tenant_id,id), UNIQUE(tenant_id,provider,idempotency_key)
);
CREATE OR REPLACE FUNCTION governed_order_events_append_only() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'governed order events are append-only'; END $$;
DROP TRIGGER IF EXISTS governed_order_events_append_only ON governed_order_events;
CREATE TRIGGER governed_order_events_append_only BEFORE UPDATE OR DELETE ON governed_order_events FOR EACH ROW EXECUTE FUNCTION governed_order_events_append_only();
CREATE INDEX IF NOT EXISTS governed_order_outbox_claim_idx ON governed_order_outbox(status,next_attempt_at,lease_expires_at);
COMMIT;
