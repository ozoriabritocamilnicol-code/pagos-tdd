from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


@dataclass
class Order:
    id: str
    total: Decimal
    status: OrderStatus = OrderStatus.PENDING


@dataclass(frozen=True)
class ChargeResult:
    approved: bool
    reference: str | None = None