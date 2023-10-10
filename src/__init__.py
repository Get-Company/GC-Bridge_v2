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
    from .modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity, BridgeCategoryTranslation, BridgeProductsCategoriesAssoc
    from .modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity, BridgeProductTranslation

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
        products = BridgeProductEntity.query.all()
        for product in products:
            db.session.delete(product)
            db.session.commit()
            db.session.close()
        # ERPArtikelController(search_value=581000).sync_one_to_bridge()

# Return the App Object
    return app, db
