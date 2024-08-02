from datetime import datetime, timedelta
from pprint import pprint

import config
from src.modules.ModulesCoreController import ModulesCoreController

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from src.modules.Bridge.controller.BridgeOrderController import BridgeOrderController
from src.modules.SW6.controller.SW6OrderController import SW6OrderController
from src.modules.ERP.controller.ERPVorgangController import ERPVorgangController
from src.modules.ERP.controller.ERPAdressenController import ERPAdressenController
BridgeOrderViews = Blueprint('bridge_order_views', __name__)


@BridgeOrderViews.route('/orders', endpoint='orders')
def bridge_show_orders():
    # Abfragen der Start- und Enddaten aus der URL (beide Parameter sind optional)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    all_orders = request.args.get('all_orders', default="false") == "true"

    # Abrufen der Bestellungen mit optionalen Filtern
    orders, start_date_obj, end_date_obj, all_orders = BridgeOrderController().get_orders_by_date(start_date=start_date,
                                                                                                  end_date=end_date,
                                                                                                  all_orders=all_orders)

    filter_start_date = filter_end_date = None   # Setzen Sie die Standardwerte auf None

    if start_date_obj:
        filter_start_date = start_date_obj
    if end_date_obj:
        filter_end_date = end_date_obj

    return render_template('bridge/order/orders.html',
                           orders=orders,
                           filter_start_date=filter_start_date,
                           filter_end_date=filter_end_date,
                           all_orders=all_orders,
                           order_state_machine_id=config.SW6Config.ORDER_STATE_MACHINE,
                           payment_state_machine_id=config.SW6Config.PAYMENT_STATE_MACHINE,
                           shipping_state_machine_id=config.SW6Config.SHIPPING_STATE_MACHINE
                           )

"""
API
"""


# ERP create order
@BridgeOrderViews.route('/api/orders/erp/create_order/<bridge_order_id>', methods=["GET", "POST"])
def api_orders_erp_create_order(bridge_order_id):
    bridge_order = BridgeOrderController().get_entity().query.get(bridge_order_id)
    if bridge_order:
        # adresse_in_erp = ERPAdressenController().sync_order_addresses_from_bridge(bridge_entity=bridge_order.customer)
        order_in_erp = ERPVorgangController().downsert(bridge_entity=bridge_order)
        return jsonify({'status': 'success', 'message': f'Bestellung {bridge_order_id} wurde in ERP angelegt.'})
    else:
        return jsonify({'status': 'error', 'message': f'No order found in bridge by ID:{bridge_order_id}'})


# SW6 Get open orders
@BridgeOrderViews.route('/api/orders/sw6/get_open_order_ids', endpoint='api_orders_sw6_get_open_order_ids')
def api_orders_sw6_get_open_order_ids():
    try:
        order_id_list = SW6OrderController().get_entity().get_api_order_ids_by_state()
        if order_id_list:
            return jsonify({'order_ids': order_id_list, 'status': 'success',
                            'message': f'{order_id_list.get("total")} offene Bestell-IDs erfolgreich abgerufen.'}), 200
        else:
            return jsonify({'order_ids': [], 'status': 'error', 'message': 'Keine offenen Bestell-IDs gefunden.'}), 404
    except Exception as e:
        # Hier könnten Sie den Fehler loggen
        return jsonify({'status': 'error', 'message': f'Fehler beim Abrufen offener Bestell-IDs: {e}'}), 500


# SW6->Bridge Create order
@BridgeOrderViews.route('/api/orders/sw6/sync_one_to_bridge/<sw6_order_id>',
                        endpoint="api_orders_sw6_sync_one_to_bridge", methods=["PATCH"])
def api_orders_sw6_sync_one_to_bridge(sw6_order_id):
    if not sw6_order_id:
        return jsonify({'message': "Es wurde keine SW6 Order Id angegeben", 'status': 'error'}), 400

    try:
        bridge_order_id = SW6OrderController().sync_one_to_bridge(sw6_entity_id=sw6_order_id)
        if bridge_order_id:
            bridge_order = BridgeOrderController().get_entity().query.get(bridge_order_id)
            return jsonify(
                {'message': f"Bestellung {bridge_order.get_order_number()} wurde angelegt/geändert", 'status': 'success'})
        else:
            return jsonify(
                {'message': f"Bestellung SW6 ID:{sw6_order_id} konnte nicht angelegt werden.", 'status': "error"}), 404
    except Exception as e:
        # Log the exception here
        return jsonify({'message': f'Beim Anlegen der Bestellung SW6 ID:{sw6_order_id} trat folgender Fehler auf: {e}',
                        'status': 'error'}), 500


