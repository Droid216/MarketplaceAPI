from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Identity, Unicode
from sqlalchemy.orm import relationship

from .general_models import Base


class WBMain(Base):
    """Модель таблицы wb_main_table."""
    __tablename__ = 'wb_main_table'

    id = Column(Integer, Identity(), primary_key=True)
    accrual_date = Column(Date, nullable=False)
    client_id = Column(String(length=255), ForeignKey('clients.client_id'), nullable=False)
    type_of_transaction = Column(String, nullable=False)
    vendor_code = Column(Unicode, nullable=False)
    posting_number = Column(String, nullable=False)
    delivery_schema = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    sale = Column(Numeric(precision=12, scale=2), nullable=False)
    quantities = Column(Integer, nullable=False)
    commission = Column(Numeric(precision=12, scale=2), default=None, nullable=True)

    client = relationship("Client", back_populates="operations_wb")


class WBCardProduct(Base):
    """Модель таблицы wb_card_product."""
    __tablename__ = 'wb_card_product'

    sku = Column(String(length=255), primary_key=True, nullable=False)
    vendor_code = Column(Unicode, nullable=False)
    client_id = Column(String(length=255), ForeignKey('clients.client_id'), nullable=False)
    category = Column(Unicode, default=None, nullable=True)
    brand = Column(Unicode, default=None, nullable=True)
    link = Column(Unicode, default=None, nullable=True)
    price = Column(Numeric(precision=12, scale=2), default=None, nullable=True)
    discount_price = Column(Numeric(precision=12, scale=2), default=None, nullable=True)

    client = relationship("Client", back_populates="card_product_wb")
    statistic_card_product = relationship("WBStatisticCardProduct", back_populates="card_product")
    statistic_advert = relationship("WBStatisticAdvert", back_populates="card_product")


class WBStatisticCardProduct(Base):
    """Модель таблицы wb_statistic_card_product."""
    __tablename__ = 'wb_statistic_card_product'

    id = Column(Integer, Identity(), primary_key=True)
    sku = Column(String(length=255), ForeignKey('wb_card_product.sku'), nullable=False)
    date = Column(Date, nullable=False)
    open_card_count = Column(Integer, nullable=False)
    add_to_cart_count = Column(Integer, nullable=False)
    orders_count = Column(Integer, nullable=False)
    add_to_cart_percent = Column(Numeric(precision=12, scale=2), nullable=False)
    cart_to_order_percent = Column(Numeric(precision=12, scale=2), nullable=False)
    price = Column(Numeric(precision=12, scale=2), default=None, nullable=True)
    discount_price = Column(Numeric(precision=12, scale=2), default=None, nullable=True)
    buyouts_last_30days_percent = Column(Numeric(precision=12, scale=2), default=None, nullable=True)

    card_product = relationship("WBCardProduct", back_populates="statistic_card_product")


class WBStatisticAdvert(Base):
    """Модель таблицы wb_statistic_advert."""
    __tablename__ = 'wb_statistic_advert'

    id = Column(Integer, Identity(), primary_key=True)
    sku = Column(String(length=255), ForeignKey('wb_card_product.sku'), nullable=False)
    advert_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    views = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    ctr = Column(Numeric(precision=12, scale=2), nullable=False)
    cpc = Column(Numeric(precision=12, scale=2), nullable=False)
    atbs = Column(Integer, nullable=False)
    orders_count = Column(Integer, nullable=False)
    shks = Column(Integer, nullable=False)
    sum_price = Column(Numeric(precision=12, scale=2), nullable=False)
    sum_cost = Column(Numeric(precision=12, scale=2), nullable=False)
    appType = Column(Unicode, default=None, nullable=True)

    card_product = relationship("WBCardProduct", back_populates="statistic_advert")


class WBTypeAdvert(Base):
    """Модель таблицы wb_type_advert."""
    __tablename__ = 'wb_type_advert'

    id_type = Column(Integer, primary_key=True)
    type = Column(Unicode, default=None, nullable=True)

    advert_type_id = relationship("WBAdverts", back_populates="advert_type")


