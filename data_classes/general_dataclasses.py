import datetime

from typing import Optional
from dataclasses import dataclass


@dataclass
class DataOperation:
    client_id: str
    accrual_date: datetime.date
    type_of_transaction: str
    vendor_code: str
    delivery_schema: str
    posting_number: str
    sku: str
    sale: float
    quantities: int
    commission: Optional[float] = None
    bonus: Optional[float] = None


@dataclass
class DataCostPrice:
    month_date: int
    year_date: int
    vendor_code: str
    cost: float


@dataclass
class DataSelfPurchase:
    client_id: str
    order_date: datetime.date
    accrual_date: datetime.date
    vendor_code: str
    quantities: int
    price: float


@dataclass
class DataOrder:
    client: "Client"
    vendor_code: str
    orders_count: float


@dataclass
class DataRate:
    date: datetime.date
    currency: str
    rate: float


@dataclass
class DataOverseasPurchase:
    accrual_date: datetime.date
    vendor_code: str
    quantities: int
    price: float
    log_cost: float
    log_add_cost: float
