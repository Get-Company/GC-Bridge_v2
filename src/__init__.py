from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from config import DBConfig


db = SQLAlchemy()


def create_app():

    # Define the root directory
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__)
    app.config.from_object(DBConfig)
    db.init_app(app)

    """ All the imports go here """

    # Controller
    from .modules.ERP.controller.ERPKategorieController import ERPKategorieController

    # Views
    from .view.dataset_view import dataset_view
    app.register_blueprint(dataset_view, url_prefix="/erp")

    with app.app_context():
        db.create_all()

    return app
