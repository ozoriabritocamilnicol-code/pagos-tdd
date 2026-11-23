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