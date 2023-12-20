from pprint import pprint

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
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

# Bridge
    # Views
    from .modules.Bridge.view.BridgeViews import BridgeViews
    app.register_blueprint(BridgeViews)

    # Entities
    from .modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity
    from .modules.Bridge.entities.BridgeProductEntity import (BridgeProductEntity,
                                                              BridgeProductTranslation,)
    from .modules.Bridge.entities.BridgePriceEntity import BridgePriceEntity
    from .modules.Bridge.entities.BridgeMarketplaceEntity import (BridgeMarketplaceEntity,
                                                                  BridgeProductMarketplacePriceAssoc)
    from .modules.Bridge.entities.BridgeCategoryEntity import (BridgeCategoryEntity, BridgeCategoryTranslation,
                                                               BridgeProductsCategoriesAssoc)
    from .modules.Bridge.entities.BridgeMediaEntity import (BridgeMediaEntity,
                                                            BridgeMediaTranslation,
                                                            BridgeCategoryMediaAssoc,
                                                            BridgeProductsMediaAssoc)

    # Controller
    from .modules.Bridge.controller.BridgeProductController import BridgeProductController
    from .modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController
    from .modules.Bridge.controller.BridgeMediaController import BridgeMediaController
    from .modules.Bridge.controller.BridgeProductController import BridgeProductController

# ERP
    # Controller
    from .modules.ERP.controller.ERPMandantSteuerController import ERPMandantSteuerController
    from .modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
    from .modules.ERP.controller.ERPArtikelController import ERPArtikelController
    from .modules.ERP.controller.ERPAdressenController import ERPAdressenController
    from .modules.SW6.entities.SW6CategoryEntity import SW6CategoryEntity
    from .modules.SW6.entities.SW6ProductEntity import SW6ProductEntity

    # DB create_all to ensure all db tables are there
    with app.app_context():
        # db.drop_all()
        db.create_all()
        # Create Marketplaces
        # Büro+ Marktplatz
        # buro_plus_marketplace = BridgeMarketplaceEntity(
        #     name="Büro+ Warenwirtschaft",
        #     description="Warenwirtschaftssystem Büro+",
        #     url="http://bueroplus.example.com",
        #     api_key="bueroplus_api_key",  # falls erforderlich
        #     config={}  # Faktor 1.0 und fixed prices
        # )
        #
        # # Shopware 5 - CH Schweiz Marktplatz
        # shopware_ch_marketplace = BridgeMarketplaceEntity(
        #     name="Shopware 5 - Schweiz",
        #     description="Shopware 5 Marktplatz für die Schweiz",
        #     url="http://shopware5ch.example.com",
        #     api_key="shopware5ch_api_key",  # falls erforderlich
        #     config={},
        #     factor=1.3
        # )
        #
        # # Fügen Sie die Objekte der Session hinzu und commiten Sie
        # db.session.add(buro_plus_marketplace)
        # db.session.add(shopware_ch_marketplace)
        # db.session.commit()

        # 1 Categories
        # ERPArtikelKategorienController(search_value="1", range_end="30000").sync_all_to_bridge()
        # 2. Products
        # ERPArtikelController(search_value='10000', range_end='15000').sync_all_to_bridge()
        # 3. Addresses

# Return the App Object
    return app, db
