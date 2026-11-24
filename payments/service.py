from decimal import Decimal

from .models import OrderStatus

DISCOUNT_THRESHOLD = Decimal("100.00")
DISCOUNT_RATE = Decimal("0.10")


class OrderNotFoundError(Exception):
    pass


class PaymentService:
    def __init__(self, gateway, repository, notifier):
        self._gateway = gateway
        self._repository = repository
        self._notifier = notifier

    def pay(self, order_id):
        order = self._load_payable_order(order_id)
        amount = self._amount_to_charge(order)
        result = self._gateway.charge(order.id, amount)
        if result.approved:
            order.status = OrderStatus.PAID
            self._repository.save(order)
            self._notifier.send_receipt(order.id, result.reference)
        else:
            order.status = OrderStatus.FAILED
            self._repository.save(order)

    def _load_payable_order(self, order_id):
        order = self._repository.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        if order.status is OrderStatus.PAID:
            raise ValueError("La orden ya fue pagada")
        return order

    def _amount_to_charge(self, order):
        if order.total > DISCOUNT_THRESHOLD:
            return (order.total * (1 - DISCOUNT_RATE)).quantize(Decimal("0.01"))
        return order.total