# SW6 Get state by name
@BridgeOrderViews.route('/api/orders/sw6/get_to_state_machine_transition_by_name/<name>/<state_machine_id>',
                        methods=["GET"])
def api_orders_get_state_machine_state_by_name(name, state_machine_id):
    state_machine_state_list = SW6OrderController().get_entity().get_api_state_machine_state_by_(field="technicalName",
                                                                                                 value=name,
                                                                                                 state_machine_id=state_machine_id)

    if state_machine_state_list:
        result_list = SW6OrderController().get_entity().get_api_state_machine_transition_by_(
            state_machine_state_id=state_machine_state_list['data'][0]['id'], state_machine_id=state_machine_id)

        return jsonify({
            'status': 'success',
            'message': 'Verfügbare nachste Stati erfolgreich abgefragt.',
            'data': result_list['data']
        })


# SW6 Set order state
@BridgeOrderViews.route('/api/orders/sw6/order/<sw6_order_id>/state/<action_name>', methods=["PATCH"])
def api_orders_change_order_state(sw6_order_id, action_name):
    try:
        result = SW6OrderController().get_entity().patch_api_change_order_state(order_id=sw6_order_id, action_name=action_name)
        return jsonify({'message': f"Order state changed successfully for order ID: {sw6_order_id}", 'status': 'success',
                        'data': result})
    except Exception as e:
        # Log the exception here
        return jsonify({'message': f'Error changing order state for order ID: {sw6_order_id}: {e}', 'status': 'error'}), 500


# SW6 Set order_transaction state
@BridgeOrderViews.route('/api/orders/sw6/order_transaction/<sw6_order_id>/state/<action_name>', methods=["PATCH"])
def api_orders_change_order_transaction_state(sw6_order_id, action_name):
    try:
        result = SW6OrderController().get_entity().patch_api_change_order_transaction_state(order_id=sw6_order_id,
                                                                                   action_name=action_name)
        return jsonify({'message': f"Order transaction state changed successfully for order ID: {sw6_order_id}",
                        'status': 'success',
                        'data': result})
    except Exception as e:
        # Log the exception here
        return jsonify({'message': f'Error changing order transaction state for order ID: {sw6_order_id}: {e}',
                        'status': 'error'}), 500


# SW6 Set order_delivery state
@BridgeOrderViews.route('/api/orders/sw6/order_delivery/<sw6_order_id>/state/<action_name>', methods=["PATCH"])
def api_orders_change_order_delivery_state(sw6_order_id, action_name):
    try:
        result = SW6OrderController().get_entity().patch_api_change_order_delivery_state(order_id=sw6_order_id,
                                                                                action_name=action_name)
        return jsonify({'message': f"Order delivery state changed successfully for order ID: {sw6_order_id}",
                        'status': 'success',
                        'data': result})
    except Exception as e:
        # Log the exception here
        return jsonify({'message': f'Error changing order delivery state for order ID: {sw6_order_id}: {e}',
                        'status': 'error'}), 500


# Bridge Delete order
@BridgeOrderViews.route('/api/orders/bridge/order_delete/<bridge_order_id>/', methods=["DELETE"])
def api_orders_delete_order(bridge_order_id):
    try:
        result = BridgeOrderController().delete_order(bridge_order_id)
        if result:
            return jsonify({'message': f"Order {bridge_order_id} deleted successfully", 'status': 'success'})
        else:
            return jsonify(
                {'message': f"Failed to delete order {bridge_order_id}. Read the log.", 'status': 'error'}), 404
    except Exception as e:
        # Log the exception here
        return jsonify({'message': f'Error deleting order {bridge_order_id}: {e}', 'status': 'error'}), 500
