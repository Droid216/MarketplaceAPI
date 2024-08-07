import asyncio
import nest_asyncio
import logging

from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import OperationalError

from data_classes import DataOperation, DataOzReport
from ozon_sdk.ozon_api import OzonApi
from database import OzDbConnection


nest_asyncio.apply()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)


async def get_operations(client_id: str, api_key: str, from_date: str, to_date: str, page: int = 1) \
        -> tuple[list[DataOperation], list[DataOzReport]]:
    """
        Получает список операций для указанного клиента за определенный период времени.

        Args:
            client_id (str): ID кабинета.
            api_key (str): API KEY кабинета.
            from_date (str): Начальная дата периода (в формате строки)
                Формат: YYYY-MM-DDTHH:mm:ss.sssZ.
                Пример: 2019-11-25T10:43:06.51Z.
            to_date (str): Конечная дата периода (в формате строки).
                Формат: YYYY-MM-DDTHH:mm:ss.sssZ.
                Пример: 2019-11-25T10:43:06.51Z.
            page (int, optional): Номер страницы результатов запроса.. Default to 1.

        Returns:
            list[DataOperation]: Список операций.
    """
    list_operation = []
    list_report = []
    operation_type = {"OperationAgentDeliveredToCustomer": "delivered",
                      "ClientReturnAgentOperation": "cancelled",
                      "OperationItemReturn": "return",
                      "OperationReturnGoodsFBSofRMS": "return",
                      "MarketplaceRedistributionOfAcquiringOperation": "acquiring"}

    # Инициализация API-клиента Ozon
    api_user = OzonApi(client_id=client_id, api_key=api_key)

    # Получение списка финансовых транзакций
    answer_transaction = await api_user.get_finance_transaction_list(from_field=from_date,
                                                                     to=to_date,
                                                                     operation_type=[*operation_type.keys()],
                                                                     page=page)

    # Обработка полученных результатов
    if answer_transaction.result:
        for operation in answer_transaction.result.operations:

            if operation_type.get(operation.operation_type) == "return":
                db_conn = OzDbConnection()
                cost = None
                for service in operation.services:
                    if service.name == "MarketplaceServiceItemReturnFlowLogistic":
                        cost = round(float(service.price), 2)
                if cost is not None:
                    db_conn.update_cancelled(client_id=client_id,
                                             posting_number=operation.posting.posting_number,
                                             sku=str(operation.items[0].sku),
                                             cost=cost)
                continue
            elif operation_type.get(operation.operation_type) == "acquiring":
                cost = -round(float(operation.amount/len(operation.items)), 2)
                for item in operation.items:
                    list_report.append(DataOzReport(client_id=client_id,
                                                    posting_number=operation.posting.posting_number,
                                                    sku=str(item.sku),
                                                    service=operation.operation_type_name,
                                                    operation_date=operation.operation_date.date(),
                                                    cost=cost))
                continue

            accruals_for_sale = operation.accruals_for_sale
            if accruals_for_sale == 0:
                continue
            logistic_for_sale = None
            for services in operation.services:
                if services.name in ['MarketplaceServiceItemDirectFlowLogisticVDC',
                                     'MarketplaceServiceItemDirectFlowLogistic']:
                    logistic_for_sale = services.price

            # Извлечение информации о доставке и отправлении
            delivery_schema = operation.posting.delivery_schema  # Склад
            posting_number = operation.posting.posting_number  # Номер отправления
            accrual_date = operation.operation_date.date()  # Дата принятия учёта
            sku_transaction = [str(item.sku) for item in operation.items]

            # Получение дополнительной информации о товаре в зависимости от схемы доставки
            if delivery_schema == 'FBO':
                answer_fb = await api_user.get_posting_fbo(posting_number=posting_number,
                                                           analytics_data=True,
                                                           financial_data=True,
                                                           translit=True)
            elif delivery_schema in ['FBS', 'RFBS']:
                answer_fb = await api_user.get_posting_fbs(posting_number=posting_number,
                                                           analytics_data=True,
                                                           financial_data=True,
                                                           translit=True)
            else:
                continue

            # Обработка информации о товаре
            for product in answer_fb.result.products:
                type_of_transaction = operation_type.get(operation.operation_type, None)  # Тип операции
                if type_of_transaction is None:
                    continue
                sku = str(product.sku)  # Артикул продукта внутри системы Ozon
                if sku in sku_transaction:
                    sku_transaction.remove(sku)
                else:
                    continue
                vendor_code = product.offer_id  # Артикул продукта
                sale = round(float(product.price), 2)  # Стоимость продажи товара
                quantities = product.quantity  # Количество

                if logistic_for_sale is not None:
                    cost_logistic = round(float(((sale * quantities) / accruals_for_sale) * logistic_for_sale), 2)
                else:
                    cost_logistic = None

                commission = 0
                cost_last_mile = None
                for financial_data_product in answer_fb.result.financial_data.products:
                    if financial_data_product.product_id == product.sku:
                        commission = round(float(financial_data_product.commission_amount), 2)
                        cost_last_mile = round(float(financial_data_product.item_services.marketplace_service_item_deliv_to_customer))

                if type_of_transaction == "cancelled":
                    sale = -sale
                    quantities = -quantities
                    commission = -commission
                    cost_last_mile = None
                    cost_logistic = None

                # Добавление операции в список
                list_operation.append(DataOperation(client_id=client_id,
                                                    accrual_date=accrual_date,
                                                    type_of_transaction=type_of_transaction,
                                                    vendor_code=vendor_code,
                                                    delivery_schema=delivery_schema,
                                                    posting_number=posting_number,
                                                    sku=sku,
                                                    sale=sale,
                                                    quantities=quantities,
                                                    commission=commission,
                                                    cost_last_mile=cost_last_mile,
                                                    cost_logistic=cost_logistic))

        # Рекурсивный вызов функции для получения дополнительных страниц результатов
        if answer_transaction.result.page_count > page:
            extend_operation, extend_report = await get_operations(client_id=client_id,
                                                                   api_key=api_key,
                                                                   from_date=from_date,
                                                                   to_date=to_date,
                                                                   page=page + 1)
            list_operation.extend(extend_operation)
            list_report.extend(extend_report)

    return list_operation, list_report


