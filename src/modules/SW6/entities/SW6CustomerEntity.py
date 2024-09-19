import time
import uuid
from datetime import datetime
from pprint import pprint


from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity
from lib_shopware6_api_base import Criteria, EqualsFilter
from src.modules.SW5.SW5_2CustomerObjectEntity import SW5_2CustomerObjectEntity


class SW6CustomerEntity(SW6AbstractEntity):

    def __init__(self):
        self._endpoint_name = 'customer'
        super().__init__(endpoint_name=self._endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        # Check if sw6_json_data is None or not a dictionary
        if sw6_json_data is None or not isinstance(sw6_json_data, dict):
            self.logger.error("Invalid data passed to map_sw6_to_bridge: sw6_json_data is None or not a dictionary")
            return None
        try:
            bridge_customer_entity_new = BridgeCustomerEntity(
                email=self.get_email(sw6_json_data),
                erp_nr=self.get_customer_nr(sw6_json_data),
                vat_id=self.get_vat_id(sw6_json_data),
                created_at=datetime.now(),
                edited_at=datetime.now()
            )
            return bridge_customer_entity_new
        except Exception as e:
            self.logger.error(
                f"SW6 {sw6_json_data['customerNumber']} Customer could not be mapped to BridgeCustomerEntity: {e}")

    def map_bridge_to_sw6(self, bridge_entity):
        # Todo: Is it neccessary to update the customer to sw6?
        pass

    def get_api_customer_address_details_by_customer_id(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations["defaultShippingAddress"] = Criteria()
        payload.associations["defaultBillingAddress"] = Criteria()

        payload.associations["addresses"] = Criteria()

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

    def get_api_customer_by_customer_number(self, customer_nr):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='customerNumber', value=customer_nr))

        result = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return result

    def get_api_customer_by_email(self, email):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='email', value=email))
        result = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return result

    def get_customer_nr(self, sw6_json_data):
        try:
            return sw6_json_data['customerNumber']
        except Exception as e:
            self.logger.error(f"Error retrieving customer number: {e}")
            return None

    def get_email(self, sw6_json_data):
        try:
            return sw6_json_data['email']
        except Exception as e:
            self.logger.error(f"Error retrieving email: {e}")
            return None

    def get_vat_id(self, sw6_json_data):
        try:
            vat_ids = sw6_json_data.get('vatIds')
            if vat_ids and isinstance(vat_ids, list) and len(vat_ids) > 0:
                return vat_ids[0]
            else:

                return None
        except Exception as e:
            self.logger.error(f"Error Customer:{sw6_json_data.get('customerNumber')} retrieving VAT ID: {e}")
            return None

    def get_group_id(self, bridge_entity):
        business_type = 'B2B' if bridge_entity.get_vat_id() else 'B2C'
        return self.config_sw6.CUSTOMER_GROUPS.get(())

    def patch_api_change_customer_nr(self, customer_id, new_customer_nr):
        print("Patching")
        if not new_customer_nr and not customer_id:
            self.logger.error("Ein 'customer_id' oder 'customer_nr' muss angegeben werden.")
            return

        customer_in_sw6 = self.get_api_(id=customer_id)
        if customer_in_sw6:
            payload = {'customerNumber': new_customer_nr}
            endpoint = self.sw6_client.request_patch(f"/{self._endpoint_name}/{customer_id}", payload=payload)
            return endpoint
        else:
            self.logger.error(f"Customer with id: {customer_id} not found. Could not patch 'customerNumber' to {new_customer_nr}.")

    def patch_customer_number_by_customer_id(self, customer_id, new_customer_nr):
        payload = {'customerNumber': new_customer_nr}
        result = self.sw6_client.request_patch(f"/{self._endpoint_name}/{customer_id}", payload=payload)
        return result

    """    SW5 Migration    """

    def sw5_get_customers_list(self):
        sw5_customer_entity = SW5_2CustomerObjectEntity()
        sw5_customers_list = sw5_customer_entity.get_customers()
        print(sw5_customers_list['total'], ":", len(sw5_customers_list['data']))
        customers_index = 18158

        # Customer with many addresses Roth
        # customer = sw5_customer_entity.get_customer('36415', True)

        # Customer CH
        # customer = sw5_customer_entity.get_customer('10496', True)

        # Customer IT
        # customer = sw5_customer_entity.get_customer('26647')
        # result = self.sw5_upsert_customer_to_sw6(customer['data'], 1, 1)
        # pprint(result)

        while True:
            try:
                customer = sw5_customers_list['data'][customers_index]
                customer_details = sw5_customer_entity.get_customer(customer_id=customer['id'])
                if customer_details and customer_details['success']:
                    customer_upserted = self.sw5_upsert_customer_to_sw6(
                        sw5_customer_data=customer_details['data'],
                        customers_index=customers_index,
                        customers_length=sw5_customers_list['total']
                    )
                    if customer_upserted:
                        print("Done!")
                    else:
                        print("Some error occured")
                else:
                    print("Error on Customer:")
                    pprint(customer_details)
            except Exception as e:
                self.logger.error(
                    f"An error occurred with customer id: {sw5_customers_list['data'][customers_index]['id']} and number: {sw5_customers_list['data'][customers_index]['number']}. The error is {e}")
                continue
            finally:
                customers_index += 1
                if customers_index >= sw5_customers_list['total']:
                    print("Done")
                    break

    def sw5_upsert_customer_to_sw6(self, sw5_customer_data, customers_index, customers_length):
        is_sw5_customer_in_sw6 = self.get_api_customer_by_email(sw5_customer_data['email'])

        if is_sw5_customer_in_sw6['total'] == 0:
            sw5_customer_entity = SW5_2CustomerObjectEntity()
            sw5_customer_details = sw5_customer_entity.get_customer(sw5_customer_data['id'])

            print(f"Sync {customers_index}/{customers_length} "
                  f"{sw5_customer_data['defaultBillingAddress']['firstname']} "
                  f"{sw5_customer_data['defaultBillingAddress']['lastname']} "
                  f"| ID:{sw5_customer_data['id']} - AdrNr:{sw5_customer_data['number']} ",
                  datetime.now().strftime('%H:%M:%S %d.%m.%Y'))

            sw6_customer_data = self.sw5_map_sw5_to_sw6(sw5_customer_details["data"])
            if sw6_customer_data:
                response = self.bulk_uploads(sw6_json_data=sw6_customer_data)
                return response
            else:
                print("\033[31mSkip, no Customer Data\033[0m")
                return None
            # pprint(response)

            # sw5_customer_orders = sw5_customer_entity.get_all_customers_orders_by_customer_id(sw5_customer_data['id'])
            # if sw5_customer_orders:
            #     for order in sw5_customer_orders:
            #         sw6_order_data = self.sw5_map_order_sw5_to_sw6(sw5_order_data=order, sw6_customer_data=sw6_customer_data)
            #         pprint(sw6_order_data)
            #         response = self.bulk_uploads(sw6_json_data=sw6_order_data, endpoint_name="order")
            #         pprint(response)

            # return True
        else:
            print(f"Customer {sw5_customer_data['id']}:{sw5_customer_data['number']} already exists. Skip!")
            return False

    def sw5_map_sw5_to_sw6(self, sw5_customer_data):
        sw6_customer_data = {
            "customerNumber": sw5_customer_data['number'],
            "vatIds": [sw5_customer_data['defaultBillingAddress']['vatId']]
        }
        sw6_customer_data.update(self.sw5_get_customer_group_id(sw5_customer_data))
        sw6_customer_data.update(self.sw5_get_payment_id(sw5_customer_data))
        sw6_customer_data.update(self.sw5_get_sales_channel_id(sw5_customer_data))
        sw6_customer_data.update(self.sw5_get_language_id(sw5_customer_data))

        if self.sw5_get_adresses(sw5_customer_data):
            sw6_customer_data.update(self.sw5_get_adresses(sw5_customer_data))
        else:
            print("\033[31mError on Adresses\033[0m")
            return None

        sw6_customer_data.update(self.sw5_get_credentials(sw5_customer_data))

        return sw6_customer_data

    def sw5_get_customer_group_id(self, sw5_customer_data):
        groupKey = sw5_customer_data['groupKey']
        groupKey_map = {
            "Vk1": ('DE', False),
            "CHB2B": ('CH', False),
            "CHB2C": ('CH', True),
            "IT_de": ('IT', False),
            "IT_it": ('IT', False)
        }

        # If the groupKey is not in the groupKey_map, it will default to ('DE', True)
        country_vat_pair = groupKey_map.get(groupKey, ('DE', True))

        return {"groupId": self.config_sw6.CUSTOMER_GROUPS[country_vat_pair]}

    def sw5_get_payment_id(self, sw5_customer_data):
        paymentId = sw5_customer_data['paymentId']
        payment_map = {
            4: 'invoice',
            9: 'invoice',
            5: 'advance',
            10: 'advance',
            11: 'advance',
            7: 'paypal'
        }

        payment_method_key = payment_map.get(paymentId, 'advance')
        return {"defaultPaymentMethodId": self.config_sw6.PAYMENT_METHODS[payment_method_key]}

    def sw5_get_sales_channel_id(self, sw5_shop_data):
        shopId = sw5_shop_data['shopId']  # Getting ShopId from the data of Shopware 5
        shop_map = {
            1: 'DE',
            2: 'CH',
            4: 'IT',
            5: 'IT'
        }

        sales_channel_key = shop_map.get(shopId, 'DE')  # Defaulting to 'DE' if the ShopId is not found
        payload = {
            "salesChannelId": self.config_sw6.SALES_CHANNELS[sales_channel_key]['id'],
            "boundSalesChannelId": self.config_sw6.SALES_CHANNELS[sales_channel_key]['id']
        }
        return payload

    def sw5_get_language_id(self, sw5_language_data):
        languageId = sw5_language_data['languageId']  # Getting languageId from the data of Shopware 5
        language_map = {
            2: 'DE',
            4: 'DE',
            5: 'IT',
            3: 'EN'
        }

        language_key = language_map.get(languageId, 'DE')  # Defaulting to 'EN' if the languageId is not found
        return {"languageId": self.config_sw6.LANGUAGE[language_key]}

    def sw5_get_adresses(self, sw5_customer_data):
        defaultCustomerId = uuid.uuid4().hex
        defaultBillingAddressId = uuid.uuid4().hex
        defaultShippingAddressId = uuid.uuid4().hex

        countryBillingAddress = self.get_api_country_details_by_iso3(
            sw5_customer_data['defaultBillingAddress']['country']['iso3'])

        countryShippingAddress = self.get_api_country_details_by_iso3(
            sw5_customer_data["defaultShippingAddress"]["country"]["iso3"]
        )

        payload = {
            "id": defaultCustomerId,
            # "defaultBillingAddressId": defaultBillingAddressId,
            "defaultBillingAddress": {
                "id": defaultBillingAddressId,
                "customerId": defaultCustomerId,
                "countryId": countryBillingAddress['data'][0]['id'],
            },
            # "defaultShippingAddressId": defaultShippingAddressId,
            "defaultShippingAddress": {
                "id": defaultShippingAddressId,
                "customerId": defaultCustomerId,
                "countryId": countryShippingAddress['data'][0]['id'],
            },
            'addresses': []
        }

        if self._check_address_fields(sw5_customer_data['defaultBillingAddress']):
            payload.update(self._sw5_set_address_fields(sw5_customer_data['defaultBillingAddress']))
            payload["defaultBillingAddress"].update(
                self._sw5_set_address_fields(sw5_customer_data['defaultBillingAddress']))
        else:
            print("\033[31mError on default billing address\033[0m")
            return None

        if self._check_address_fields(sw5_customer_data['defaultShippingAddress']):
            payload["defaultShippingAddress"].update(
                self._sw5_set_address_fields(sw5_customer_data['defaultShippingAddress']))
        else:
            print("\033[31mError on default shipping address\033[0m")
            return None

        for adresses_index, address in enumerate(sw5_customer_data['addresses']):
            if not address['id'] == sw5_customer_data['defaultBillingAddress']['id'] and not address['id'] == \
                                                                                             sw5_customer_data[
                                                                                                 'defaultShippingAddress'][
                                                                                                 'id']:
                # A Check if every required field is set and some other checks
                if self._check_address_fields(address):
                    print(f"Address {adresses_index}/{len(sw5_customer_data['addresses'])}")
                    addressId = uuid.uuid4().hex
                    countryIso3 = self._sw5_get_country_iso3(address['countryId'])
                    countryAddress = self.get_api_country_details_by_iso3(countryIso3)
                    payload["addresses"].append({
                        "id": addressId,
                        "customerId": defaultCustomerId,
                        "countryId": countryAddress['data'][0]['id'],
                        **self._sw5_set_address_fields(address),
                    })
        return payload

    def _check_address_fields(self, sw5_address_data):
        if not sw5_address_data['firstname'] or len(sw5_address_data['firstname']) < 3:
            print(f"Skip address. first name = {sw5_address_data['firstname']}")
            return False
        # Überprüfen Sie den 'lastname', nicht den 'firstname'
        if not sw5_address_data['lastname'] or len(sw5_address_data['lastname']) < 3:
            print(f"Skip address. last name = {sw5_address_data['lastname']}")
            return False
        if 'street' not in sw5_address_data or not sw5_address_data['street'] or len(sw5_address_data['street']) < 3:
            print(f"Skip address. street = {sw5_address_data.get('street')}")
            return False

        else:
            return True

    def _sw5_set_address_fields(self, sw5_address_data):
        return {
            "salutationId": self._sw5_get_salutation(sw5_address_data['salutation']),
            "firstName": sw5_address_data['firstname'],
            "lastName": sw5_address_data['lastname'],
            "zipcode": sw5_address_data['zipcode'],
            "city": sw5_address_data['city'],
            "company": sw5_address_data['company'],
            "street": sw5_address_data['street'],
            "department": sw5_address_data['department'],
            "title": sw5_address_data['title'],
            "phoneNumber": sw5_address_data['phone'],
        }

    def _sw5_get_salutation(self, salutation):
        salutationId = self.config_sw6.SALUTATION.get(salutation, 'mr')
        return salutationId

    def _sw5_get_country_iso3(self, country_id):
        country_map = {
            2: 'DEU',
            5: 'BEL',
            7: 'DNK',
            8: 'FIN',
            9: 'FRA',
            11: 'GBR',
            12: 'IRL',
            14: 'ITA',
            18: 'LUX',
            21: 'NLD',
            23: 'AUT',
            25: 'SWE',
            27: 'ESP',
            30: 'POL',
            31: 'HUN',
            33: 'CZE',
            34: 'SVK',
            35: 'ROU',
            41: 'CHE',
            170: 'MCO',
            180: 'NZL'
        }
        return country_map.get(country_id, 'N/A')  # Returning 'N/A' if the country id is not found

    def sw5_get_credentials(self, sw5_customer_data):
        encoder_name = sw5_customer_data['encoderName']
        hash_password = sw5_customer_data['hashPassword']
        payload = {
            "email": sw5_customer_data['email'],
            "firstLogin": sw5_customer_data['firstLogin'],
            "lastLogin": sw5_customer_data['lastLogin'],
            "createdAt": sw5_customer_data['firstLogin'],
            "updatedAt": sw5_customer_data['changed'],
        }
        if encoder_name == "bcrypt":
            payload.update({
                "password": hash_password
            })
            return payload
        elif encoder_name == "md5":
            payload.update({
                "legacyPassword": hash_password,
                "legacyEncoder": "Md5"
            })
            return payload
        else:
            print(f"Error: Invalid encoderName {encoder_name}")
        return False

    def sw5_map_order_sw5_to_sw6(self, sw5_order_data, sw6_customer_data):
        # pprint(sw6_customer_data)
        # pprint(sw5_order_data)

        sw6_order_data = {
            "billingAddressId": sw6_customer_data['defaultBillingAddress']['id'],
            "currencyId": self.config_sw6.CURRENCY[sw5_order_data["currency"]],
            "languageId": sw6_customer_data["languageId"],
            "salesChannelId": sw6_customer_data["salesChannelId"],
            "orderDateTime": sw5_order_data["orderTime"],
            "orderCustomer": {
                "customerId": sw6_customer_data['defaultBillingAddress']['id'],
                "salutationId": sw6_customer_data['defaultBillingAddress']['salutationId'],
                "firstName": sw6_customer_data['defaultBillingAddress']['firstName'],
                "lastName": sw6_customer_data['defaultBillingAddress']['lastName'],
                "email": sw6_customer_data['email'],
            },
            "price": {
                "netPrice": sw5_order_data["invoiceAmountNet"],
                "totalPrice": sw5_order_data["invoiceAmount"],
                "calculatedTaxes": [{
                    "taxRate": sw5_order_data['details'][0]['taxRate'],
                    "name": f"{sw5_order_data['details'][0]['taxRate']} %",
                    "tax": 0,
                    "price": sw5_order_data["invoiceAmountNet"],
                    "position": 1
                }],
                "taxRules": [self._sw6_get_taxrule_by_tax_rate_and_country_id(
                    tax_rate=sw5_order_data['details'][0]['taxRate'],
                    country_id=sw6_customer_data['defaultBillingAddress']['countryId'],
                )],
                "positionPrice": sw5_order_data["invoiceAmountNet"],
                "rawTotal": sw5_order_data["invoiceAmountNet"],
                "taxStatus": "Net" if sw5_order_data['net'] == 1 else "Gross"
            },
            "shippingCosts": {
                "unitPrice": 7,
                "totalPrice": 7,
                "quantity": 1,
                "calculatedTaxes": [{
                    "taxRate": sw5_order_data['details'][0]['taxRate'],
                    "name": f"{sw5_order_data['details'][0]['taxRate']} %",
                    "tax": 0,
                    "price": 7,
                    "position": 1
                }],
                "taxRules": [self._sw6_get_taxrule_by_tax_rate_and_country_id(
                    tax_rate=sw5_order_data['details'][0]['taxRate'],
                    country_id=sw6_customer_data['defaultBillingAddress']['countryId'],
                )],
            },
            "currencyFactor": sw5_order_data["currencyFactor"],
            "stateId": "62ddf493792c4ae3b963e9b40796d3e1",
            "lineItems": [],
            "createdAt": sw5_order_data["orderTime"]
        }
        for i, item in enumerate(sw5_order_data["details"], start=1):
            sw6_order_data["lineItems"].append(self._sw5_get_line_items(i, item, sw6_customer_data))
        return sw6_order_data

    def _sw5_get_line_items(self, index, sw5_order_item, sw6_customer_data):
        # pprint(sw5_order_item)
        sw6_line_item = {
            # "orderId": sw5_order_item['orderId'],
            "identifier": sw5_order_item['articleName'],
            "quantity": sw5_order_item['quantity'],
            "label": sw5_order_item['articleName'],
            "position": index,
            "price": {
                "unitPrice": sw5_order_item['price'],
                "quantity": sw5_order_item['quantity'],
                "totalPrice": round(sw5_order_item['price'] * sw5_order_item['quantity'], 2),
                "calculatedTaxes": [{
                    "taxRate": sw5_order_item['taxRate'],
                    "name": f"{sw5_order_item['taxRate']} %",
                    "tax": 0,
                    "price": sw5_order_item['price'],
                    "position": index
                }],
                "taxRules": [self._sw6_get_taxrule_by_tax_rate_and_country_id(
                    tax_rate=sw5_order_item['taxRate'],
                    country_id=sw6_customer_data['defaultBillingAddress']['countryId'],
                )]
            }
        }
        return sw6_line_item

    def _sw6_get_taxrule_by_tax_rate_and_country_id(self, tax_rate, country_id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='taxRate', value=tax_rate))
        payload.filter.append(EqualsFilter(field='countryId', value=country_id))

        try:
            result = self.sw6_client.request_post(f"/search/tax-rule", payload)
            if result['data'][0]:
                payload = {
                    "taxRuleTypeId": result['data'][0]['taxRuleTypeId'],
                    "countryId": result['data'][0]["countryId"],
                    "taxRate": result['data'][0]['taxRate'],
                    "taxId": result['data'][0]['taxId'],
                    "percentage": 100
                }
                return payload
            else:
                return None
        except Exception as e:
            print(f"Error on getting tax rule data: {e}")
            return None

    """    EOF SW5 Migration    """


