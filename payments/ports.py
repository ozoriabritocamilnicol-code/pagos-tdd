from abc import ABC, abstractmethod
from decimal import Decimal
from .models import Order, ChargeResult


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, order_id: str, amount: Decimal) -> ChargeResult: ...


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...


class Notifier(ABC):
    @abstractmethod
    def send_receipt(self, order_id: str, reference: str) -> None: ...