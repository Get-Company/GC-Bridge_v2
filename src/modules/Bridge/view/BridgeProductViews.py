from flask import Blueprint, render_template, request, abort, jsonify
from src.modules.Bridge.controller.BridgeProductController import BridgeProductController, BridgeProductEntity
from src.modules.SW6.controller.SW6ProductController import SW6ProductController
from config import GCBridgeConfig, SW6Config

BridgeProductViews = Blueprint('bridge_product_views', __name__)


@BridgeProductViews.route('/products', endpoint='products')
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


@BridgeProductViews.route('/product/<id>', endpoint='product')
def bridge_product(id):
    product = BridgeProductEntity.query.get(id)

    if product:

        return render_template('bridge/product/product.html',
                               product=product,
                               assets_img_path=GCBridgeConfig.ASSETS_PATH + "/" + GCBridgeConfig.IMG_PATH
                               )
    else:
        abort(404)


@BridgeProductViews.route('/product/erp_nr/<erp_nr>', endpoint='product_by_erp_nr')
def bridge_product_by_erp_nr(erp_nr):
    product = BridgeProductEntity.query.filter_by(erp_nr=erp_nr).one_or_none()

    if product:

        return render_template('bridge/product/product.html',
                               product=product,
                               assets_img_path=GCBridgeConfig.ASSETS_PATH + "/" + GCBridgeConfig.IMG_PATH
                               )
    else:
        abort(404)


"""
API
"""

@BridgeProductViews.route('/api/product/sync_to_sw6/<bridge_product_id>')
def api_product_sync_to_sw6(bridge_product_id):
    """
    This function is responsible to synchronize a single product from the bridge to SW6 based on the given product ID.

    :param bridge_product_id: The ID of the product which needs to be synchronized from the bridge to SW6
    :return: A JSON response object that contains a message and status indicating the synchronization status of product
    """

    try:
        # Fetch the product from the bridge based on the provided ID.
        product = BridgeProductEntity.query.get(bridge_product_id)
    except Exception as ex:
        return jsonify({'message': 'An error occured during product retrieval from the database', 'status': 'error'})

    if product:
        try:
            # Call the sync_one_from_bridge method of the SW6ProductController to sync the product to SW6.
            result = SW6ProductController().sync_one_from_bridge(product)
        except Exception as ex:
            return jsonify({'message': f'Das Produkt {bridge_product_id} konnte nicht in SW6 synchronisiert werden',
                            'status': 'error'})

        # If synchronization is successful, return success message, else return error message.
        if result:
            return jsonify({'message': f'Das Produkt {bridge_product_id} wurde erfolgreich in SW6 synchronisiert',
                            'status': 'success'})
        else:
            return jsonify({'message': f'Das Produkt {bridge_product_id} konnte nicht in SW6 synchronisiert werden',
                            'status': 'error'})

    else:
        return jsonify({'message': f'Das Produkt {bridge_product_id} wurde nicht in der Db gefunden',
                        'status': 'error'})