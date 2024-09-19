import datetime
from pprint import pprint

from flask import Blueprint, render_template, request, abort, jsonify, redirect, url_for
from sqlalchemy import or_

from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity, BridgeProductTranslation
from src.modules.Bridge.entities.BridgeMarketplaceEntity import BridgeProductMarketplacePriceAssoc
from src.modules.Bridge.controller.BridgePriceController import BridgePriceController
from src.modules.SW6.controller.SW6ProductController import SW6ProductController
from src.modules.ERP.controller.ERPArtikelController import ERPArtikelController
from config import GCBridgeConfig, SW6Config
from src import db

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
    config = GCBridgeConfig

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bridge/product/products.html', products=products, per_page=per_page, config=config)


@BridgeProductViews.route('/products_sort', endpoint='products_sort')
def products_sort():
    categories = BridgeCategoryEntity().query.filter_by(parent_category_id=None).all()

    return render_template(
        'bridge/product/products_sort.html',
        categories=categories
    )

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

@BridgeProductViews.route('/product/special_price_submit', methods=['POST'], endpoint='special_price_submit')
def special_price_submit():
    # Assign values from the request
    special_price_received = request.form.get('percentage')
    special_start_date_received = request.form.get('special_start_date')
    special_end_date_received = request.form.get('special_end_date')
    marketplace_id = int(request.form.get('marketplace_id'))
    price_id = int(request.form.get('price_id'))
    product_id = int(request.form.get('product_id'))

    # Convert received date strings to datetime objects
    special_start_date = datetime.datetime.strptime(special_start_date_received,
                                                    "%Y-%m-%d") if special_start_date_received else None
    special_end_date = datetime.datetime.strptime(special_end_date_received,
                                                  "%Y-%m-%d") if special_end_date_received else None

    # Convert received percentage string to float
    special_price = float(special_price_received) if special_price_received else 0

    # Create the controller
    price_controller = BridgePriceController()

    # Call the controller to update the price
    price_controller.set_price_with_percentage(price_id, special_price, special_start_date, special_end_date)

    # If marketplace id is 1, perform the same operation on all marketplaces
    if marketplace_id == 1:
        price_controller.apply_marketplace_price_change(product_id, special_price, special_start_date, special_end_date)

    return redirect(url_for('bridge_product_views.product', id=product_id))


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

@BridgeProductViews.route('/api/product/sync_to_erp/<bridge_product_id>')
def api_product_sync_to_erp(bridge_product_id):
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
            erp_product_controller = ERPArtikelController(product.get_erp_nr())
            result = erp_product_controller.sync_one_from_bridge(bridge_entity=product)

        except Exception as ex:
            return jsonify({
                               'message': f'Das Produkt <b>{product.get_translation().get_name()}<b/> konnte nicht in ERP synchronisiert werden',
                               'status': 'error'})

        # If synchronization is successful, return success message, else return error message.
        if result:
            return jsonify({
                               'message': f'Das Produkt <b>{product.get_translation().get_name()}<b/> wurde erfolgreich in ERP synchronisiert',
                               'status': 'success'})
        else:
            return jsonify({
                               'message': f'Das Produkt <b>{product.get_translation().get_name()}<b/> konnte nicht in ERP synchronisiert werden',
                               'status': 'error'})

    else:
        return jsonify(
            {'message': f'Das Produkt <b>{product.get_translation().get_name()}<b/> wurde nicht in der DB gefunden',
             'status': 'error'})

@BridgeProductViews.route("/api/product/sync_product_marketplace_status/<product_id>/<marketplace_id>/<state>",
                          methods=['GET'])
def api_product_sync_state(product_id, marketplace_id, state):
    # Convert "true"/"false" string to boolean
    state_bool = state.strip().lower() == 'true'

    # 1. Change Bridge
    product_marketplace_assoc = BridgeProductMarketplacePriceAssoc()
    association = BridgeProductMarketplacePriceAssoc.query.filter_by(
        product_id=product_id,
        marketplace_id=marketplace_id
    ).one_or_none()
    bridge_product_entity = association.get_product()
    association.set_is_active(state_bool)
    db.session.add(association)
    db.session.commit()
    db.session.refresh(association)

    # 2. Change SW6
    pprint(bridge_product_entity)
    sw_bridge_controller = SW6ProductController()
    sw_bridge_controller.deactivate_in_saleschannel(bridge_entity=association.get_product())

    return jsonify(
        {
            'message': f'Status geändert. '
                       f'Neuer Bridge Status: <b>{association.get_is_active()}</b><br/>'
                       f'Neuer SW6 Status: <b>{association.get_is_active()}</b>',
            'status': 'success'})

