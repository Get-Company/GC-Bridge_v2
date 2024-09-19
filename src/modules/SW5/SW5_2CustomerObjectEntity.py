from pprint3x import pprint

from .SW5_2ObjectEntity import SW5_2ObjectEntity


class SW5_2CustomerObjectEntity(SW5_2ObjectEntity):
    def __init__(self):
        super().__init__()

    def get_customers(self):
        url = "/customers?limit=30000"
        response = self.get(url)
        return response

    def get_customer(self, customer_id, is_number_not_id=False):

        url = f"/customers/{customer_id}"
        if is_number_not_id:
            url += '?useNumberAsId=true'
        response = self.get(url)
        return response

    def get_customer_addresses_by_id(self, address_id):
        url = f"/addresses/{address_id}"
        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving address with ID '{address_id}': {e}")

    def get_all_customers_by_adrnr(self, adrnr):
        url = "/customers"
        url = url + f'?filter[number]={adrnr}'

        try:
            response = self.get(url)
            customer_list = []
            if response["success"]:
                for customer in response["data"]:
                    customer_detail = self.get_customer(customer_id=customer["id"])
                    if customer_detail["success"]:
                        customer_list.append(customer_detail["data"])
                    else:
                        return {"total": len(customer_list), "success": False, "data": customer_list}

            return {"total": len(customer_list), "success": True, "data": customer_list}
        except Exception as e:
            raise Exception(f"Error retrieving customers with same adrnr '{adrnr}': {e}")

    def get_all_customers_without_standard_addresses(self):
        url = "/customers?filter[0][property]=defaultBillingAddress&filter[0][expression]=NULL&filter[1][property]=defaultShippingAddress&filter[1][expression]=NULL&limit=20"

        try:
            response = self.get(url=url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving customers without standard addresses: {e}")

    def get_all_customers_by_email(self, email):
        url = "/customers"
        url = url + f'?filter[email]={email}'

        try:
            response = self.get(url)
            return response
        except Exception as e:
            raise Exception(f"Error retrieving customers with same email '{email}': {e}")

    def get_all_customers_orders_by_customer_id(self, customer_id):
        url = "/orders"
        url = url + f"?filter[customerId]={customer_id}"

        try:
            response = self.get(url)
            if response['success'] and response['total'] > 0:
                orders_details = []
                for order in response['data']:
                    order_details = self.get_order(order['id'])
                    if order_details:
                        orders_details.append(order_details)
                return orders_details
            else:
                print(response)
                return False
        except Exception as e:
            raise Exception(f"Error on retrieving order list for customer with ID '{customer_id}': {e}")

    def get_order(self, order_id):
        url = f"/orders/{order_id}"
        try:
            response = self.get(url)
            if response['success']:
                return response['data']
            else:
                print(response)
                return False
        except Exception as e:
            raise Exception(f"Error retrieving order with ID '{order_id}': {e}")

    def update(self, customer):
        url = f"/customers/{customer['id']}"
        response = self.put(url=url, data=customer)

        return response

    def delete_customer(self, customer_id):
        if not customer_id:
            return "No customer ID given"

        url = f"/customers/{customer_id}"
        try:
            response = self.delete(url)
            return response
        except Exception as e:
            raise Exception(f"Error on deleting the Customer: {customer_id}. Error: {e}")

    """
    ### 
    Addresses
    ###
    """

    def get_addresses(self, address_id):
        url = f"/addresses/{address_id}"
        try:
            response = self.get(url)
            return response['data']
        except Exception as e:
            raise Exception(f"Error retrieving address with ID '{address_id}': {e}")

    def set_customer_number_by_id(self, customer_id, number):
        url = '/customers/%s' % customer_id
        data = {
            'id': customer_id,
            'number': number
        }
        try:
            response = self.put('/customers/%s' % customer_id, data)['data']
            return response
        except Exception as e:
            raise Exception(f"Error on updating Adrnr: {number} on Customer_ID: {customer_id}: {e}")
