from flask import Blueprint, render_template
from src import db
from src.modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity

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


""" 
    Example for the template:
    <!-- In index.html -->
    <a href="{{ url_for('bridge_views.dashboard') }}">Go to Home/Dashboard</a>
"""
