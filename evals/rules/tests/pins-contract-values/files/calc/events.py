"""Builds the events the shop publishes.

The billing service subscribes to events whose "type" is "order.placed" and
reads "order_id" and "total_cents" from them to raise the invoice. "emitted_by"
names the module that built the event, for people reading logs; nothing reads it.
"""

ORDER_PLACED = "order.placed"
EMITTER = "calc.events"


def order_placed_event(order_id, total_cents):
    """Returns the event billing receives when an order is placed."""
    return {
        "type": ORDER_PLACED,
        "order_id": order_id,
        "total_cents": total_cents,
        "emitted_by": EMITTER,
    }
