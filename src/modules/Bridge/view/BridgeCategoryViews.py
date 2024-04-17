from flask import Blueprint, render_template
from src.modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController

BridgeCategoryViews = Blueprint('bridge_category_views', __name__)


@BridgeCategoryViews.route("/categories", endpoint='categories')
def bridge_show_categories():
    categories = BridgeCategoryController().get_all()

    return render_template('bridge/category/categories.html',
                           categories=categories)
