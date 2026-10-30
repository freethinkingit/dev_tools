"""Builds the events the shop publishes.

The billing service subscribes to events whose "type" is "order.placed" and
reads "order_id" and "total_cents" from them to raise the invoice. The tracking
service subscribes to events whose "type" is "shipment.dispatched" and reads
"order_id" and "carrier" from them to show the customer where the parcel is.
"emitted_by" names the module that built the event, for people reading logs;
nothing reads it.
"""

ORDER_PLACED = "order.placed"
SHIPMENT_DISPATCHED = "shipment.dispatched"
EMITTER = "calc.events"


def order_placed_event(order_id, total_cents):
    """Returns the event billing receives when an order is placed."""
    return {
        "type": ORDER_PLACED,
        "order_id": order_id,
        "total_cents": total_cents,
        "emitted_by": EMITTER,
    }


def shipment_dispatched_event(order_id, carrier):
    """Returns the event tracking receives when an order is shipped."""
    return {
        "type": SHIPMENT_DISPATCHED,
        "order_id": order_id,
        "carrier": carrier,
        "emitted_by": EMITTER,
    }
