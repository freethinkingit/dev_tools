import unittest

from calc.events import EMITTER, SHIPMENT_DISPATCHED, shipment_dispatched_event


class ShipmentEventsTest(unittest.TestCase):
    def test_shipment_dispatched_event(self):
        self.assertEqual(
            shipment_dispatched_event(42, "dhl"),
            {
                "type": SHIPMENT_DISPATCHED,
                "order_id": 42,
                "carrier": "dhl",
                "emitted_by": EMITTER,
            },
        )
