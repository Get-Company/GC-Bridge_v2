from flask import Blueprint, render_template, request, abort, redirect, url_for
from src import db
from src.modules.ERP.controller.ERPArtikelKategorienController import ERPArtikelKategorienController
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity
from src.modules.Bridge.controller.BridgeCategoryController import BridgeCategoryController
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity
from src.modules.Bridge.entities.BridgeMarketplaceEntity import BridgeMarketplaceEntity
from src.modules.Bridge.entities.BridgeMarketplaceForm import BridgeMarketplaceForm
from config import GCBridgeConfig
from sqlalchemy import or_, desc, asc

BridgeViews = Blueprint('bridge_views', __name__)


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
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id')  # default column to sort by
    sort_order = request.args.get('sort_order', 'asc', type=str)  # default sort order

    query = BridgeProductEntity.query

    if search:
        # for example if your entity has 'name' and 'description' exposed
        query = query.filter(
            BridgeProductEntity.erp_nr.contains(search)
        )

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bridge/product/products.html', products=products, per_page=per_page)


@BridgeViews.route('/inventur', endpoint='inventur')
def bridge_products_inventur():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id')  # default column to sort by
    sort_order = request.args.get('sort_order', 'asc', type=str)  # default sort order

    query = BridgeProductEntity.query

    if search:
        # for example if your entity has 'name' and 'description' exposed
        query = query.filter(
            BridgeProductEntity.erp_nr.contains(search)
        )

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bridge/product/inventur.html', products=products, per_page=per_page)


@BridgeViews.route('/product/<id>', endpoint='product')
def bridge_product(id):
    product = BridgeProductEntity.query.get(id)

    if product:

        return render_template('bridge/product/product.html',
                               product=product,
                               assets_img_path=GCBridgeConfig.ASSETS_PATH + "/" + GCBridgeConfig.IMG_PATH
                               )
    else:
        abort(404)


@BridgeViews.route('/product/erp_nr/<erp_nr>', endpoint='product_by_erp_nr')
def bridge_product_by_erp_nr(erp_nr):
    product = BridgeProductEntity.query.filter_by(erp_nr=erp_nr).one_or_none()

    if product:

        return render_template('bridge/product/product.html',
                               product=product,
                               assets_img_path=GCBridgeConfig.ASSETS_PATH + "/" + GCBridgeConfig.IMG_PATH
                               )
    else:
        abort(404)


@BridgeViews.route('/marketplaces', endpoint='marketplaces')
def bridge_marketplaces():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id')  # default column to sort by
    sort_order = request.args.get('sort_order', 'asc', type=str)  # default sort order

    query = BridgeMarketplaceEntity.query

    if search:
        # for example if your entity has 'name' and 'description' exposed
        query = query.filter(
            BridgeMarketplaceEntity.name.contains(search)
        )

    marketplaces = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bridge/marketplace/marketplaces.html', marketplaces=marketplaces, per_page=per_page)


@BridgeViews.route('/marketplace/<int:id>', endpoint='marketplace', methods=['POST', 'GET'])
def bridge_marketplacet(id):
    marketplace = BridgeMarketplaceEntity.query.get_or_404(id)
    form = BridgeMarketplaceForm(request.form, obj=marketplace)
    if request.method == 'POST' and form.validate():
        form.populate_obj(marketplace)
        db.session.commit()
    return render_template('bridge/marketplace/marketplace.html', form=form, marketplace=marketplace)

