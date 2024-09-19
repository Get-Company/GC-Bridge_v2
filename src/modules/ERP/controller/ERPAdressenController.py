from pprint import pprint

from .ERPConnectionController import ERPConnectionController
from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPAdressenEntity import ERPAdressenEntity
from ..entities.ERPAnschriftenEntity import ERPAnschriftenEntity
from ..entities.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity
from ..controller.ERPKontenplanController import ERPKontenplanController

from src.modules.Bridge.controller.BridgeCustomerController import BridgeCustomerController
from src.modules.Bridge.entities.BridgeCustomerEntity import BridgeCustomerAddressEntity
from datetime import datetime

from ...SW6.controller.SW6CustomerController import SW6CustomerController


class ERPAdressenController(ERPAbstractController):
    """
    Examples:
        **Search by one:**
            adr_ctrl = ERPAdressenController(search_value=10026)
            # Use the child function to get vtrnr
            print(adr_ctrl.get_vtrnr())

        **Search by many:**
            adr_ctrl_ = ERPAdressenController(index="VtrNr", search_value=["54", "65309"])
            # Use the child function to get adrnr
            print(adr_ctrl_index.get_adrnr())

        **Search by range:**
            adr_ctrl_ranged = ERPAdressenController(search_value=["01.09.2023", 10000], index="ErstUmsatz", range_end=["30.09.2023", 69999])
            print("Ranged:", adr_ctrl_ranged.get_entity().get_is_ranged(), "| Count:", adr_ctrl_ranged.get_entity().get_range_count())

        **Get Nested Ums from 09/23 from Adresse 10026**
            adr_ctrl = ERPAdressenController(search_value=10026)
            adr_ctrl_ranged.get_entity().get_nested_("Ums", "Jahr", "2023", "UmsSep")

        **Get Billing Address and the billing contact**
            buchner = ERPAdressenController(10026)
            buchner_billing = buchner.billing_address()
            buchner_billing.get_("Na2")
            buchner_billing_contact = buchner_billing.billing_contact()
            buchner_billing_contact.get_("NNa")

        **Set Billing Address Na2 to Rembremerting**
            buchner = ERPAdressenController(10026)
            buchner_billing = buchner_ctrl.billing_address()
            buchner_billing.start_transaction()
            buchner_billing.set_("Na2", new_name)
            buchner_billing.commit()

        **Get Shipping Address and shipping contact**
            buchner = ERPAdressenController(10026)
            buchner.shipping_address().get_("Na2")
            buchner.shipping_contact().get_("NNa")


    """

    def __init__(self, search_value=None, index=None, range_end=None):
        self._search_value = search_value
        self._index = index
        self._range_end = range_end

        self._bridge_controller = BridgeCustomerController()

        self.erp_adresse_entity_current = None
        self.erp_anschrift_entity_current = None
        self.erp_ansprechpartner_entity_current = None

        super().__init__(
            bridge_controller=self._bridge_controller,
            search_value=self._search_value
        )

    def create_dataset_entity(self, erp):
        try:
            self._dataset_entity = self._dataset_entity = ERPAdressenEntity(
                search_value=self._search_value,
                index=self._index,
                erp=erp,
                range_end=self._range_end)
        except Exception as e:
            print(f"Error creating Adressen Dataset: {str(e)}")

    def destroy_dataset_entity(self):
        print("Adressen destroy dataset")
        self._dataset_entity = None

    def get_entity(self):
        """
        Retrieve the dataset entity of the controller.

        Note: This method is an implementation of the abstract method defined in
        the parent class ERPAbstractController. For a detailed explanation of its purpose
        and behavior, please refer to the documentation in ERPAbstractController.

        Returns:
            Dataset entity.

        Raises:
            ValueError: If dataset entity is not set.
        """
        if self._dataset_entity:
            return self._dataset_entity
        else:
            message = "Dataset entity is not set"
            self.logger.warning(message)
            raise ValueError(message)

    def get_adrnr(self):
        self._adrnr = self.get_entity().get_adrnr()
        return self._adrnr

    def get_vtrnr(self):
        vtrnr = self.get_entity().get_(return_field="VtrNr")
        return vtrnr

    def set_relations(self, bridge_entity):
        bridge_entity = self._set_anschriften_and_ansprechpartner(bridge_entity=bridge_entity)
        return bridge_entity

    def is_in_db(self, bridge_entity_new):
        bridge_entity_in_db = self._bridge_controller.get_entity().query.filter_by(id=bridge_entity_new.id).one_or_none()
        if bridge_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.erp_nr} found in the db!")
            return bridge_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.erp_nr} found in the db!")
            return None

    def _set_anschriften_and_ansprechpartner(self, bridge_entity):
        addresses = self.get_entity().get_anschriften()
        while not addresses.range_eof():
            contacts = addresses.get_ansprechpartner()
            while not contacts.range_eof():
                # 1. Map new objects
                bridge_customer_address_entity_new = self.get_entity().map_erp_customer_address_to_bridge(erp_anschrift_entity=addresses, erp_ansprechpartner_entity=contacts)

                # 2. Check DB for existing entries
                bridge_customer_address_entity_in_db = BridgeCustomerAddressEntity.query.filter_by(id=bridge_customer_address_entity_new.id).one_or_none()

                if bridge_customer_address_entity_in_db:
                    # Update
                    bridge_customer_address_entity_for_db = bridge_customer_address_entity_in_db.update(bridge_entity_new=bridge_customer_address_entity_new)
                else:
                    # Insert
                    bridge_customer_address_entity_for_db = bridge_customer_address_entity_new

                bridge_entity.addresses.append(bridge_customer_address_entity_for_db)
                contacts.range_next()
            addresses.range_next()

        return bridge_entity

    """ Adressen """

    def billing_address(self):
        self.logger.info(f"Get Billing Address from Entity: {self.get_entity().get_dataset_name()}")
        return self.get_entity().get_billing_address_entity()

    def shipping_address(self):
        return self.get_entity().get_shipping_address_entity()

    """ Anschriften """

    def billing_contact(self):
        contact = self.get_entity().get_billing_ansprechpartner_entity()
        return contact

    def shipping_contact(self):
        contact = self.get_entity().get_shipping_ansprechpartner_entity()
        return contact

    """ Direction Bridge to ERP """
    def downsert(self, bridge_entity):
        pass

    def sync_order_addresses_from_bridge(self, bridge_entity, bridge_marketplace_entity):
        """
        Synchronizes customer's order addresses between a given bridge entity and the ERP system.

        Args:
        bridge_entity (BridgeEntity object): Contains information about the customer, address, and contact person.

        Returns:
        BridgeEntity: The processed bridge entity with synchronized data, or False in case of any failures during processing.
        """

        # Step 1: Create or update customer's data in ERP system based on the provided bridge entity.
        erp_adresse_entity = self._handle_customer_create_or_update(bridge_entity=bridge_entity)

        # Step 2: Process billing and shipping information of the customer.
        bridge_entity = self._process_billing_and_shipping(
            bridge_entity=bridge_entity,
            erp_adresse_entity=erp_adresse_entity)

        # Step 3: Update the processed bridge entity in the database.
        try:
            bridge_entity.set_erp_nr(erp_adresse_entity.get_adrnr())
            self.db.session.add(bridge_entity)
            self.db.session.commit()
            self.db.session.refresh(bridge_entity)
        except Exception as e:
            print(f"Could not update db with erp_adresse_entity: {erp_adresse_entity.get_adrnr()}: {e}")
            raise

        # Step 4: Update the processed bridge entity in SW6
        try:
            # Get the marketplace_customer_id
            sw6_customer_entity = SW6CustomerController().get_entity()
            bridge_marketplace_id = bridge_marketplace_entity.get_id()
            print("Marketplace ID:", bridge_marketplace_id)
            sw6_customer_id = bridge_entity.get_customer_marketplace_id(bridge_marketplace_id)

            pprint(f"Update SW6 Customer {sw6_customer_id} from marketplace {bridge_marketplace_id} to new AdrNr {erp_adresse_entity.get_adrnr()}")
            response = sw6_customer_entity.patch_api_change_customer_nr(
                customer_id=sw6_customer_id,
                new_customer_nr=erp_adresse_entity.get_adrnr()
            )
            pprint(response)
        except Exception as e:
            print(f"Could not find BridgeCustomerID: {bridge_entity.get_id()} in BridgeMarketplaceID:{bridge_marketplace_entity.get_id()}, error: {e}")

        # Step 5: Set standard billing and shipping address for the adresse.
        try:
            erp_adresse_entity.edit_()
            erp_adresse_entity.append()
            erp_adresse_entity.set_("BKtoNr", erp_adresse_entity.get_adrnr())
            erp_adresse_entity.set_reansnr(int(bridge_entity.standard_billing_address.get_erp_ans_nr()))
            erp_adresse_entity.set_liansnr(int(bridge_entity.standard_shipping_address.get_erp_ans_nr()))
            erp_adresse_entity.post()
        except Exception as e:
            print("Error on setting ReAnsNr and LiAnsNr:", e)

        # Step 6: Remove all default settings and apply the correct ones.
        self._cleanup_std_kz(bridge_entity=bridge_entity)

        # Get the customer record back from the bridge entity after synchronization.
        return bridge_entity if bridge_entity else None

    def _handle_customer_create_or_update(self, bridge_entity):
        """
        This method handles the creation or updating of customers. It makes use of the "bridge_entity" which is an object
        that holds customer-related data. The function analyzes the customer's ERP number to decide whether to call
        _create_customer or _update_customer functions.

        Args:
        bridge_entity: An object representing a customer carrying all necessary customer data.

        Returns:
        Returns an object with updated customer data if successful, else returns False.
        """

        # Step 1: Evaluate ERP number to determine applicable method for downserting of a customer
        try:
            if int(bridge_entity.erp_nr) > 69999:
                erp_adresse_entity = self._create_customer(bridge_entity)
            elif 10000 < int(bridge_entity.erp_nr) < 69999:
                erp_adresse_entity = self._update_customer(bridge_entity)
            else:
                # Log error for invalid ERP number
                self.logger.error('Invalid ERP number: {}'.format(bridge_entity.erp_nr))
                return False

            if not erp_adresse_entity:
                # Log failed customer creation/updating
                self.logger.error("Couldn't create/update customer. ERP number: {}".format(bridge_entity.erp_nr))
                return False
            else:
                # Log success of customer creation/updating
                self.logger.info('Customer created/updated: {}'.format(erp_adresse_entity.get_adrnr()))
                return erp_adresse_entity

        except Exception as e:
            # Log an exception that occurred during customer creation/updating
            self.logger.error('Failed to create/update customer: {}. Error: {}'.format(bridge_entity.erp_nr, e))
            return False

    def _process_billing_and_shipping(self, bridge_entity, erp_adresse_entity):
        """
        Function to process the billing and shipping details for a given bridge
        entity and ERP address entity. It assigns appropriate values to the
        standard billing and shipping addresses of the bridge entity.

        Args:
        bridge_entity : object
            Bridge entity holding customer-related data
        erp_adresse_entity : object
            ERP address entity holding erp-level record

        Returns:
        object:
            Updated bridge entity with processed standard billing and shipping addresses.
        """
        try:
            # Checking if standard shipping address is same as billing address
            if bridge_entity.standard_shipping_address == bridge_entity.standard_billing_address:
                # Single address for both billing and shipping
                bridge_entity.standard_billing_address = self._process_addresses(
                    bridge_customer_address_entity=bridge_entity.standard_billing_address,
                    erp_adresse_entity=erp_adresse_entity,
                    address_type="billing"
                )
                bridge_entity.standard_shipping_address = self._process_addresses(
                    bridge_customer_address_entity=bridge_entity.standard_billing_address,
                    erp_adresse_entity=erp_adresse_entity,
                    address_type="shipping"
                )
            elif bridge_entity.standard_shipping_address != bridge_entity.standard_billing_address:
                # Separate addresses for billing and shipping
                bridge_entity.standard_billing_address = self._process_addresses(
                    bridge_customer_address_entity=bridge_entity.standard_billing_address,
                    erp_adresse_entity=erp_adresse_entity,
                    address_type="billing"
                )
                bridge_entity.standard_shipping_address = self._process_addresses(
                    bridge_customer_address_entity=bridge_entity.standard_shipping_address,
                    erp_adresse_entity=erp_adresse_entity,
                    address_type="shipping"
                )
            return bridge_entity
        except Exception as e:
            # Log error detail with given logger
            self.logger.error("Error occurred while processing billing and shipping: " + str(e))

    def _process_addresses(self, bridge_customer_address_entity, erp_adresse_entity, address_type="billing"):
        """
        Process addresses for a given bridge customer address entity.
        This method will create or update 'Anschrift' and 'Ansprechpartner' if they exist.

        Args:
        bridge_customer_address_entity : object
            An instance of the bridge customer address entity that is to be updated.
        erp_adresse_entity : object
            An instance of the ERP address entity that is linked with the bridge customer address entity.
        address_type : str
            The type of the address to be processed; can either be "billing" or "shipping".
            Defaults to "billing".

        Returns:
        object:
            Updated bridge customer address entity. Returns False if an exception occurs.
        """
        try:
            # Create or Update 'Anschrift'
            erp_anschrift_entity = self._downsert_anschrift(
                bridge_entity=bridge_customer_address_entity,
                erp_adresse_entity=erp_adresse_entity,
                address_type=address_type
            )

            try:
                # If 'Anschrift' exists, Create or Update 'Ansprechpartner'
                if erp_anschrift_entity:
                    erp_ansprechpartner_entity = self._downsert_ansprechpartner(
                        bridge_entity=bridge_customer_address_entity,
                        erp_adresse_entity=erp_adresse_entity,
                        erp_anschrift_entity=erp_anschrift_entity
                    )
                    # If 'Adresse', 'Anschrift' and 'Ansprechpartner' exists, update the erp_combined_id in the database
                    if erp_adresse_entity and erp_anschrift_entity and erp_ansprechpartner_entity:
                        bridge_customer_address_entity.set_erp_combined_id(
                            erp_adresse_id=erp_adresse_entity.get_id(),
                            erp_anschrift_id=erp_anschrift_entity.get_id(),
                            erp_ansprechpartner_id=erp_ansprechpartner_entity.get_id()
                        )
                        bridge_customer_address_entity.set_erp_nr(erp_adresse_entity.get_adrnr())
                        bridge_customer_address_entity.set_erp_ans_nr(erp_anschrift_entity.get_ansnr())
                        bridge_customer_address_entity.set_erp_asp_nr(erp_ansprechpartner_entity.get_aspnr())
            except Exception as e:
                self.logger.error(f"Error occurred while creating/updating 'Ansprechpartner': {e}")
                return False
        except Exception as e:
            self.logger.error(f"Error occurred while creating/updating 'Anschrift': {e}")
            return False
        return bridge_customer_address_entity

    def _create_customer(self, bridge_entity):
        """
        Method to create a customer. Maps the bridge object to the ERPAdressenEntity,
        fetches the corresponding 'Kontenplan' if it exists, and modifies it based on
        the bridge_entity, otherwise, logs a message that Kontenplan for the respective
        'AdrNr' is not found.

        :param bridge_entity: Object that holds the necessary customer details.
        :returns: ERPAdressenEntity object.
        """
        # Create ERPAdressenEntity instance and map bridge_entity to it
        erp_adresse_entity_new = ERPAdressenEntity().map_bridge_to_erp(bridge_entity)

        # Instantiate ERPKontenplanController
        erp_kontenplan_controller = ERPKontenplanController()

        try:
            # Get ERP Kontenplan entity
            erp_kontenplan_entity = erp_kontenplan_controller.get_entity()

            # Search for the Kontenplan using Adresse's AdrNr
            found = erp_kontenplan_entity.find_one(search_value=erp_adresse_entity_new.get_adrnr())
            if found:
                self.logger.info(f"Found Kontenplan of {erp_adresse_entity_new.get_adrnr()}")

                # Edit and map the Kontenplan entity to the new Adresse
                erp_kontenplan_entity.edit_()
                erp_kontenplan_entity.map_bridge_to_erp(
                    bridge_entity=bridge_entity,
                    erp_entity=erp_adresse_entity_new
                )

                # Post the new event
                erp_kontenplan_entity.post()
            else:
                self.logger.error(f"Kontenplan for AdrNr {erp_adresse_entity_new.get_adrnr()} not found")
        except Exception as e:
            self.logger.exception(f"Error on Kontenplan for Adresse {erp_adresse_entity_new.get_adrnr()}")
            raise

        # Return the newly created ERPAdressenEntity object
        return erp_adresse_entity_new

    def _update_customer(self, bridge_entity):
        """
        This function updates the customer details in the ERP system based on the provided bridge entity.
        If the customer does not exist, it logs an error message and returns False.

        Args:
        bridge_entity (ERPBridgeEntity): The bridge entity that contains the customer data.

        Returns:
        ERPAdressenEntity: An object with updated customer data if successful, else False.
        """
        # Instantiate ERPAdressenEntity class
        erp_adresse_entity_updated = ERPAdressenEntity()

        try:
            # Attempt to find customer in the ERP system
            found = erp_adresse_entity_updated.find_one(
                search_value=bridge_entity.get_erp_nr()
            )
            # Condition to check if the customer exists
            if found:
                # If customer is found, update their details with bridge entity's information
                erp_adresse_entity_updated.update(bridge_entity=bridge_entity)
            else:
                # If customer is not found, log error and return False
                self.logger.error(f"Update Customer {bridge_entity.get_erp_nr()} failed")
                return False
            return erp_adresse_entity_updated
        except Exception as e:
            # Log any error that occurred during the process
            self.logger.error(f"Failed to update customer {bridge_entity.get_erp_nr()}, Error: {str(e)}")
            return False

    def _downsert_anschrift(self, bridge_entity, erp_adresse_entity, address_type):
        """
        Function to update or insert  (upsert) the Anschrift records.
        If the record with given erp_combined_id exists, the record is updated.
        If the record with given erp_combined_id does not exist, one is created.

        :param bridge_entity: The bridge entity containing the information to update
        :param erp_adresse_entity: The adresse entity containing the information to insert
        :param adress_type: Type of the address(e.g., billing)
        :return erp_anschrift_entity: The updated or newly created Anschrift entity
        """
        self.logger.info("Initializing downsert_anschrift...")

        erp_anschrift_entity = None
        found = False

        try:
            # Check if erp_combined_id exists
            if bridge_entity.get_id_for_erp_anschrift_from_combined_id():
                self.logger.info("erp_combined_id found. Preparing for update or creation of Anschrift entity...")

                erp_anschrift_entity = ERPAnschriftenEntity()
                try:
                    # Try to fetch Anschrift entity based on the erp_combined_id
                    found = erp_anschrift_entity.find_one(
                        search_value=bridge_entity.get_id_for_erp_anschrift_from_combined_id(),
                        dataset_index='ID'
                    )
                except Exception as err:
                    # Log any exception occurred during data fetching
                    self.logger.error(f"Error while trying to find Anschrift entity: {err}")
                if found:
                    # If record found, update the existing Anschrift record
                    self.logger.info("Anschrift entity found. Updating...")
                    erp_anschrift_entity = self._update_anschrift(
                        bridge_entity=bridge_entity,
                        erp_adresse_entity=erp_adresse_entity,
                        erp_anschrift_entity=erp_anschrift_entity,
                        address_type=address_type
                    )
                    self.logger.info("Anschrift entity updated successfully!")
                    return erp_anschrift_entity
                else:
                    # If not found, create a new Anschrift record
                    self.logger.info("Anschrift not found. Creating new Anschrift...")
                    erp_anschrift_entity = self._create_anschrift(
                        bridge_entity=bridge_entity,
                        erp_adresse_entity=erp_adresse_entity,
                        address_type=address_type
                    )
                    self.logger.info(f"New Anschrift created successfully! ID: {erp_anschrift_entity.get_ansnr()}")
                    return erp_anschrift_entity
            else:
                # If erp_combined_id not provided, create a new Anschrift
                self.logger.info("erp_combined_id not provided. Creating new Anschrift...")
                erp_anschrift_entity = self._create_anschrift(
                    bridge_entity=bridge_entity,
                    erp_adresse_entity=erp_adresse_entity,
                    address_type=address_type
                )
                self.logger.info("New Anschrift created successfully!")
                return erp_anschrift_entity
        except Exception as error:
            # Log any exception occurred during the process
            self.logger.error(f"An error occurred in downsert_anschrift: {error}")
            return False

    def _create_anschrift(self, bridge_entity, erp_adresse_entity, address_type):
        """
        Performs mapping from a bridge address entity to ERP address entity.

        Args:
            bridge_entity (BridgeEntity): The bridge entity containing address information.
            erp_adresse_entity (ERPAnschriftenEntity): The ERP entity where information will be stored.
            address_type (str): The type of the address (i.e., billing, shipping).

        Returns:
            erp_anschrift_entity (ERPAnschriftenEntity): The mapped ERP entity.
            If mapping fails, returns None.
        """

        try:
            # Map bridge information to ERP address entity
            erp_anschrift_entity = ERPAnschriftenEntity().map_bridge_to_erp(
                bridge_entity=bridge_entity,
                erp_adresse_entity=erp_adresse_entity,
                address_type=address_type
            )
            # If mapping is successful, return the ERP address entity
            if erp_anschrift_entity:
                return erp_anschrift_entity
            # If mapping fails, return None
            else:
                return None
        except Exception as e:
            # Log the error details
            self.logger.error(f"Error occurred while creating address entity: {e}")
            # If an exception happened, return None
            return None

    def _update_anschrift(self, bridge_entity, erp_adresse_entity, erp_anschrift_entity, address_type):
        """
        Function to update the Anschrift entity.

        :param bridge_entity: The bridge entity containing the information to update
        :param erp_adresse_entity: The erp_adresse_entity containing the address information
        :param erp_anschrift_entity: The original anschrift entity that needs to be updated
        :param address_type: Type of the address (e.g., 'billing', 'shipping')
        :return erp_anschrift_entity: Updated Anschrift entity
        """
        try:
            # Perform update operation on the erp_anschrift_entity using given data
            erp_anschrift_entity_updated = erp_anschrift_entity.update(
                bridge_entity=bridge_entity,
                erp_adresse_entity=erp_adresse_entity,
                address_type=address_type
            )
        except Exception as err:
            # Log the error incase of any exceptions
            self.logger.error(f"Error while updating anschrift entity: {err}")
            return None

        # Return the updated entity
        return erp_anschrift_entity_updated

    def _cleanup_std_kz(self, bridge_entity):
        """
        Cleanups the standard address key for a given bridge entity. It checks if bridge entity exists,
        if exists, fetches all addresses, sets the standard billing or shipping address key, and saves
        it back to ERP system.
        """
        try:
            erp_entity_for_cleanup = ERPAdressenEntity()
            found = erp_entity_for_cleanup.find_one(bridge_entity.get_erp_nr())

            # If entity found in ERP
            if found:
                # Get all addresses for the entity
                anschriften = erp_entity_for_cleanup.get_anschriften()
                print(f"Found {anschriften.range_count()} Anschriften")
                erp_entity_for_cleanup.edit_()

                while not anschriften.range_eof():
                    anschriften.edit_()
                    # Get bridge billing address & respective ids
                    bridge_billing_entity = bridge_entity.standard_billing_address
                    bridge_billing_id = bridge_billing_entity.get_id_for_erp_anschrift_from_combined_id()
                    bridge_billing_erp_ans_nr = bridge_billing_entity.get_erp_ans_nr()
                    print(
                        f"Bridge Billing {bridge_billing_id}-{bridge_billing_erp_ans_nr} = ERP Anschrift {anschriften.get_id()}:{anschriften.get_ansnr()}")

                    # If billing address matches
                    if int(bridge_billing_id) == int(anschriften.get_id()):
                        print("Billing Match")
                        erp_entity_for_cleanup.set_reansnr(int(anschriften.get_ansnr()))
                        anschriften.set_stdrekz(1)
                    else:
                        anschriften.set_stdrekz(0)

                    # Get bridge shipping address & respective ids
                    bridge_shipping_entity = bridge_entity.standard_shipping_address
                    bridge_shipping_id = bridge_shipping_entity.get_id_for_erp_anschrift_from_combined_id()
                    bridge_shipping_erp_ans_nr = bridge_shipping_entity.get_erp_ans_nr()
                    print(
                        f"Bridge Shipping {bridge_shipping_id}-{bridge_shipping_erp_ans_nr} = ERP Anschrift {anschriften.get_id()}:{anschriften.get_ansnr()}")

                    # If shipping address matches
                    if int(bridge_shipping_id) == int(anschriften.get_id()):
                        print("Shipping match")
                        erp_entity_for_cleanup.set_liansnr(int(anschriften.get_ansnr()))
                        anschriften.set_stdlikz(1)
                    else:
                        anschriften.set_stdlikz(0)

                    # Post updates to Address and move the range cursor to next
                    anschriften.post()
                    anschriften.range_next()
                # Post all the updates to ERPAdressenEntity
                erp_entity_for_cleanup.post()

        except Exception as e:
            # Log the error message and rethrow the exception to handle it at higher level
            self.logger.error(f"Error occurred while cleaning up standard address key: {e}")
            raise e

    def _downsert_ansprechpartner(self, bridge_entity, erp_adresse_entity, erp_anschrift_entity):
        """
        The function attempts to downsert (i.e. update or insert) an Ansprechpartner entity. The operation is based on
        whether a corresponding Ansprechpartner with the same ID exists in the database.

        Parameters:
        bridge_entity: Bridge entity which contains the record that should be downserted.
        erp_adresse_entity: ERP address entry connected to the Ansprechpartne.
        erp_anschrift_entity: ERP address entry related to Ansprechpartner.

        Returns:
        erp_ansprechpartner_entity: ERPAnsprechpartnerEntity that was updated or created.
        """
        erp_ansprechpartner_entity = None

        try:
            # Checking the presence of ID
            if bridge_entity.get_id_for_erp_ansprechpartner_from_combined_id():
                print(f"Update Ansprechpartner: {bridge_entity.get_id_for_erp_anschrift_from_combined_id()}")

                erp_ansprechpartner_entity = ERPAnsprechpartnerEntity()
                found = None

                try:
                    # Attempt to find the entity in the DB.
                    found = erp_ansprechpartner_entity.find_one(
                        search_value=bridge_entity.get_id_for_erp_ansprechpartner_from_combined_id(),
                        dataset_index='ID'
                    )
                except Exception as error:
                    self.logger.error(f"Error while finding Ansprechpartner entity: {error}")

                # If found, update the entry else create a new one.
                if found:
                    erp_ansprechpartner_entity = self._update_ansprechpartner(
                        bridge_entity=bridge_entity,
                        erp_adresse_entity=erp_adresse_entity,
                        erp_anschrift_entity=erp_anschrift_entity,
                        erp_ansprechpartner_entity=erp_ansprechpartner_entity
                    )
                else:
                    erp_ansprechpartner_entity = self._create_ansprechpartner(
                        bridge_entity=bridge_entity,
                        erp_adresse_entity=erp_adresse_entity,
                        erp_anschrift_entity=erp_anschrift_entity
                    )
                return erp_ansprechpartner_entity
            else:
                # When ID isn't found, a new entry is created.
                erp_ansprechpartner_entity = self._create_ansprechpartner(
                    bridge_entity=bridge_entity,
                    erp_adresse_entity=erp_adresse_entity,
                    erp_anschrift_entity=erp_anschrift_entity
                )
            return erp_ansprechpartner_entity
        except Exception as error:
            self.logger.error(f"Error occurred in downsert_ansprechpartner method: {error}")
            return False

    def _create_ansprechpartner(self, bridge_entity, erp_adresse_entity, erp_anschrift_entity):
        """
        Method to create an Ansprechpartner entity based on the provided arguments.

        Parameters:
            bridge_entity (type: BridgeEntity): Entity from the bridge repository.
            erp_adresse_entity (type: ERPAdresseEntity): ERPAdresse entity associated with the Ansprechpartner.
            erp_anschrift_entity (type: ERPAnschriftEntity): ERPAnschrift entity associated with the Ansprechpartner.

        Returns:
            erp_ansprechpartner_entity (type: ERPAnsprechpartnerEntity): ERPAnsprechpartner entity associated with the bridge_entity.
        """
        try:
            # Log information about Ansprechpartner creation
            self.logger.info(
                f"Create Ansprechpartner for Adr: {erp_adresse_entity.get_adrnr()} and Ans: {erp_anschrift_entity.get_ansnr()}")

            # Create a new Ansprechpartner entity by mapping the Bridge Entity to the ERP Ansprechpartner entity
            erp_ansprechpartner_entity = ERPAnsprechpartnerEntity().map_bridge_to_erp(
                bridge_entity=bridge_entity,
                erp_adresse_entity=erp_adresse_entity,
                erp_anschrift_entity=erp_anschrift_entity
            )
        except Exception as ex:
            # Log any exception that occurs during the process
            self.logger.error(f"Error occurred while creating Ansprechpartner: {ex}")
            return None

        # Return the created ERP Ansprechpartner entity
        return erp_ansprechpartner_entity

    def _update_ansprechpartner(self, bridge_entity, erp_adresse_entity, erp_anschrift_entity, erp_ansprechpartner_entity):
        """
        Updates the provided `erp_ansprechpartner_entity` using details from `bridge_entity`, `erp_adresse_entity` and
        `erp_anschrift_entity`. The updated `erp_ansprechpartner_entity` is then returned.

        Parameters:
            bridge_entity: The bridge entity containing details for the update operation.
            erp_adresse_entity: ERP address entity related to Ansprechpartner.
            erp_anschrift_entity: ERP anschrift entity related to Ansprechpartner.
            erp_ansprechpartner_entity: The ERP Ansprechpartner entity to be updated.

        Returns:
            erp_ansprechpartner_entity: The updated ERP Ansprechpartner entity.
        """

        try:
            # Perform the update operation
            erp_ansprechpartner_entity_updated = erp_ansprechpartner_entity.update(
                bridge_entity=bridge_entity,
                erp_adresse_entity=erp_adresse_entity,
                erp_anschrift_entity=erp_anschrift_entity,
                erp_ansprechpartner_entity=erp_ansprechpartner_entity
            )
            return erp_ansprechpartner_entity_updated
        except Exception as e:
            # Log any exceptions that occur during the update operation
            self.logger.error(f"Error occurred while updating Ansprechpartner entity: {e}")
            return None

    def __del__(self):
        print("ERPAdressenController del called.")
        erp_co_ctrl = ERPConnectionController()

        erp_co_ctrl.close()
