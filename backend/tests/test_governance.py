import pathlib, unittest
from backend.app.order_domain import evaluate_order, can_transition

ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE={"customer_actor_id":"customer-1","merchant_id":"merchant-1","inventory_snapshot_version":"v2","tax_quote_ref":"tax:q1","items":[{"item_id":"sku-1","quantity":2,"unit_price":5,"available":True,"stock_available":3}],"tax":1,"shipping":2,"discount":1,"total":12}

class GovernanceTests(unittest.TestCase):
    def test_deterministic_pricing(self): self.assertEqual(evaluate_order(BASE,"customer-1"),evaluate_order(BASE,"customer-1"))
    def test_calculated_total(self): self.assertEqual(evaluate_order(BASE,"customer-1")["result"]["total_cents"],1200)
    def test_ownership_fails_closed(self): self.assertTrue(evaluate_order(BASE,"other")["errors"])
    def test_inventory_fails_closed(self): self.assertTrue(evaluate_order({**BASE,"items":[{**BASE["items"][0],"stock_available":0}]},"customer-1")["errors"])
    def test_total_divergence_fails(self): self.assertTrue(evaluate_order({**BASE,"total":1},"customer-1")["errors"])
    def test_valid_transition(self): self.assertTrue(can_transition("reserved","payment_pending"))
    def test_shortcut_denied(self): self.assertFalse(can_transition("reservation_pending","fulfilled"))
    def test_migration_tenant_scope(self): self.assertIn("PRIMARY KEY(tenant_id,id)",(ROOT/"backend/migrations/001_governed_order_lifecycle.sql").read_text())
    def test_migration_immutable_audit(self): self.assertIn("append_only",(ROOT/"backend/migrations/001_governed_order_lifecycle.sql").read_text())
    def test_outbox_has_leases_receipts(self):
        sql=(ROOT/"backend/migrations/001_governed_order_lifecycle.sql").read_text();self.assertIn("lease_expires_at",sql);self.assertIn("provider_receipt",sql)
    def test_router_has_idempotency_and_skip_locked(self):
        source=(ROOT/"backend/app/routers/governed_orders.py").read_text();self.assertIn("Idempotency-Key",source);self.assertIn("SKIP LOCKED",source);self.assertIn("dead_letter",source)
    def test_startup_is_non_destructive(self):
        main=(ROOT/"backend/app/main.py").read_text();launch=(ROOT/"start.sh").read_text();self.assertNotIn("create_all",main);self.assertNotIn("seed_database",main);self.assertNotIn("pip install",launch);self.assertIn("ALLOW_SCHEMA_MIGRATION",launch)

if __name__ == "__main__": unittest.main()
