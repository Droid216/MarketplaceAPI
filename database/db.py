import time
import logging

from typing import Type
from functools import wraps

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from pyodbc import Error as PyodbcError
from sqlalchemy.exc import OperationalError
from sqlalchemy.dialects.postgresql import insert

from config import *
from data_classes import *
from database.models import *

logger = logging.getLogger(__name__)


def retry_on_exception(retries=3, delay=10):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except (OperationalError, PyodbcError) as e:
                    attempt += 1
                    logger.debug(f"Error occurred: {e}. Retrying {attempt}/{retries} after {delay} seconds...")
                    time.sleep(delay)
                    if hasattr(self, 'session'):
                        self.session.rollback()
                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}. Rolling back...")
                    if hasattr(self, 'session'):
                        self.session.rollback()
                    raise e
            raise RuntimeError("Max retries exceeded. Operation failed.")
        return wrapper
    return decorator


class DbConnection:
    def __init__(self, echo: bool = False) -> None:
        self.engine = create_engine(url=DB_URL, echo=echo, pool_pre_ping=True)
        self.session = Session(self.engine)

    @retry_on_exception()
    def start_db(self) -> None:
        """Создание таблиц."""
        metadata.create_all(self.session.bind, checkfirst=True)

    @retry_on_exception()
    def get_client(self, client_id: str) -> Type[Client]:
        """
            Возвращает данные кабинета, отфильтрованный по ID кабинета.

            Args:
                client_id (str): ID кабинета для фильтрации.

            Returns:
                Type[Client]: данные кабинета, удовлетворяющих условию фильтрации.
        """
        client = self.session.query(Client).filter_by(client_id=client_id).first()
        return client

    @retry_on_exception()
    def get_clients(self, marketplace: str = None) -> list[Type[Client]]:
        """
            Возвращает список данных кабинета, отфильтрованный по заданному рынку.

            Args:
                marketplace (str): Рынок для фильтрации.

            Returns:
                List[Type[Client]]: Список данных кабинета, удовлетворяющих условию фильтрации.
        """
        if marketplace:
            result = self.session.query(Client).filter_by(marketplace=marketplace).all()
        else:
            result = self.session.query(Client).all()
        return result

    @retry_on_exception()
    def add_cost_price(self, list_cost_price: list[DataCostPrice]) -> None:
        """
            Добавляет себестоймость товаров в БД.

            Args:
                list_cost_price (list[DataCostPrice]): список данных по себестоймости.
        """
        for row in list_cost_price:
            stmt = insert(CostPrice).values(
                month_date=row.month_date,
                year_date=row.year_date,
                vendor_code=row.vendor_code,
                cost=row.cost
            ).on_conflict_do_update(
                index_elements=['month_date', 'year_date', 'vendor_code'],
                set_={'cost': row.cost}
            )
            self.session.execute(stmt)
        self.session.commit()
        logger.info(f"Успешное добавление в базу")

    @retry_on_exception()
    def add_self_purchase(self, list_self_purchase: list[DataSelfPurchase]) -> None:
        for row in list_self_purchase:
            stmt = insert(SelfPurchase).values(
                client_id=row.client_id,
                order_date=row.order_date,
                accrual_date=row.accrual_date,
                vendor_code=row.vendor_code,
                quantities=row.quantities,
                price=row.price
            ).on_conflict_do_update(
                index_elements=['client_id', 'order_date', 'accrual_date', 'vendor_code', 'price'],
                set_={'quantities': row.quantities}
            )
            self.session.execute(stmt)
        self.session.commit()
        logger.info(f"Успешное добавление в базу")
