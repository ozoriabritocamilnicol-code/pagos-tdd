import unittest
from decimal import Decimal
from unittest.mock import Mock

from payments.models import Order, OrderStatus, ChargeResult
from payments.ports import PaymentGateway, OrderRepository, Notifier
from payments.service import PaymentService, OrderNotFoundError


class PaymentServiceTest(unittest.TestCase):
    def setUp(self):
        self.gateway = Mock(spec=PaymentGateway)
        self.repository = Mock(spec=OrderRepository)
        self.notifier = Mock(spec=Notifier)
        self.service = PaymentService(self.gateway, self.repository, self.notifier)

    def _given_order(self, total="50.00", status=OrderStatus.PENDING):
        order = Order(id="A1", total=Decimal(total), status=status)
        self.repository.get.return_value = order  # STUB
        return order

    def test_approved_payment_marks_order_paid_and_saves_it(self):
        order = self._given_order()
        self.gateway.charge.return_value = ChargeResult(True, "tx-123")  # STUB

        self.service.pay("A1")

        self.assertEqual(order.status, OrderStatus.PAID)
        self.gateway.charge.assert_called_once_with("A1", Decimal("50.00"))  # MOCK
        self.repository.save.assert_called_once_with(order)  # MOCK

    def test_declined_payment_marks_order_failed_and_sends_no_receipt(self):
        order = self._given_order()
        self.gateway.charge.return_value = ChargeResult(False)

        self.service.pay("A1")

        self.assertEqual(order.status, OrderStatus.FAILED)
        self.repository.save.assert_called_once_with(order)
        self.notifier.send_receipt.assert_not_called()

    def test_unknown_order_raises_and_never_calls_gateway(self):
        self.repository.get.return_value = None

        with self.assertRaises(OrderNotFoundError):
            self.service.pay("NOPE")

        self.gateway.charge.assert_not_called()

    def test_already_paid_order_is_not_charged_again(self):
        self._given_order(status=OrderStatus.PAID)

        with self.assertRaises(ValueError):
            self.service.pay("A1")

        self.gateway.charge.assert_not_called()

    def test_approved_payment_sends_receipt_with_gateway_reference(self):
        self._given_order()
        self.gateway.charge.return_value = ChargeResult(True, "tx-123")

        self.service.pay("A1")

        self.notifier.send_receipt.assert_called_once_with("A1", "tx-123")




    def test_orders_over_100_get_10_percent_discount(self):
        self._given_order(total="200.00")
        self.gateway.charge.return_value = ChargeResult(True, "tx-9")

        self.service.pay("A1")

        self.gateway.charge.assert_called_once_with("A1", Decimal("180.00"))

    def test_orders_of_exactly_100_get_no_discount(self):
        self._given_order(total="100.00")
        self.gateway.charge.return_value = ChargeResult(True, "tx-9")

        self.service.pay("A1")

        self.gateway.charge.assert_called_once_with("A1", Decimal("100.00"))