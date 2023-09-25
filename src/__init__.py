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
# Entities
    # ERP Entities are not necessary

    # Bridge
    from .modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity, BridgeCategoryTranslation, bridge_category_marketplace_association
    from .modules.Bridge.entities.BridgeMarketplaceEntity import BridgeMarketplaceEntity

# Controller
    # ERP Controller
    from .modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
    from .modules.ERP.controller.ERPArtikelController import ERPArtikelController
    from .modules.ERP.controller.ERPAdressenController import ERPAdressenController

    # Bridge Controller
# Views
    # ERP Views
    from .view.dashboard_view import dashboard_view
    app.register_blueprint(dashboard_view, url_prefix="/")

# DB create_all to ensure all db tables are there
    with app.app_context():
        db.create_all()

# Return the App Object
    return app
