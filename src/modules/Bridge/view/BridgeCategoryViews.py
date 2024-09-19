from pprint import pprint

from flask import Blueprint, render_template, abort, request, jsonify
from sqlalchemy import asc

from src.modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController, BridgeCategoryEntity

BridgeCategoryViews = Blueprint('bridge_category_views', __name__)


@BridgeCategoryViews.route("/categories", endpoint='categories')
def bridge_show_categories():
    categories = BridgeCategoryController().get_all()

    return render_template('bridge/category/categories.html',
                           categories=categories)


@BridgeCategoryViews.route("/category/<int:category_id>", endpoint='category')
def bridge_show_category(category_id):
    category = BridgeCategoryEntity().query.get(category_id)
    if category:
        return render_template('bridge/category/category.html', category=category)
    else:
        abort(404)


@BridgeCategoryViews.route("/categories_tree", endpoint='categories_tree')
def bridge_show_categories_tree():
    categories = BridgeCategoryController().get_entity().query.order_by(asc("cat_nr")).all()
    return render_template('bridge/category/categories_tree.html',
                           categories=categories)


"""
API
"""

@BridgeCategoryViews.route("/api/categories/get_category_tree", methods=['GET', 'POST'])
def api_get_category_tree():
    tree = BridgeCategoryController().build_tree()
    if tree:
        return tree
    else:
        abort(404)


@BridgeCategoryViews.route("/api/category/set_assoc_sort", methods=['POST'])
def api_set_assoc_sort():
    data = request.get_json()

    # Access your data (replace with your logic)
    moved = data['moved']
    source = data['source']
    target = data['target']
    target_next_node = data['targetNextNode']

    # If a Product was moved
    if moved['type_of'] == 'product':
        print("Product moved")
        return jsonify({'result': 'success'}, 200)
    # If a category was moved
    elif moved['type_of'] == 'category':
        result = BridgeCategoryController().move_category(moved=moved, source=source, target=target,
                                                          target_next_node=target_next_node)
        return jsonify({'result': 'success'}, 200)
    # if anything else raise error:
    else:
        print(f"Move {moved['type_of']} not possible. Something weired caused a ajax call")
        return jsonify({'result': 'error'}, 500)

