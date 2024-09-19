"""
A basic Shopware 5 API client I threw together for a project. There's a few gotchas in here that
I thought are useful enough to others to publish it. But please take it as is - it works for my
purpose (processing Shopware articles daily), I make no claims beyond that.
"""

import logging
import os
import datetime

import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPDigestAuth
from urllib3 import Retry

from SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity

logger = logging.getLogger(__name__)

# This is a Shopware constant
ROOT_ID = 3


class ShopwareAPIError(Exception):
    pass


def client_from_env():
    """
    Returns an APIClient instance constructed from settings in the environment variables.
    """
    api_credentials = 'geco_bot:gpTCCXGurNt2JTnw0FDqXTLl0yMuh41hl18SVq3I'
    api_base_url = "https://www.classei-shop.com/api"
    # api_base_url = "https://develop.classei-shop.com/api"
    if not api_credentials or not api_base_url:
        raise ValueError(
            'You need to set SHOPWARE_API_CREDENTIALS to the format username:password and '
            'SHOPWARE_API_URL to the base API URL.')
    return APIClient(api_base_url, *api_credentials.split(':', 1))


class APIClient:
    """
    Basic API client that handles some retries, but not much more.

    TODO: You can filter queries by using e.g.
    client.get('/articles?filter[0][property]=mainDetail.number&filter[0][value]=1000-%25'
    See https://developers.shopware.com/developers-guide/rest-api/#filter,-sort,-limit,-offset
    """

    def __init__(self, base_url, username, token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(username, token)
        # Set up automatic retries on certain HTTP codes
        retry = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _make_request(self, method, url, payload=None):
        response = self.session.request(method, self.base_url + url, json=payload)
        try:
            json_response = response.json()
        except ValueError:
            raise ShopwareAPIError('Received no JSON as response. Response: %s' % response)
        else:
            if not json_response['success']:
                raise ShopwareAPIError('Shopware indicated a failure: %s' % json_response)
            return json_response

    def get(self, url):
        return self._make_request('get', url)

    def post(self, url, data):
        return self._make_request('post', url, payload=data)

    def put(self, url, data):
        return self._make_request('put', url, payload=data)

    def delete(self, url, data=None):
        return self._make_request('delete', url, data)

    # Address
    def get_addresses_by_id(self, id):
        """
        Function to get customer_address addresses by Address ID
        :param id:
        :return:
        """
        print('get Address from id: %s' % id)
        url = '/addresses/%s' % id

        return self.get(url)['data']

    def get_address_by_userId(self, userId):
        """
        Function to get a customer_address addresses by WebshopId
        :param userId:
        :return:
        """
        filter = '?filter[user_id]=%s' % userId
        url = '/addresses' + filter

        return self.get(url)['data']

    def set_address_by_id(self, address_id, user_id):
        print('Update Address: %s to Customer: %s' % (address_id, user_id))
        data = {
            'customer_address': int(user_id)
        }

        return self.put('/addresses/%s' % address_id, data)['data']

    # Customer
    def get_customer(self, customer_id, is_number_not_id=False):
        url = '/customers/%s' % customer_id
        if is_number_not_id:
            url = url + '?useNumberAsId=true'

        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise e

    def set_customer_credentials_by_customerId(self,
                                               customerId: int,
                                               password: str,
                                               encoder_name: str,
                                               last_login,
                                               email: str):
        """
        Set all fields necessary for the customer_address. If the password changes there is a chance that the email is also
        wrong - so lets set it. The last_login is a date object, which needs to be converted into a string:
        2022-05-05T16:36:46+0200 -> "%Y-%m-%dT%H:%M:%S+%f"
        (https://www.programiz.com/python-programming/datetime/strptime)
        :param customerId: int WebshopID
        :param password: string Password Hash
        :param encoder_name: string Encoder Name
        :param last_login: date
        :param email:
        :return: SW5 Customer Data
        """
        # Check if last_login is not datetime. Convert if needed
        if type(last_login) is datetime.datetime:
            last_login = last_login.strftime("%Y-%m-%dT%H:%M:%S")

        url = '/customers/%s' % customerId
        data = {
            'hashPassword': password,
            'encoderName': encoder_name,
            'lastLogin': last_login,
            'email': email
        }
        return self.put(url, data)['data']

    def set_customer_addresses_orders_and_credentials(self, customer: SW5CustomerEntity):
        # 1. Customer
        # Todo: The  email could be already in the db. Following code wont run, bc SW detects duplicate emails. So we need to changes the wrong duplicate emails in a for loop
        # Get all customers by email but not with the right_id. Replace email with new one, use credentials from  return
        duplicate_customers = self.get_customer_filter_by_email_and_not_like_id(customer.get_webshopid(),
                                                                                customer.get_email())
        for index, duplicate_customer in enumerate(duplicate_customers):
            new_email = str(index) + duplicate_customer['email']
            self.set_customer_credentials_by_customerId(
                customerId=duplicate_customer['id'],
                password=duplicate_customer['hashPassword'],
                encoder_name=duplicate_customer['encoderName'],
                last_login=duplicate_customer['lastLogin'],
                email=new_email
            )
            new_email = None

        # 2 Addresses
        if customer.get_addresses_ids():
            for address_id in customer.get_addresses_ids():
                self.set_address_by_id(address_id, customer.get_webshopid())
        # 3. Orders
        if customer.get_orders_ids():
            for order_id in customer.get_orders_ids():
                self.set_order_customerId_by_orderId(customer.get_webshopid(), order_id)
        print("Set Ad, Ord, Cre", customer)

        # 4. Credentials
        updated_customer = self.set_customer_credentials_by_customerId(
            customerId=customer.get_webshopid(),
            password=customer.get_password_hash(),
            encoder_name=customer.get_password_encoder(),
            last_login=customer.get_last_login(),
            email=customer.get_email()
        )

        self.set_customer_adrnr_by_Id(customer.get_webshopid(), customer.get_adrnr())
        return updated_customer

    def set_customer_adrnr_by_Id(self, customerId, adrnr):
        data = {
            'number': adrnr
            # SW5 Api calls it number, db calls it customernumber and backend calls it Kundennummer.Momahdu, NaPataMahDu, JadaPataMahda, NaMahddaMoa
        }

        return self.put('/customers/%s' % customerId, data)['data']

    def get_customer_filter_by_email_and_not_like_id(self, id, email):
        """
        Get all customer_address by email but not with the id
        :return:
        """
        url = '/customers?'
        email_filter = 'filter[0][property]=email&filter[0][value]=%s' % email
        id_filter = '&filter[1][property]=id&filter[1][expression]=!=&filter[1][value]=%s' % id

        return self.get(url + email_filter + id_filter)['data']

    def delete_customer_by_customerId(self, customerId):
        url = '/customers/%s' % customerId

        return self.delete(url)

    # Orders
    def get_orders_by_customerId(self, customerId):
        filter = '?filter[customerId]=%s' % customerId
        url = '/orders' + filter

        return self.get(url)['data']

    def set_orders_customerId_by_orderId(self, customerId, orderId):
        print('Update Order %s to Customer: %s' % (orderId, customerId))
        if type(customerId) is not int:
            customerId = int(customerId)
        data = {
            'customerId': customerId
        }
        return self.put('/orders/%s' % orderId, data)['data']

    # Articles
    def get_article(self, article_id, is_number_not_id=False):
        url = '/articles/%s' % article_id
        if is_number_not_id:
            url = url + '?useNumberAsId=true'
        return self.get(url)['data']

    def get_variant(self, article_id, is_number_not_id=False):
        url = '/variants/%s' % article_id
        if is_number_not_id:
            url = url + '?useNumberAsId=true'
        return self.get(url)['data']

    def get_articles(self):
        limit = 100000
        response = self.get('/articles?limit=%s' % limit)
        if response['total'] >= limit:
            # Sorry for being lazy. Use the start= query kwarg for pagination.
            # https://forum.shopware.com/discussion/10484/geloest-mehr-als-1000-artikel-mit-rest-api-laden
            raise ValueError(
                'You have more than %s articles. You need to implement pagination in the '
                'get_articles method.')
        return response['data']

    def delete_article(self, article_id):
        return self.delete('/articles/%s' % article_id)

    def create_article(self, *args, **kwargs):
        if 'article_id' in kwargs:
            raise TypeError('article_id must not be included')
        return self._update_or_create_article(*args, **kwargs)

    def update_article(self, article_id, *args, **kwargs):
        kwargs['article_id'] = article_id
        return self._update_or_create_article(*args, **kwargs)

    def _update_or_create_article(
            self, description, sku, price, category_ids, supplier, name=None,
            image_urls=None, active=None, tax=19, num_in_stock=1, purchase_price=None,
            article_id=None, price_group_id=None, last_stock=False, supplier_sku=None,
            shipping_time_days=None, attributes=None):
        """
        Updates if article ID is given, creates otherwise.
        """
        categories = [{'id': category_id} for category_id in category_ids]
        data = {
            'tax': tax,
            'descriptionLong': description,
            'lastStock': last_stock,  # "Abverkauf"
            'mainDetail': {
                'number': sku,  # "Artikelnummer"
                'inStock': num_in_stock,
                'prices': [
                    {
                        'price': price,
                    }
                ],
                'purchasePrice': purchase_price or '0',
            },
            'categories': categories,
            'supplier': supplier,
        }
        if name is None:
            if not article_id:
                raise ValueError("A product name is needed when creating.")
        else:
            data['name'] = name
        if active is not None:
            # No idea why we need to double this, but we do. A kingdom for good API docs.
            data['active'] = data['mainDetail']['active'] = active
        if image_urls:
            # http://forum.shopware.com/discussion/8497/rest-api-artikelbilder-setzen
            data['images'] = [{'link': url} for url in image_urls]
        if price_group_id is not None:
            data['priceGroupActive'] = True
            data['priceGroupId'] = price_group_id
        if supplier_sku is not None:
            # "Herstellernummer"
            data['mainDetail']['supplierNumber'] = supplier_sku
        if shipping_time_days:
            data['mainDetail']['shippingTime'] = shipping_time_days
        # Keys are 'attr[1..20]' E.g. attributes={'attr4': '25%'} for Mirko's discount field.
        if attributes is not None:
            data['mainDetail']['attribute'] = attributes
        if article_id:
            # Updating
            response = self.put('/articles/%s' % article_id, data)
        else:
            # Creating
            response = self.post('/articles', data)
        if 'data' in response and 'id' in response['data']:
            return response['data']['id']
        else:
            try:
                raise ShopwareAPIError(
                    'Unexpected response format. Request was %s, article_id: %s' % (
                        data, article_id or 'Create'))
            except ShopwareAPIError:
                # TEMPORARY: Ensure this gets to Sentry
                from raven.transport import TwistedHTTPTransport
                from raven import Client
                client = Client(dsn=settings.RAVEN_CONFIG['dsn'])
                client.captureException()
                raise

    def update_stock_level(self, article_id, num_in_stock):
        """
        Update article stock level. Does not work for variants, will just update main variant
        """
        data = {'mainDetail': {'inStock': int(num_in_stock)}}
        return self.put('/articles/%s' % article_id, data)['data']

    def update_variant_stock_level(self, variant_id, num_in_stock):
        """
        Updates stock level for variant. Seems to also work for non-variant products.
        """
        data = {'inStock': int(num_in_stock)}
        return self.put('/variants/%s' % variant_id, data)['data']

    def clear_images(self, article_id):
        data = {'images': []}
        return self.put('/articles/%s' % article_id, data)['data']

    def delete_all_articles(self):
        articles = self.get_articles()
        for article in articles:
            self.delete_article(article['id'])
        return articles

    # Categories

    def get_categories(self):
        """
        Returns the tree of categories.
        :return:
        """
        limit = 100000
        response = self.get('/categories?limit=%s' % limit)
        if response['total'] >= limit:
            # Sorry for being lazy. Use the start= query kwarg for pagination.
            # https://forum.shopware.com/discussion/10484/geloest-mehr-als-1000-artikel-mit-rest-api-laden
            raise ValueError(
                'You have more than %s categories. You need to implement pagination in the '
                'get_categories method.')
        return response['data']

    def get_category(self, category_id):
        return self.get('/categories/%s' % category_id)['data']

    def find_category_ids(self, name, parent_id=None):
        """
        Returns all categories matching the name. Optionally also matches on parent_id. If not
        given, all name matches are returned.
        """
        matches = []
        categories = self.get_categories()
        for category in categories:
            if category['name'] == name:
                if parent_id is None or category['parentId'] == parent_id:
                    matches.append(category['id'])
        return matches

    def create_category(self, name, parent_id):
        """
        Creates a category. Use ROOT_ID for parent_id if creating a root category.
        """
        created = self.post('/categories', {
            'name': name,
            'parentId': parent_id,
        })
        return created['data']['id']

    def get_or_create_category(self, name, parent_id):
        """
        Returns category ID of category with supplied name. Created if necessary.
        """
        matches = self.find_category_ids(name, parent_id)
        if len(matches) > 1:
            raise ValueError(
                "There are %s categories with name '%s' (parent: %s), expected only 1 or less." %
                (len(matches), name, parent_id)
            )
        elif len(matches) == 1:
            return matches[0]
        else:
            logger.info('Creating category %s (parent: %s)' % (name, parent_id))
            self.create_category(name, parent_id)

    def update_category_title(self, category_id, new_title):
        return self.put('/categories/%s' % category_id, {'name': new_title})

    def delete_category(self, category_id):
        return self.delete('/categories/%s' % category_id)

    # Misc

    def get_customer_groups(self):
        # TODO: Check for limit
        return self.get('/customerGroups')['data']