class WBStatusAdvert(Base):
    """Модель таблицы wb_status_advert."""
    __tablename__ = 'wb_status_advert'

    id_status = Column(Integer, primary_key=True)
    status = Column(Unicode, default=None, nullable=True)

    advert_status_id = relationship("WBAdverts", back_populates="advert_status")


class WBAdverts(Base):
    """Модель таблицы wb_adverts_table."""
    __tablename__ = 'wb_adverts_table'

    id_advert = Column(Integer, primary_key=True)
    client_id = Column(String(length=255), ForeignKey('clients.client_id'), nullable=False)
    id_type = Column(Integer, ForeignKey('wb_type_advert.id_type'), nullable=False)
    id_status = Column(Integer, ForeignKey('wb_status_advert.id_status'), nullable=False)
    name_advert = Column(Unicode, default=None, nullable=True)
    create_time = Column(Date)
    change_time = Column(Date)
    start_time = Column(Date)
    end_time = Column(Date)

    advert_type = relationship("WBTypeAdvert", back_populates="advert_type_id")
    advert_status = relationship("WBStatusAdvert", back_populates="advert_status_id")
    client = relationship("Client", back_populates="adverts_wb")


class WBReport(Base):
    """Модель таблицы wb_report."""
    __tablename__ = 'wb_report'

    id = Column(Integer, Identity(), primary_key=True)
    client_id = Column(String(length=255), ForeignKey('clients.client_id'), nullable=False)
    realizationreport_id = Column(String, default=None, nullable=True)
    gi_id = Column(String, default=None, nullable=True)
    subject_name = Column(Unicode, default=None, nullable=True)
    sku = Column(String, default=None, nullable=True)
    brand = Column(Unicode, default=None, nullable=True)
    vendor_code = Column(Unicode, default=None, nullable=True)
    size = Column(Unicode, default=None, nullable=True)
    barcode = Column(String, default=None, nullable=True)
    doc_type_name = Column(Unicode, default=None, nullable=True)
    quantity = Column(Integer, default=None, nullable=False)
    retail_price = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    retail_amount = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    sale_percent = Column(Integer, default=None, nullable=False)
    commission_percent = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    office_name = Column(Unicode, default=None, nullable=True)
    supplier_oper_name = Column(Unicode, default=None, nullable=True)
    order_date = Column(Date, default=None, nullable=True)
    sale_date = Column(Date, default=None, nullable=True)
    operation_date = Column(Date, default=None, nullable=True)
    shk_id = Column(String, default=None, nullable=True)
    retail_price_withdisc_rub = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    delivery_amount = Column(Integer, default=None, nullable=False)
    return_amount = Column(Integer, default=None, nullable=False)
    delivery_rub = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    gi_box_type_name = Column(Unicode, default=None, nullable=True)
    product_discount_for_report = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    supplier_promo = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    order_id = Column(String, default=None, nullable=True)
    ppvz_spp_prc = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_kvw_prc_base = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_kvw_prc = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    sup_rating_prc_up = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    is_kgvp_v2 = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_sales_commission = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_for_pay = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_reward = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    acquiring_fee = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    acquiring_bank = Column(Unicode, default=None, nullable=True)
    ppvz_vw = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_vw_nds = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    ppvz_office_id = Column(String, default=None, nullable=True)
    ppvz_office_name = Column(Unicode, default=None, nullable=True)
    ppvz_supplier_id = Column(String, default=None, nullable=True)
    ppvz_supplier_name = Column(Unicode, default=None, nullable=True)
    ppvz_inn = Column(String, default=None, nullable=True)
    declaration_number = Column(String, default=None, nullable=True)
    bonus_type_name = Column(Unicode, default=None, nullable=True)
    sticker_id = Column(String, default=None, nullable=True)
    site_country = Column(Unicode, default=None, nullable=True)
    penalty = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    additional_payment = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    rebill_logistic_cost = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    rebill_logistic_org = Column(Unicode, default=None, nullable=True)
    kiz = Column(String, default=None, nullable=True)
    storage_fee = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    deduction = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    acceptance = Column(Numeric(precision=12, scale=2), default=None, nullable=False)
    posting_number = Column(String, default=None, nullable=True)

    client = relationship("Client", back_populates="report_wb")