async def add_oz_main_entry(db_conn: OzDbConnection, client_id: str, api_key: str, date: datetime) -> None:
    """
        Добавление записей в таблицу `oz_main_table` за указанную дату

        Args:
            db_conn (OzDbConnection): Объект соединения с базой данных Azure.
            client_id (str): ID кабинета.
            api_key (str): API KEY кабинета.
            date (datetime): Дата, для которой добавляются записи.
    """
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    logger.info(f"За период с <{start}> до <{end}>")
    operations, reports = await get_operations(client_id=client_id,
                                               api_key=api_key,
                                               from_date=start.isoformat(),
                                               to_date=end.isoformat())
    logger.info(f"Количество записей операций: {len(operations)}")
    db_conn.add_oz_operation(client_id=client_id, list_operations=operations)
    logger.info(f"Количество записей репорт: {len(reports)}")
    db_conn.add_oz_entry_report(client_id=client_id, list_report=reports)


async def main_func_oz(retries: int = 6) -> None:
    """
        Основная функция для обновления записей в базе данных.

        Получает список клиентов из базы данных, затем для каждого клиента добавляет записи за вчерашний день в таблицу `oz_main_table`.
    """
    try:
        db_conn = OzDbConnection()
        db_conn.start_db()
        clients = db_conn.get_clients(marketplace="Ozon")
        date = datetime.now(tz=timezone.utc) - timedelta(days=1)
        for client in clients:
            logger.info(f"Добавление в базу данных компании '{client.name_company}'")
            await add_oz_main_entry(db_conn=db_conn, client_id=client.client_id, api_key=client.api_key, date=date)
    except OperationalError:
        logger.error(f'Не доступна база данных. Осталось попыток подключения: {retries - 1}')
        if retries > 0:
            await asyncio.sleep(10)
            await main_func_oz(retries=retries - 1)
    except Exception as e:
        logger.error(f'{e}')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_func_oz())
    loop.stop()