class SW6CustomerAddressEntity(SW6AbstractEntity):

    def __init__(self):
        self._endpoint_name = 'customer-address'
        super().__init__(endpoint_name=self._endpoint_name)

    def map_sw6_to_bridge(self, sw6_json_data):
        try:
            bridge_customer_address_entity_new = BridgeCustomerAddressEntity(
                sw6_id=self.get_sw6_id(sw6_json_data),
                name1=self.get_name_1(sw6_json_data),
                name2=self.get_name_2(sw6_json_data),
                name3=self.get_name_3(sw6_json_data),
                department=self.get_department(sw6_json_data),
                street=self.get_street(sw6_json_data),
                postal_code=self.get_postal_code(sw6_json_data),
                city=self.get_city(sw6_json_data),
                land=self.get_land(sw6_json_data),
                email=self.get_email(sw6_json_data),
                title=self.get_title(sw6_json_data),
                first_name=self.get_first_name(sw6_json_data),
                last_name=self.get_last_name(sw6_json_data),
                phone=self.get_phone(sw6_json_data),
                created_at=datetime.now(),
                edited_at=datetime.now()
            )
            return bridge_customer_address_entity_new
        except Exception as e:
            self.logger.error(f"SW6 Customer Address could not be mapped to BridgeCustomerAddressEntity: {e}")

    def map_bridge_to_sw6(self, bridge_entity):
        pass

    def get_api_customer_address_details(self, id):
        payload = Criteria()
        payload.filter.append(EqualsFilter(field='id', value=id))

        payload.associations["salutation"] = Criteria()
        payload.associations["country"] = Criteria()
        payload.associations["countryState"] = Criteria()
        payload.associations["customer"] = Criteria()

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

    def get_sw6_id(self, sw6_json_data):
        try:
            return sw6_json_data['id']
        except Exception as e:
            self.logger.error(f"Error retrieving id: {e}")
            return None

    def get_name_1(self, sw6_json_data):
        try:
            if sw6_json_data['company']:
                return 'Firma'
            else:
                return sw6_json_data['salutation']['displayName']
        except Exception as e:
            self.logger.error(f"Error retrieving name_1: {e}")
            return None

    def get_name_2(self, sw6_json_data):
        try:
            if self.get_name_1(sw6_json_data) == 'Firma':
                return sw6_json_data['company']
            else:
                first_name = self.get_first_name(sw6_json_data)
                last_name = self.get_last_name(sw6_json_data)
                return f"{first_name} {last_name}"
        except Exception as e:
            self.logger.error(f"Error retrieving name_2: {e}")
            return None

    def get_name_3(self, sw6_json_data):
        # Considering this method is intentionally returning None, no exception handling needed.
        return None

    def get_department(self, sw6_json_data):
        try:
            return sw6_json_data['department']
        except Exception as e:
            self.logger.error(f"Error retrieving department: {e}")
            return None

    def get_street(self, sw6_json_data):
        try:
            return sw6_json_data['street']
        except Exception as e:
            self.logger.error(f"Error retrieving street: {e}")
            return None

    def get_postal_code(self, sw6_json_data):
        try:
            return sw6_json_data['zipcode']
        except Exception as e:
            self.logger.error(f"Error retrieving postal code: {e}")
            return None

    def get_city(self, sw6_json_data):
        try:
            return sw6_json_data['city']
        except Exception as e:
            self.logger.error(f"Error retrieving city: {e}")
            return None

    def get_land(self, sw6_json_data):
        try:
            return sw6_json_data['country']['iso']
        except Exception as e:
            self.logger.error(f"Error retrieving land: {e}")
            return None

    def get_email(self, sw6_json_data):
        try:
            return sw6_json_data['customer']['email']
        except Exception as e:
            self.logger.error(f"Error retrieving email: {e}")
            return None

    def get_title(self, sw6_json_data):
        try:
            return sw6_json_data['salutation']['displayName']
        except Exception as e:
            self.logger.error(f"Error retrieving title: {e}")
            return None

    def get_first_name(self, sw6_json_data):
        try:
            return sw6_json_data['firstName']
        except Exception as e:
            self.logger.error(f"Error retrieving first name: {e}")
            return None

    def get_last_name(self, sw6_json_data):
        try:
            return sw6_json_data['lastName']
        except Exception as e:
            self.logger.error(f"Error retrieving last name: {e}")
            return None

    def get_phone(self, sw6_json_data):
        try:
            return sw6_json_data['phoneNumber']
        except Exception as e:
            self.logger.error(f"Error retrieving phone number: {e}")
