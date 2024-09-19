import json
from pprint import pprint

from flask import Blueprint, render_template, request, abort, redirect, url_for, jsonify, make_response
import os

from jinja2 import FileSystemLoader, Environment, select_autoescape

from ..controller.MailController import MailController
from src.modules.Bridge.entities.BridgeProductEntity import BridgeProductEntity

from config import JinjaConfig

MailViews = Blueprint('mail_views', __name__)


@MailViews.route('/mail/new', methods=['GET', 'POST'], endpoint='new')
def mail_new():
    template_dir = 'src/templates/mail/templates/'
    mjml_files = [f for f in os.listdir(template_dir) if f.endswith('.mjml')]

    return render_template('mail/mail_new.html', mjml_templates=mjml_files)


"""
API
"""


@MailViews.route('/api/mail/render_template', methods=['POST'])
def render_mail_template():
    # Collect JSON data from the POST request
    data = json.loads(request.data)

    # Extract selected template and product IDS from the received data
    selected_template = data.get('selectedTemplate')
    products = data.get('products')

    # Query db for route_product_entities
    product_entities = []
    for product in products:
        product_entity = BridgeProductEntity.query.get(product['id'])
        if product_entity:
            product_entities.append(product_entity)

    # Load the MJML template using FileSystemLoader
    env = Environment(
        loader=FileSystemLoader('src/templates/mail/templates'),
    )
    env.filters['currency_format'] = JinjaConfig.currency_format

    mjml_template = env.get_template(f'{selected_template}')

    # Render the template with the product_entities
    rendered_jinja_template = mjml_template.render(products=product_entities)

    mail_controller = MailController()
    api_response = mail_controller.render_mjml_to_html(mjml=rendered_jinja_template)

    # Handled the JSON response from the API according to the returned status code:
    if 'html' in api_response:
        # For success response, 200 status code is returned along with the response data
        return jsonify(api_response), 200
    elif 'message' in api_response:
        # For error responses, we check the presence of 'message' in the response,
        # then an appropriate HTTP status code is chosen according to their respective
        # error messages along with the response data.
        if 'Bad Request' in api_response['message']:
            return make_response(jsonify(api_response), 400)
        elif 'Unauthorized' in api_response['message']:
            return make_response(jsonify(api_response), 401)
        elif 'Forbidden' in api_response['message']:
            return make_response(jsonify(api_response), 403)
        elif 'Internal Server Error' in api_response['message']:
            return make_response(jsonify(api_response), 500)
