from flask import Blueprint, render_template, request
from src import db
from src.modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity

BridgeViews = Blueprint('bridge_views', __name__)


@BridgeViews.route('/', endpoint='dashboard')
def bridge_dashboard_view():
    return render_template('bridge/dashboard.html')


@BridgeViews.route('/rules', endpoint='rules')
def bridge_rules_view():
    return render_template('bridge/rules/rules.html')


@BridgeViews.route('/categories', endpoint='categories')
def bridge_categories():
    cat_ntt = BridgeCategoryEntity()
    categories = db.session.query(BridgeCategoryEntity).all()
    return render_template('bridge/category/categories.html', categories=categories)

@BridgeViews.route('/products', endpoint='products')
def bridge_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = BridgeProductEntity.query
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bridge/product/products.html', products=products, per_page=per_page)


""" 
    Example for the template:
    <!-- In index.html -->
    <a href="{{ url_for('bridge_views.dashboard') }}">Go to Home/Dashboard</a>
"""
