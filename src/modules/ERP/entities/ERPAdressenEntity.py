from pprint import pprint

from ..entities.ERPAbstractEntity import ERPAbstractEntity
from ..entities.ERPAnschriftenEntity import ERPAnschriftenEntity
from ..entities.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity

from src.modules.Bridge.entities.BridgeCustomerEntity import BridgeCustomerEntity, BridgeCustomerAddressEntity


class ERPAdressenEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):

        super().__init__(
            dataset_name="Adressen",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )
        # This comes after the parent.
        self.set_created_dataset_ex()

    def map_erp_to_bridge(self):
        try:
            customer_entity = BridgeCustomerEntity(
                id=self.get_id(),
                erp_nr=self.get_adrnr(),
                email=self.get_email(),
                vat_id=self.get_vat_id(),
                created_at=self.get_erstdat(),
                edited_at=self.get_aenddat()
            )
            return customer_entity

        except Exception as e:
            # Log the error and return None
            self.logger.error(f"Error mapping ERPCustomer to Bridge: {str(e)}")
            return None

    def map_bridge_to_erp(self, bridge_entity):
        # 1. Find the dataset in the
        new_address = ERPAdressenEntity()
        new_address.append()
        erp_adrnr_new = new_address.get_created_dataset().SetupNr("")
        print("AdrNr new:", erp_adrnr_new)
        new_address.set_adrnr(erp_adrnr_new)
        new_address.set_suchbeg("GCB")
        new_address.set_status('Kunde aus Internet')
        new_address = self.set_values_from_file(
            erp_dataset=new_address,
            entity='customer',
            country=bridge_entity.standard_billing_address.get_land()
        )
        new_address.post()
        try:
            # Fetch the adresse again and return it
            new_address_in_erp = ERPAdressenEntity()
            new_address_in_erp.find_one(search_value=erp_adrnr_new)
            return new_address_in_erp
        except Exception as e:
            print("Error mapping BridgeCustomerEntity to ERPAdressenEntity", e)
            raise

    def update(self, bridge_entity):
        updated_id = self.get_id()
        self.edit_()
        self.set_suchbeg("GCU")
        self.set_status("GCB Kunde - Update")
        self.post()

        erp_adress_entity_updated = ERPAdressenEntity()
        erp_adress_entity_updated.find_one(search_value=updated_id, dataset_index='ID')

        return erp_adress_entity_updated

    def set_created_dataset_ex(self):
        """
        Create and set the dataset EX using the dataset name.
        Overwrites the _created_dataset
        """
        try:
            if self.get_dataset_name():
                self._created_dataset = self._dataset_infos.Item(self.get_dataset_name()).CreateDataSetEx()
                self.logger.info(f"Set {self.get_dataset_name()} as created dataset Ex")
            else:
                raise ValueError("Dataset name is not set. Cannot create dataset Ex.")
        except Exception as e:
            self.logger.error(f"Error creating dataset Ex for {self.get_dataset_name()}: {str(e)}")
            raise

    def get_adrnr(self):
        return self.get_("AdrNr")

    def set_adrnr(self, value):
        self.set_("AdrNr", value)

    def get_reansnr(self):
        return self.get_("ReAnsNr")

    def set_reansnr(self, value):
        self.set_("ReAnsNr", value)

    def get_email(self):
        billing_ansprechpartner = self.get_billing_ansprechpartner_entity()
        email = billing_ansprechpartner.get_("EMail1")
        return email

    def set_email(self, value):
        self.set_("EMail1", value)

    def get_vat_id(self):
        return self.get_("UStId")

    def set_vat_id(self, value):
        self.set_("UStId", value)

    def get_erp_combined_id(self):
        # Todo: Create the combined erp_id_string separated by ;
        # Example:
        # 55660;13420;56987
        # Address;Anschrift;Ansprechpartner
        pass

    def get_liansnr(self):
        return self.get_("LiAnsNr")

    def set_liansnr(self, value):
        self.set_("LiAnsNr", value)

    def get_billing_address_entity(self):
        self.logger.info(f"Get the billing address from ERPAnschriftenEntity")
        return ERPAnschriftenEntity([self.get_adrnr(), self.get_reansnr()])

    def set_billing_address(self):
        # Todo: Set the billing address
        pass

    def get_shipping_address_entity(self):
        return ERPAnschriftenEntity([self.get_adrnr(), self.get_liansnr()])

    def set_shipping_address(self):
        # Todo: Set the shipping address
        pass

    def get_billing_ansprechpartner_entity(self):

        return ERPAnsprechpartnerEntity(
            [
                self.get_adrnr(),
                self.get_reansnr(),
                self.get_billing_address_entity().get_("AspNr")
            ]
        )

    def get_shipping_ansprechpartner_entity(self):
        return ERPAnsprechpartnerEntity(
            [
                self.get_adrnr(),
                self.get_liansnr(),
                self.get_shipping_address_entity().get_("AspNr")
            ]
        )

    def get_anschriften(self, max=500):
        addresses_range = ERPAnschriftenEntity(
            search_value=[self.get_adrnr(), 0],
            range_end=[self.get_adrnr(), max]
        )
        return addresses_range

    def get_ansprechpartner_by(self, ansnr, adrnr=None):
        if not adrnr:
            adrnr = self.get_adrnr()

        contact = ERPAnsprechpartnerEntity(
            search_value=[adrnr, ansnr, 0],
            range_end=[adrnr, ansnr, 999]
        )
        ERPAnschriftenEntity().set_created_dataset()

    def get_ansprechpartner(self):
        contacts_range = ERPAnsprechpartnerEntity(
            search_value=[self.adrnr, 0, 0],
            range_end=[self.adrnr, 9999, 9999]
        )
        return contacts_range

    def get_webshop_id(self):
        return self.get_("WShopID")

    def set_webshop_id(self, value):
        self.set_("WShopID", value)

    def get_webshop_id_kz(self):
        return self.get_("WShopAdrKz")

    def set_webshop_id_kz(self, value):
        self.set_("WShopAdrKz", value)

    def get_suchbeg(self):
        return self.get_("SuchBeg")

    def set_suchbeg(self, value):
        self.set_("SuchBeg", value)

    def get_status(self):
        return self.get_("Status")

    def set_status(self, value):
        self.set_("Status", value)

    def print_all_anschriften_and_ansprechparter(self):

        anschriften_entity_ds = self.get_anschriften()

        while not anschriften_entity_ds.range_eof():
            ansprechpartner_ds = anschriften_entity_ds.get_ansprechpartner()

            while not ansprechpartner_ds.range_eof():
                print(f"Adrnr: {anschriften_entity_ds.get_adrnr()} Anschrift Ansnr: {anschriften_entity_ds.get_ansnr()} Ansprechpartner AspNr: {ansprechpartner_ds.get_aspnr()}")

                ansprechpartner_ds.range_next()

            anschriften_entity_ds.range_next()

    def __repr__(self):
        return f'Adresse {self.get_adrnr()}'
