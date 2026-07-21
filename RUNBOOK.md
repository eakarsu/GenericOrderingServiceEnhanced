# Governed ordering runbook

The `/api/governed-orders` API is authoritative. The prior generic CRUD, payment stub, demo seed, and generated views are disabled by default and forbidden in production. Signed tokens identify actor, tenant, role, and permitted order subjects. Customers see their subjects; operators and merchants act only in authorized tenant scope; administrators have audited tenant scope.

Run `./start.sh check`, back up PostgreSQL, then run `ALLOW_SCHEMA_MIGRATION=1 ./start.sh migrate`. The migration is additive and preserves legacy data. Run `python3 -m unittest backend.tests.test_governance` and start with `./start.sh start`. Startup never creates schema, seeds, installs packages, exposes credentials, or kills unrelated processes. For rollback, deploy the prior application while retaining additive tables; restore the backup only after reconciling accepted orders.

Inventory, tax, payment, shipping, fulfillment, notification, and webhook providers are allow-listed. Each command is payload-bound to an idempotency key. Workers use `FOR UPDATE SKIP LOCKED` and a claim token, store typed non-secret receipts, retry with backoff, and move the fifth failure to the dead-letter queue. Reconcile provider state before replay, especially reservation release, payment authorization/refund, and partial fulfillment.

Immutable events record every state decision and operator reason. Retention and legal holds apply to orders and receipts. On duplicate charges, inventory divergence, fulfillment failure, tenant leakage, or receipt mismatch, stop the affected provider worker, revoke credentials if needed, preserve events, notify tenant owners, and recover from the last verified receipt.
