import uuid
from pprint import pprint

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

from sqlalchemy import asc

import config
from config import DBConfig

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    # Define the root directory
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__)
    app.config.from_object(DBConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    """ All the imports go here """

    """
    ############
    Jinja Functions
    ############
    """
    from config import JinjaConfig
    app.jinja_env.filters['currency_format'] = JinjaConfig.currency_format
    app.jinja_env.filters['date_field_format'] = JinjaConfig.date_field_format

    """
    ############
    Bridge
    ############
    """
    # Views
    from .modules.Bridge.view.BridgeDashboardViews import BridgeDashboardViews
    app.register_blueprint(BridgeDashboardViews)

    from .modules.Bridge.view.BridgeViews import BridgeViews
    app.register_blueprint(BridgeViews)

    from .modules.Bridge.view.BridgeOrderViews import BridgeOrderViews
    app.register_blueprint(BridgeOrderViews)

    from .modules.Bridge.view.BridgeCustomerViews import BridgeCustomerViews
    app.register_blueprint(BridgeCustomerViews)

    from .modules.Bridge.view.BridgeCategoryViews import BridgeCategoryViews
    app.register_blueprint(BridgeCategoryViews)

    from .modules.Bridge.view.BridgeProductViews import BridgeProductViews
    app.register_blueprint(BridgeProductViews)

    from .modules.Bridge.view.BridgeRuleViews import BridgeRuleViews
    app.register_blueprint(BridgeRuleViews)

    # Entities
    from .modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity
    from .modules.Bridge.entities.BridgeProductEntity import (BridgeProductEntity,
                                                              BridgeProductTranslation)
    from .modules.Bridge.entities.BridgePriceEntity import BridgePriceEntity
    from .modules.Bridge.entities.BridgeCustomerEntity import (BridgeCustomerEntity,
                                                               BridgeCustomerAddressEntity)

    from .modules.Bridge.entities.BridgeMarketplaceEntity import (BridgeMarketplaceEntity,
                                                                  BridgeProductMarketplacePriceAssoc,
                                                                  BridgeCustomerMarketplaceAssoc)
    from .modules.Bridge.entities.BridgeCategoryEntity import (BridgeCategoryEntity,
                                                               BridgeCategoryTranslation,
                                                               BridgeProductsCategoriesAssoc)
    from .modules.Bridge.entities.BridgeMediaEntity import (BridgeMediaEntity,
                                                            BridgeMediaTranslation,
                                                            BridgeCategoryMediaAssoc,
                                                            BridgeProductsMediaAssoc)
    from .modules.Bridge.entities.BridgeOrderEntity import BridgeOrderEntity
    from .modules.Bridge.entities.BridgeOrderDetailsEntity import BridgeOrderDetailsEntity
    from .modules.Bridge.entities.BridgeRuleEntity import BridgeRuleEntity

    # Controller
    from .modules.Bridge.controller.BridgeProductController import BridgeProductController
    from .modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController
    from .modules.Bridge.controller.BridgeMediaController import BridgeMediaController
    from .modules.Bridge.controller.BridgeMarketplaceController import BridgeMarketplaceController
    from .modules.Bridge.controller.BridgeOrderController import BridgeOrderController
    from .modules.Bridge.controller.BridgeRuleController import BridgeRuleController

    """
    ############
    ERP
    ############
    """
    # Entities
    from .modules.ERP.entities.ERPAdressenEntity import (ERPAdressenEntity,
                                                         ERPAnschriftenEntity,
                                                         ERPAnsprechpartnerEntity)
    from .modules.ERP.entities.ERPArtikelEntity import ERPArtikelEntity

    # Controller
    from .modules.ERP.controller.ERPMandantSteuerController import ERPMandantSteuerController
    from .modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
    from .modules.ERP.controller.ERPArtikelController import ERPArtikelController
    from .modules.ERP.controller.ERPAdressenController import ERPAdressenController
    from .modules.ERP.controller.ERPLagerController import ERPLagerController
    from .modules.ERP.controller.ERPKontenplanController import ERPKontenplanController

    """
    ############
    SW6
    ############
    """
    # Entities
    from .modules.SW6.entities.SW6CategoryEntity import SW6CategoryEntity
    from .modules.SW6.entities.SW6ProductEntity import SW6ProductEntity
    from .modules.SW6.entities.SW6MediaEntity import SW6MediaEntity

    # Controller
    from .modules.SW6.controller.SW6OrderController import SW6OrderController
    from .modules.SW6.controller.SW6CustomerController import SW6CustomerController
    from .modules.SW6.controller.SW6MarketplaceController import SW6MarketplaceController
    from .modules.SW6.controller.SW6ProductController import SW6ProductController
    from .modules.SW6.controller.SW6CategoryController import SW6CategoryController
    from .modules.SW6.controller.SW6MediaController import SW6MediaController
    from .modules.SW6.controller.SW6BackupController import SW6BackupController

    # Views
    from .modules.SW6.view.SW6CustomerViews import SW6CustomerViews
    app.register_blueprint(SW6CustomerViews)
    from .modules.SW6.view.SW6BackupViews import SW6BackupViews
    app.register_blueprint(SW6BackupViews)

    """
    ############
    Mail
    ############
    """
    # Entities
    from .modules.Mail.entities.MailEntity import MailEntity

    # Controller
    from .modules.Mail.controller.MailController import MailCoreController

    # Views
    from .modules.Mail.view.MailViews import MailViews
    app.register_blueprint(MailViews)

    # WebScraper
    from .modules.webscraper.controller.WebScraperController import WebScraperController

    # Tests
    # from .modules.Test.AbstractController import speak

    # DB create_all to ensure all db tables are there
    with app.app_context():
        # db.drop_all()
        db.create_all()
        # 1 Categories
        # ERPArtikelKategorienController(search_value="1", range_end="30000").sync_all_to_bridge()
        # SW6CategoryController().sync_all_from_bridge()

        # 2. Products
        # ERPArtikelController(search_value='291000', range_end='999999').sync_all_to_bridge()
        # ERPArtikelController(search_value='104025').sync_one_to_bridge()
        # SW6ProductController().sync_all_from_bridge()

        # try:
        #     bridge_product_entity = BridgeProductController().get_entity()
        #     product = bridge_product_entity.query.filter_by(erp_nr='091300').one_or_none()
        #     if product:
        #         response = SW6ProductController().sync_one_from_bridge(bridge_entity=product)
        #         pprint(response)
        # except Exception as e:
        #     print("Error: " + str(e))

        # 3. Addresses
        # ERP -> Bridge
        # id = ERPAdressenController("091300").sync_one_to_bridge()
        # Bridge -> ERP
        # bridge_entity = BridgeCustomerEntity.query.filter_by(erp_nr='10026').one_or_none()
        # if bridge_entity:
        #     ERPAdressenController().sync_one_from_bridge(bridge_entity=bridge_entity)
        # 4. Marketplaces downsert
        # SW6MarketplaceController().sync_all_to_bridge()
        # ERPAdressenController(search_value='10026').get_entity().print_all_anschriften_and_ansprechparter()

        # 5. Kunden
        # erp_anschrift = ERPAnschriftenEntity()
        # erp_anschrift.find_wildcard(search_value="?Patentamt", dataset_index="Na2")
        # erp_anschrift.set_filter("Ort='München'")
        # erp_anschrift.range_first()
        # print("Range count:", erp_anschrift.range_count())
        # while not erp_anschrift.range_eof():
        #     print(erp_anschrift.get_adrnr(), erp_anschrift.get_id(), erp_anschrift.get_na2(), erp_anschrift.get_city())
        #     erp_anschrift.range_next()

        # SW6ProductController().get_entity().delete_all()
        # result = ERPArtikelController(search_value="090000", range_end="999999").sync_all_to_bridge()
        # result = ERPArtikelController(search_value="291021").sync_one_to_bridge()
        # product = BridgeProductController().get_entity().query.filter_by(erp_nr='204011').one_or_none()
        # result = SW6ProductController().sync_one_from_bridge(bridge_entity=product)

        # SW6ProductController().sync_all_from_bridge()

        # 6. Bestellungen
        # SW6OrderController().get_api_state_machines_list_for_config()

        # pprint(result)
        # print("############################# Answer from SW6 #########################")
        # result = SW6ProductEntity().get_details(id="b4ce53e0a0ac43cb95269505988cc66e")
        # pprint(result["data"][0]["prices"])

        # 10. Rules

        # 11. Backups
        # SW6BackupController().backup_directory()

        """ Webscraper """
        # scraper = WebScraperController(file_name="Bestatter_v2.xlsx").get_addresses_bestattungsvergleich_de()
        # scrapper = WebScraperController(file_name="bestatter_at.xlsx").get_addresses_bestatter_at()
        # scraper = WebScraperController(file_name="Evangelische_Kirche.xlsx").get_addresses_evangelische_kirchen_bayern()
        # scraper = WebScraperController(file_name="Katholische_Kirche_Bistum_München.xlsx").get_addresses_katholische_kirchen_munic()
        # scraper = WebScraperController(file_name="Betreuer.xlsx").get_addresses_bdb()

        # scraper = WebScraperController(file_name='Mappei.xlsx').get_prices_mappei()

        # sw6_customer_entity = SW6CustomerController().get_entity()
        # sw6_customer_entity.sw5_get_customers_list()
        # print('\033[31mError \033[0m')

        # Delete all orders
        # sw6_order_entity = SW6OrderController().get_entity()
        # response = sw6_order_entity.get_api_list()
        # pprint(response)
        # for order in response['data']:
        #     pprint(order['id'])
        #     response_delete = sw6_order_entity.delete(order['id'])

    # Return the App Object
    return app, db
