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
    from .modules.Bridge.view.BridgeViews import BridgeViews
    app.register_blueprint(BridgeViews)

    # ERP
    from .modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
    from .modules.ERP.controller.ERPArtikelController import ERPArtikelController
    from .modules.ERP.controller.ERPAdressenController import ERPAdressenController


# Views


# Attention! This is commented, since we handle the db by migrations
# DB create_all to ensure all db tables are there
#    with app.app_context():
#         db.create_all()

# Return the App Object
    return app
