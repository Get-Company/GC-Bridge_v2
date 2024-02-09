from datetime import datetime, timedelta
from pprint import pprint

import config
from src.modules.ModulesCoreController import ModulesCoreController

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from src.modules.Bridge.controller.BridgeOrderController import BridgeOrderController
from src.modules.SW6.controller.SW6OrderController import SW6OrderController

BridgeOrderViews = Blueprint('bridge_order_views', __name__)


@BridgeOrderViews.route('/orders', endpoint='orders')
def bridge_show_orders():
    # Abfragen der Start- und Enddaten aus der URL (beide Parameter sind optional)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Abrufen der Bestellungen mit optionalen Filtern
    orders, start_date_obj, end_date_obj = BridgeOrderController().get_orders_by_date(start_date=start_date, end_date=end_date)

    today = datetime.today()
    filter_end_date = today

    yesterday = today - timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    filter_start_date = yesterday

    if start_date_obj:
        filter_start_date = start_date_obj
    if end_date_obj:
        filter_end_date = end_date_obj

    return render_template('bridge/order/orders.html',
                           orders=orders,
                           filter_start_date=filter_start_date,
                           filter_end_date=filter_end_date,
                           today=today,
                           yesterday=yesterday,
                           order_state_machine_id=config.SW6Config.ORDER_STATE_MACHINE,
                           payment_state_machine_id=config.SW6Config.PAYMENT_STATE_MACHINE,
                           shipping_state_machine_id=config.SW6Config.SHIPPING_STATE_MACHINE
                           )

@BridgeOrderViews.route('/bridge/orders/change_states', endpoint='change_states', methods=['POST'])
def bridge_orders_change_states():
    # Sicherstellen, dass es sich um eine POST-Anfrage handelt.
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        order_state_technicalName = request.form.get('order_state')
        payment_state_technicalName = request.form.get('payment_state')
        shipping_state_technicalName = request.form.get('shipping_state')

        print(f"Updating Order to: {order_state_technicalName} for order ID {order_id} ")
        print(f"Updating Payment to: {payment_state_technicalName} for order ID {order_id} ")
        print(f"Updating Shipping to: {shipping_state_technicalName} for order ID {order_id} ")

    return redirect(url_for('bridge_order_views.orders'))


"""
API
"""


@BridgeOrderViews.route('/api/orders/sw6/get_open_order_ids', endpoint='api_orders_sw6_get_open_order_ids')
def api_orders_sw6_get_open_order_ids():
    try:
        order_id_list = SW6OrderController().get_entity().get_api_order_ids_by_state()
        if order_id_list:
            return jsonify({'order_ids': order_id_list, 'status': 'success', 'message': f'{order_id_list.get("total")} offene Bestell-IDs erfolgreich abgerufen.'}), 200
        else:
            return jsonify({'order_ids': [], 'status': 'error', 'message': 'Keine offenen Bestell-IDs gefunden.'}), 404
    except Exception as e:
        # Hier könnten Sie den Fehler loggen
        return jsonify({'status': 'error', 'message': f'Fehler beim Abrufen offener Bestell-IDs: {e}'}), 500


@BridgeOrderViews.route('/api/orders/sw6/sync_one_to_bridge/<sw6_order_id>', endpoint="api_orders_sw6_sync_one_to_bridge")
def api_orders_sw6_sync_one_to_bridge(sw6_order_id):
    if not sw6_order_id:
        return jsonify({'message': "Es wurde keine SW6 Order Id angegeben", 'status': 'error'}), 400

    try:
        bridge_order_id = SW6OrderController().sync_one_to_bridge(sw6_entity_id=sw6_order_id)
        if bridge_order_id:
            bridge_order = BridgeOrderController().get_entity().query.get(bridge_order_id)
            return jsonify({'message': f"Bestellung {bridge_order.get_order_number()} wurde angelegt", 'status': 'success'})
        else:
            return jsonify({'message': f"Bestellung SW6 ID:{sw6_order_id} konnte nicht angelegt werden.", 'status': "error"}), 404
    except Exception as e:
        # Log the exception here
        return jsonify({'message': f'Beim Anlegen der Bestellung SW6 ID:{sw6_order_id} trat folgender Fehler auf: {e}', 'status': 'error'}), 500


@BridgeOrderViews.route('/api/orders/sw6/get_to_state_machine_transition_by_name/<name>/<state_machine_id>', methods=["GET"])
def api_orders_get_state_machine_state_by_name(name, state_machine_id):
    state_machine_state_list = SW6OrderController().get_entity().get_api_state_machine_state_by_(field="technicalName", value=name, state_machine_id=state_machine_id)

    if state_machine_state_list:
        result_list = SW6OrderController().get_entity().get_api_state_machine_transition_by_(state_machine_state_id=state_machine_state_list['data'][0]['id'], state_machine_id=state_machine_id)

        return jsonify({
            'status': 'success',
            'message': 'Verfügbare nachste Stati erfolgreich abgefragt.',
            'data': result_list['data']
        })

