from .requests import *
from .response import *
from .core import WBAsyncEngine
from .wb_endpoints_list import WBAPIFactory


class WBApi:

    def __init__(self, api_key: str):
        self._engine = WBAsyncEngine(api_key=api_key)
        self._api_factory = WBAPIFactory(self._engine)

        self._supplier_sales_api = self._api_factory.get_api(SupplierSalesResponse)
        self._promotion_adverts_api = self._api_factory.get_api(PromotionAdvertsResponse)
        self._fullstats_api = self._api_factory.get_api(FullstatsResponse)
        self._nm_report_detail_api = self._api_factory.get_api(NMReportDetailResponse)
        self._list_goods_filter_api = self._api_factory.get_api(ListGoodsFilterResponse)
        self._supplier_report_detail_by_period_api = self._api_factory.get_api(SupplierReportDetailByPeriodResponse)
        self._paid_storage_api = self._api_factory.get_api(PaidStorageResponse)
        self._paid_storage_status_api = self._api_factory.get_api(PaidStorageStatusResponse)
        self._paid_storage_download_api = self._api_factory.get_api(PaidStorageDownloadResponse)

    async def get_supplier_sales_response(self, date_from: str, flag: int = 0) -> SupplierSalesResponse:
        """
            Продажи. \n
            Дата в формате RFC3339. Можно передать дату или дату со временем. Время можно указывать с точностью до секунд или миллисекунд. \n
                Время передаётся в часовом поясе Мск (UTC+3). \n
                Примеры:
                    2019-06-20 \n
                    2019-06-20T23:59:59 \n
                    2019-06-20T00:00:00.12345 \n
                    2017-03-25T00:00:00

            Args:
                date_from (str): Начальная дата отчета.
                flag (int, option): Если параметр flag=0 (или не указан в строке запроса),
                    при вызове API возвращаются данные, у которых значение поля lastChangeDate
                    (дата время обновления информации в сервисе) больше или равно переданному значению параметра dateFrom.
                    При этом количество возвращенных строк данных варьируется в интервале от 0 до примерно 100 000.
                    Если параметр flag=1, то будет выгружена информация обо всех заказах или продажах с датой,
                    равной переданному параметру dateFrom (в данном случае время в дате значения не имеет).
                    При этом количество возвращенных строк данных будет равно количеству всех заказов или продаж,
                    сделанных в указанную дату, переданную в параметре dateFrom. Default to 0.
        """
        request = SupplierSalesRequest(dateFrom=date_from, flag=flag)
        answer: SupplierSalesResponse = await self._supplier_sales_api.get(request)

        return answer

    async def get_promotion_adverts(self, status: int, type_field: int, order: str = 'create', direction: str = 'asc') \
            -> PromotionAdvertsResponse:
        """
            Информация о рекламных кампаниях. \n
            Статус кампании:
                -1 - кампания в процессе удаления \n
                4 - готова к запуску \n
                7 - кампания завершена \n
                8 - отказался \n
                9 - идут показы \n
                11 - кампания на паузе
            Тип кампании:
                4 - кампания в каталоге \n
                5 - кампания в карточке товара \n
                6 - кампания в поиске \n
                7 - кампания в рекомендациях на главной странице \n
                8 - автоматическая кампания \n
                9 - поиск + каталог
            Порядок:
                create (по времени создания кампании) \n
                change (по времени последнего изменения кампании) \n
                id (по идентификатору кампании)
            Направление:
                desc (от большего к меньшему) \n
                asc (от меньшего к большему)

            Args:
                status (int): Статус кампании.
                type_field (int): Тип кампании.
                order (str, optional): Порядок.. Default to 'create'.
                direction (str, optional): Направление.. Default to 'asc'.

        """
        request = PromotionAdvertsRequest(status=status, type=type_field, order=order, direction=direction)
        answer: PromotionAdvertsResponse = await self._promotion_adverts_api.post(query=request)

        return answer

    async def get_fullstats(self, company_ids: list[int], dates: list[str]) -> FullstatsResponse:
        """
            Возвращает статистику кампаний. \n
            Дата в формате строки YYYY-DD-MM. \n
            Примеры:
                    "2023-10-07" \n
                    "2023-12-06"

            Args:
                company_ids (list[int]): ID кампании, не более 100.
                dates (list[str]): Даты, за которые необходимо выдать информацию.
        """
        request = []
        for company_id in company_ids:
            request.append(FullstatsRequest(id=company_id, dates=dates))
        answer: FullstatsResponse = await self._fullstats_api.post(body=request)

        return answer

    async def get_nm_report_detail(self, date_from: str, date_to: str, brand_names: list[str] = None,
                                   object_ids: list[int] = None, tag_ids: list[int] = None, nm_ids: list[int] = None,
                                   timezone: str = 'Europe/Moscow', field: str = 'openCard', mode: str = 'asc',
                                   page: int = 1) -> NMReportDetailResponse:
        """
            Получение статистики КТ за выбранный период, по nmID/предметам/брендам/тегам. \n
            Поля brand_names,object_ids, tag_ids, nm_ids могут быть пустыми, тогда в ответе идут все карточки продавца. \n
            При выборе нескольких полей в ответ приходят данные по карточкам, у которых есть все выбранные поля. Работает с пагинацией. \n
            Можно получить отчёт максимум за последний год (365 дней). \n
            Также в данных, где предоставляется информация по предыдущему периоду:
                В previousPeriod данные за такой же период, что и в selectedPeriod.
                Если дата начала previousPeriod раньше, чем год назад от текущей даты, она будет приведена к виду:
                previousPeriod.start = текущая дата - 365 дней.
            Все виды сортировки field:
                openCard — по открытию карточки (переход на страницу товара) \n
                addToCart — по добавлениям в корзину \n
                orders — по кол-ву заказов \n
                avgRubPrice — по средней цене в рублях \n
                ordersSumRub — по сумме заказов в рублях \n
                stockMpQty — по кол-ву остатков маркетплейса шт. \n
                stockWbQty — по кол-ву остатков на складе шт. \n
                cancelSumRub — сумме возвратов в рублях \n
                cancelCount — по кол-ву возвратов \n
                buyoutCount — по кол-ву выкупов \n
                buyoutSumRub — по сумме выкупов

            Args:
                date_from (str): Начало периода.
                date_to (str): Конец периода.
                brand_names (list[str], optional): Название брендов.. Default to None.
                object_ids (list[int], optional): Идентификаторы предмета.. Default to None.
                tag_ids (list[int], optional): Идентификаторы тега.. Default to None.
                nm_ids (list[int], optional): Артикулы WB.. Default to None.
                timezone (str, optional): Временная зона.. Default to 'Europe/Moscow'.
                field (str, optional): Вид сортировки.. Default to 'openCard'.
                mode (str, optional): asc — по возрастанию, desc — по убыванию.. Default to 'asc'.
                page (int, optional): Страница.. Default to 1.
        """
        request = NMReportDetailRequest(brandNames=brand_names,
                                        objectIDs=object_ids,
                                        tagIDs=tag_ids,
                                        nmIDs=nm_ids,
                                        timezone=timezone,
                                        period=NMReportDetailPeriodRequest(begin=date_from,
                                                                           end=date_to),
                                        orderBy=NMReportDetailOrderByRequest(field=field,
                                                                             mode=mode),
                                        page=page)
        answer: NMReportDetailResponse = await self._nm_report_detail_api.post(body=request)

        return answer

    async def get_list_goods_filter(self, limit: int = 10, offset: int = 0, filter_nm_id: int = None) \
            -> ListGoodsFilterResponse:
        """
            Возвращает информацию о товаре по его артикулу. Чтобы получить информацию обо всех товарах, оставьте артикул пустым.

            Args:
                limit (int, optional): Сколько элементов вывести на одной странице (пагинация). Максимум 1 000 элементов. Default to 10.
                offset (int, optional): Сколько элементов пропустить.. Default to 0.
                filter_nm_id (int, optional): Артикул Wildberries, по которому искать товар.. Default to None.
        """
        request = ListGoodsFilterRequest(limit=limit, offset=offset, filterNmID=filter_nm_id)
        answer: ListGoodsFilterResponse = await self._list_goods_filter_api.get(request)

        return answer

    async def get_supplier_report_detail_by_period(self, date_from: str, date_to: str, limit: int = 100000,
                                                   rrdid: int = 0) -> SupplierReportDetailByPeriodResponse:
        request = SupplierReportDetailByPeriodRequest(dateFrom=date_from,
                                                      limit=limit,
                                                      dateTo=date_to,
                                                      rrdid=rrdid)
        answer: SupplierReportDetailByPeriodResponse = await self._supplier_report_detail_by_period_api.get(request)

        return answer

    async def get_paid_storage(self, date_from: str, date_to: str) -> PaidStorageResponse:
        request = PaidStorageRequest(dateFrom=date_from,
                                     dateTo=date_to)
        answer: PaidStorageResponse = await self._paid_storage_api.get(request)

        return answer

    async def get_paid_storage_status(self, task_id: str) -> PaidStorageStatusResponse:
        request = PaidStorageStatusRequest()
        answer: PaidStorageStatusResponse = await self._paid_storage_status_api.get(request,
                                                                                    format_dict={'task_id': task_id})

        return answer

    async def get_paid_storage_download(self, task_id: str) -> PaidStorageDownloadResponse:
        request = PaidStorageDownloadRequest()
        answer: PaidStorageDownloadResponse = await self._paid_storage_download_api.get(request,
                                                                                        format_dict={'task_id': task_id})

        return answer
