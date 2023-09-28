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
    from .modules.Bridge.entities.BridgeCategoryEntity import (
        BridgeCategoryEntity,
        BridgeCategoryTranslation)

# ERP
    # Controller
    from .modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
    from .modules.ERP.controller.ERPArtikelController import ERPArtikelController
    from .modules.ERP.controller.ERPAdressenController import ERPAdressenController

    # DB create_all to ensure all db tables are there
    with app.app_context():

        # artcat_ctrl = ERPArtikelKategorienController(1, range_end=21000)
        # artcat_ctrl.sync_all_to_bridge()
        db.create_all()

# Return the App Object
    return app, db
