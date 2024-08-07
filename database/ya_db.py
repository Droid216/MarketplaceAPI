import logging

from .db import DbConnection
from data_classes import DataOperation, DataYaCampaigns, DataYaReport
from .models import Client, YaMain, YaCampaigns, YaReport

logger = logging.getLogger(__name__)


class YaDbConnection(DbConnection):

    def add_ya_campaigns(self, list_campaigns: list[DataYaCampaigns]) -> None:
        for campaign in list_campaigns:
            existing_client = self.session.query(Client).filter_by(client_id=campaign.client_id).first()
            if existing_client:
                new_campaign = YaCampaigns(campaign_id=campaign.campaign_id,
                                           client_id=campaign.client_id,
                                           name=campaign.name,
                                           placement_type=campaign.placement_type)
                self.session.merge(new_campaign)
        try:
            self.session.commit()
            logger.info(f"Успешное добавление в базу")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка добавления: {e}")

    def add_ya_operation(self, client_id: str, list_operations: list[DataOperation]) -> None:
        """
            Добавление в базу данных записи об операциях с товарами.

            Args:
                client_id (str): ID кабинета.
                list_operations (list[DataOperation]): Список данных об операциях.
        """
        existing_client = self.session.query(Client).filter_by(client_id=client_id).first()
        if existing_client:
            for operation in list_operations:
                existing_operation = self.session.query(YaMain).filter_by(client_id=client_id,
                                                                          type_of_transaction=operation.type_of_transaction,
                                                                          posting_number=operation.posting_number,
                                                                          sku=operation.sku).first()
                if not existing_operation:
                    new_operation = YaMain(client_id=operation.client_id,
                                           accrual_date=operation.accrual_date,
                                           type_of_transaction=operation.type_of_transaction,
                                           vendor_code=operation.vendor_code,
                                           posting_number=operation.posting_number,
                                           delivery_schema=operation.delivery_schema,
                                           sku=operation.sku,
                                           sale=operation.sale,
                                           quantities=operation.quantities)
                    self.session.add(new_operation)
            try:
                self.session.commit()
                logger.info(f"Успешное добавление в базу")
            except Exception as e:
                self.session.rollback()
                logger.error(f"Ошибка добавления: {e}")

    def add_ya_report(self, client_id: str, list_reports: list[DataYaReport]) -> None:
        """
            Добавление в базу данных записи об операциях с товарами.

            Args:
                client_id (str): ID кабинета.
                list_reports (list[DataYaReport]): Список данных об операциях.
        """
        existing_client = self.session.query(Client).filter_by(client_id=client_id).first()
        if existing_client:
            for operation in list_reports:
                row = self.session.query(YaReport).filter_by(campaign_id=operation.campaign_id).first()
                if row:
                    new_operation = YaReport(client_id=row.client_id,
                                             campaign_id=operation.campaign_id,
                                             posting_number=operation.posting_number,
                                             application_number=operation.application_number,
                                             vendor_code=operation.vendor_code,
                                             service=operation.service,
                                             accrual_date=operation.accrual_date,
                                             cost=operation.cost)
                    self.session.add(new_operation)
            try:
                self.session.commit()
                logger.info(f"Успешное добавление в базу")
            except Exception as e:
                self.session.rollback()
                logger.error(f"Ошибка добавления: {e}")
