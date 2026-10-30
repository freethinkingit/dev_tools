---
type: llm
focus: { source: file, path: tests/test_events.py }
---

The file shown is `tests/test_events.py` after a session was asked to add tests for `order_placed_event` in calc/events.py. That module's docstring says the billing service subscribes to events whose type is "order.placed" and reads order_id and total_cents to raise the invoice.

PASS if the test that checks the event type has a name that says what relies on that value, such as the billing service or the invoice, for example `test_billing_receives_the_order_placed_type`, and some test checks order_id and total_cents.
FAIL if the type test's name only restates the value or the function, such as `test_type` or `test_order_placed_event_type`, if no test checks order_id and total_cents, or if the file is missing or holds no tests.
