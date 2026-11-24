from .models import OrderStatus


class OrderNotFoundError(Exception):
    pass


class PaymentService:
    def __init__(self, gateway, repository, notifier):
        self._gateway = gateway
        self._repository = repository
        self._notifier = notifier

    def pay(self, order_id):
        order = self._repository.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        result = self._gateway.charge(order.id, order.total)
        order.status = OrderStatus.PAID if result.approved else OrderStatus.FAILED
        self._repository.save(order)
        