@BridgeProductViews.route("/api/product/sync_status/<bridge_product_id>/<new_state>", methods=['GET'])
def api_product_sync_status(bridge_product_id, new_state):
    # 1. In der Bridge deaktivieren
    bridge_product_entity = BridgeProductEntity.query.get(bridge_product_id)
    state_bool = new_state.strip().lower() == 'true'
    bridge_product_entity.set_is_active(state_bool)

    db.session.add(bridge_product_entity)
    db.session.commit()
    db.session.refresh(bridge_product_entity)

    bridge_status = bridge_product_entity.get_is_active()

    # 2. In SW6 deaktivieren
    sw_bridge_controller = SW6ProductController()
    sw6_result = sw_bridge_controller.get_entity().set_status(bridge_entity=bridge_product_entity)
    sw6_status = sw6_result["data"]["active"]

    if sw6_status == bridge_status:
        print("both the same")
    else:
        print("SW6", sw6_status, "Bridge", bridge_status)

    return jsonify(
        {
            'message': f'Anfrage bearbeitet. '
                       f'Neuer Bridge Status: <b>{bridge_status}</b><br/>'
                       f'Neuer SW6 Status: <b>{sw6_status}</b>',
            'status': 'success'})


@BridgeProductViews.route('/api/product/delete_in_bridge/<bridge_product_id>', methods=['DELETE'])
def api_delete_product_in_bridge(bridge_product_id):
    """
    This function is responsible for deleting a single product from the bridge based on the given product ID.

    :param bridge_product_id: The ID of the product which needs to be deleted from the bridge
    :return: A JSON response object that contains a message and status indicating the deletion status of the product
    """

    try:
        # Fetch the product from the bridge based on the provided ID.
        product = BridgeProductEntity.query.get(bridge_product_id)
    except Exception as ex:
        return jsonify({'message': 'An error occured during product retrieval from the database', 'status': 'error'})

    if product:
        try:
            # Delete the product from the database
            db.session.delete(product)
            db.session.commit()
            return jsonify(
                {'message': f'Das Produkt {bridge_product_id} wurde erfolgreich gelöscht', 'status': 'success'})
        except Exception as ex:
            db.session.rollback()
            return jsonify(
                {'message': f'Das Produkt {bridge_product_id} konnte nicht gelöscht werden', 'status': 'error'})
    else:
        return jsonify(
            {'message': f'Das Produkt {bridge_product_id} wurde nicht in der Db gefunden', 'status': 'error'})


@BridgeProductViews.route('/api/product/update_in_bridge/<bridge_product_id>', methods=['PUT'])
def api_update_product_in_bridge(bridge_product_id):
    """
    This function is responsible for updating a single product in the bridge based on the given product ID and provided data.

    :param bridge_product_id: The ID of the product which needs to be updated in the bridge
    :return: A JSON response object that contains a message and status indicating the update status of the product
    """
    try:
        # Fetch the product from the bridge based on the provided ID.
        product = BridgeProductEntity.query.filter_by(id=bridge_product_id).one_or_none()

    except Exception as ex:
        return jsonify(
            {'message': f'An error occurred during product retrieval from the database: {ex}', 'status': 'error'})

    if not product:
        return jsonify(
            {'message': f'Das Produkt {bridge_product_id} wurde nicht in der Db gefunden', 'status': 'error'})

    try:
        erp_product_controller = ERPArtikelController(search_value=product.get_erp_nr())
        bridge_product_entity_id = erp_product_controller.sync_one_to_bridge()
        if bridge_product_entity_id:
            return jsonify(
                {'message': f'Das Produkt {bridge_product_id} wurde erfolgreich aktualisiert', 'status': 'success'})
    except Exception as ex:
        return jsonify(
            {'message': f'Das Produkt {bridge_product_id} konnte nicht aktualisiert werden Error{str(ex)}',
             'status': 'error'})

