from datetime import datetime, timedelta
from pprint import pprint
from src import db

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound


from src.modules.Bridge.controller.BridgeCustomerController import BridgeCustomerController
from ..entities.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from src.modules.SW6.controller.SW6CustomerController import SW6CustomerController

BridgeCustomerViews = Blueprint('bridge_customer_views', __name__)


@BridgeCustomerViews.route('/bridge/customers', endpoint='customers')
def bridge_show_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'id')  # default column to sort by
    sort_order = request.args.get('sort_order', 'asc', type=str)  # default sort order

    query = BridgeCustomerEntity.query

    if search:
        # First all joins
        query = query.join(
            BridgeCustomerAddressEntity,
            BridgeCustomerEntity.id == BridgeCustomerAddressEntity.customer_id
        )
        # Then all fields
        query = query.filter(
            or_(
                BridgeCustomerAddressEntity.last_name.contains(search),
                BridgeCustomerAddressEntity.first_name.contains(search),
                BridgeCustomerEntity.erp_nr.contains(search)
            )

        )

    customers = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('bridge/customer/customers.html', customers=customers, per_page=per_page)


"""
API
"""

@BridgeCustomerViews.route('/api/bridge/customers/update_erp_nr', methods=['PUT'])
def bridge_customer_update_erp_nr():
    data = request.json
    customer_id = data.get('customer_id')
    new_customer_nr = data.get('new_customer_nr')
    bridge_customer_id = data.get('bridge_customer_id')

    if not all([customer_id, new_customer_nr, bridge_customer_id]):
        return jsonify({'status': 'error', 'message': 'Kunden-ID, neue AdrNr und Bridge-Kunden-ID sind erforderlich'}), 400

    print(f"Neue Adrnr: {new_customer_nr} für id: {bridge_customer_id} in Bridge")

    # Check for new_customer_nr in bridge
    new_customer_nr_in_db = BridgeCustomerController().get_entity().query.filter_by(erp_nr=new_customer_nr).one_or_none()
    if new_customer_nr_in_db:
        return jsonify({'status': 'error', 'message': f'AdrNr {new_customer_nr} gibt es bereits in der Bridge!'})

    bridge_customer = BridgeCustomerController().get_entity().query.get(bridge_customer_id)
    if bridge_customer:
        try:
            bridge_customer.erp_nr = new_customer_nr
            db.session.add(bridge_customer)
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'Neue AdrNr: {new_customer_nr} in der Bridge gespeichert.'}), 200
        except SQLAlchemyError as e:
            # Fehler loggen (serverseitig)
            print(f"Fehler beim Speichern der neuen AdrNr in der Bridge: {e}")
            return jsonify({'status': 'error', 'message': 'Datenbankfehler beim Speichern der neuen AdrNr in der Bridge'}), 500
    else:
        return jsonify({'status': 'error', 'message': f'Kunde ID:{customer_id} in der Bridge nicht gefunden!'}), 404