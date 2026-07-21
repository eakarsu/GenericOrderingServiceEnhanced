"""Pure deterministic order validation and lifecycle policy."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

TRANSITIONS = {
    "reservation_pending": {"reserved", "reservation_failed", "cancelled"},
    "reservation_failed": {"reservation_pending", "cancelled"},
    "reserved": {"payment_pending", "cancelled"},
    "payment_pending": {"payment_authorized", "payment_failed", "cancelled"},
    "payment_failed": {"payment_pending", "cancelled"},
    "payment_authorized": {"fulfillment_pending", "refund_pending"},
    "fulfillment_pending": {"fulfilled", "fulfillment_failed", "refund_pending"},
    "fulfillment_failed": {"fulfillment_pending", "refund_pending"},
    "cancelled": set(), "refund_pending": {"refunded"}, "refunded": set(), "fulfilled": set(),
}

def cents(value):
    try:
        return int((Decimal(str(value)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, TypeError):
        return None

def evaluate_order(data, actor):
    errors = []
    if str(data.get("customer_actor_id", "")) != str(actor): errors.append("customer_actor_id must match signed actor")
    if not str(data.get("merchant_id", "")).strip(): errors.append("merchant_id required")
    if not str(data.get("inventory_snapshot_version", "")).strip(): errors.append("inventory_snapshot_version required")
    if not str(data.get("tax_quote_ref", "")).strip(): errors.append("tax_quote_ref required")
    items = data.get("items") if isinstance(data.get("items"), list) else []
    if not items: errors.append("at least one item required")
    subtotal = 0
    normalized = []
    for index, item in enumerate(items):
        price, quantity = cents(item.get("unit_price")), item.get("quantity")
        if not item.get("item_id") or not isinstance(quantity, int) or quantity < 1 or price is None or price < 0:
            errors.append(f"items[{index}] invalid")
        if item.get("available") is not True or not isinstance(item.get("stock_available"), int) or item.get("stock_available", 0) < (quantity or 0):
            errors.append(f"items[{index}] unavailable")
        if price is not None and isinstance(quantity, int): subtotal += price * quantity
        normalized.append({"item_id": str(item.get("item_id", "")), "quantity": quantity, "unit_price_cents": price})
    tax, shipping, discount, declared = [cents(data.get(key, 0)) for key in ("tax", "shipping", "discount", "total")]
    if any(value is None for value in (tax, shipping, discount, declared)): errors.append("money values invalid")
    total = subtotal + (tax or 0) + (shipping or 0) - (discount or 0)
    if declared != total: errors.append("server-calculated total differs from declared total")
    return {"errors": errors, "result": {"items": normalized, "subtotal_cents": subtotal, "tax_cents": tax,
        "shipping_cents": shipping, "discount_cents": discount, "total_cents": total,
        "initial_state": "reservation_pending", "human_override_requires_reason": True}}

def can_transition(old, new):
    return new in TRANSITIONS.get(old, set())