@BridgeProductViews.route('/api/product/search', methods=['GET'])
def search():
    """Search for products based on a query parameter.

    This function accepts a GET request with a 'q' query parameter for
    a search string. It uses this search string to attempt to find matches
    in both the 'erp_nr' field of the BridgeProductEntity and the 'name'
    field in the associated BridgeProductTranslations. If matches are found,
    it returns them in a list of dictionaries as a JSON response.

    If no matches are found, it returns a "No results" message. If an
    exception occurs during the search attempt, it provides an "Error" message.

    Returns:
        Flask Response: A JSON response containing either a list of matching
                        products or an error message.
    """

    # The query parameter from the request
    query_param = request.args.get('q')

    try:
        # Adding wildcards for LIKE SQL query
        query = '%' + query_param + '%'

        # Searching in erp_nr and product translations
        results = BridgeProductEntity.query.filter(
            or_(
                BridgeProductEntity.erp_nr.like(query),
                BridgeProductEntity.translations.any(BridgeProductTranslation.name.like(query))
            )
        ).all()

        # Check if results were found
        if not results:
            return jsonify({"message": "No results"})

        # Generate a list with the product information we want to return
        output = [
            {
                'id': product.id,
                'erp_nr': product.erp_nr,
                'name': product.get_translation().name if product.get_translation() else None
            }
            for product in results
        ]

        return jsonify(output)

    except Exception as e:
        # Log the error and return a message
        print(f"An error occurred while attempting the search: {str(e)}")
        return jsonify({"message": "An error occurred. Please try again later."})


@BridgeProductViews.route('/api/products/get_by_category/<category_id>', methods=['GET'])
def api_products_get_by_category(category_id):
    """
    This function retrieves all products associated with a given category ID.

    :param category_id: The ID of the category whose products need to be fetched.
    :return: A JSON response object that contains a list of products or an error message.
    """

    try:
        # Fetch the category from the database based on the provided ID
        category = BridgeCategoryEntity.query.get(category_id)

        if not category:
            return jsonify({'message': f'Category with ID {category_id} not found', 'status': 'error'})

        # Fetch all products associated with the category
        products = category.products

        # Produkte filtern (nur aktive Produkte) und nach 'sort' aufsteigend sortieren
        active_products = [product for product in products if product.get_is_active()]
        sorted_products = sorted(
            active_products,
            key=lambda product: (product.sort is None, product.sort if product.sort is not None else 0)
        )

        # Build the list of product dictionaries with relevant fields
        products_list = []
        for product in sorted_products:
            if product.get_is_active():
                translation = product.get_translation()
                product_data = {
                    'id': product.id,
                    'erp_nr': product.erp_nr,
                    'name': translation.name,
                    'sort': product.sort,
                }
                products_list.append(product_data)

        return jsonify({'products': products_list, 'status': 'success'})

    except Exception as ex:
        return jsonify({'message': 'An error occurred while fetching products from the database', 'status': 'error'})


@BridgeProductViews.route('/api/product/update_sort', methods=['POST'])
def api_product_update_sort():
    """
    API-Endpunkt zum Aktualisieren des 'sort'-Felds eines Produkts.
    Erwartet JSON-Daten mit 'product_id' und 'sort'.
    """
    data = request.get_json()
    product_id = data.get('product_id')
    sort_value = data.get('sort')

    if product_id is None or sort_value is None:
        return jsonify({'message': 'Produkt-ID und Sortierwert sind erforderlich', 'status': 'error'}), 400

    try:
        sort_value = int(sort_value)
    except ValueError:
        return jsonify({'message': 'Sortierwert muss eine Ganzzahl sein', 'status': 'error'}), 400

    product = BridgeProductEntity.query.get(product_id)
    if not product:
        return jsonify({'message': f'Produkt mit ID {product_id} nicht gefunden', 'status': 'error'}), 404

    try:
        product.set_sort(sort_value)
        db.session.commit()
        return jsonify({'message': f'Sortierwert für Produkt {product_id} aktualisiert', 'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Fehler beim Aktualisieren des Sortierwerts: {str(e)}', 'status': 'error'}), 500
