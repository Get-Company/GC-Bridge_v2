from pprint import pprint

from flask import Blueprint, request, jsonify
from src.modules.SW6.controller.SW6CustomerController import SW6CustomerController

from werkzeug.exceptions import BadRequest, NotFound

SW6CustomerViews = Blueprint('sw6_customer_views', __name__)

"""
API
"""


@SW6CustomerViews.route('/api/sw6/customers/update_erp_nr', methods=['PUT'])
def sw6_customer_update_erp_nr():
    data = request.json

    # Eingabedaten validieren
    customer_id = data.get('customer_id')
    new_customer_nr = data.get('new_customer_nr')
    if not customer_id or not new_customer_nr:
        return jsonify({'status': 'error', 'message': 'Kunden-ID und neue Kundennummer sind erforderlich'}), 400

    print(f"Neue Adrnr: {new_customer_nr} für id: {customer_id} in SW6")

    # Check for the new_customer_nr in SW6
    new_customer_nr_in_db = SW6CustomerController().get_entity().get_api_customer_by_customer_number(customer_nr=new_customer_nr)
    if new_customer_nr_in_db['total'] >= 1:
        return jsonify({'status': 'error', 'message': f'AdrNr. {new_customer_nr} gibt es bereits in SW6!'})

    sw6_customer = SW6CustomerController().get_entity().get_api_(id=customer_id)
    if sw6_customer:
        try:
            result = SW6CustomerController().get_entity().patch_customer_number_by_customer_id(
                customer_id=customer_id,
                new_customer_nr=new_customer_nr)

            if not result:
                return jsonify({'status': 'success', 'message': f'Neue AdrNr. {new_customer_nr} in SW6 gespeichert.'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'AdrNr konnte nicht in SW6 aktualisiert werden'}), 500
        except Exception as e:
            # Fehler loggen (serverseitig)
            print(f"Fehler beim Update der Kundennummer: {e}")
            return jsonify({'status': 'error', 'message': 'Interner Serverfehler beim Update der Kundennummer'}), 500
    else:
        return jsonify({'status': 'error', 'message': f'Kunde mit ID: {customer_id} in SW6 nicht gefunden!'}), 404