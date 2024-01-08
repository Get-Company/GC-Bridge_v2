from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPAdressenEntity import ERPAdressenEntity

from src.modules.Bridge.controller.BridgeCustomerController import BridgeCustomerController
from src.modules.Bridge.entities.BridgeCustomerEntity import BridgeCustomerAddressEntity
from datetime import datetime


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
        self._dataset_entity = ERPAdressenEntity(
            search_value=search_value,
            index=index,
            range_end=range_end)

        self._bridge_controller = BridgeCustomerController()

        super().__init__(
            dataset_entity=self._dataset_entity,
            bridge_controller=self._bridge_controller
        )

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

    """
    Direction Bridge to ERP
    """
    def downsert(self, bridge_entity):
        erp_entity = self._dataset_entity
        found = erp_entity.find_one(
            search_value=bridge_entity.get_id(),
            dataset_index='ID'
        )
        if found:
            # Update customer
            print(erp_entity.get_("AdrNr"), erp_entity.get_("ID"))
            erp_entity.map_bridge_to_erp(bridge_entity=bridge_entity)
            erp_entity.start_transaction()
            erp_entity.post()
        else:
            # Insert customer
            print(f"No customer with id {bridge_entity.get_id()} found.")