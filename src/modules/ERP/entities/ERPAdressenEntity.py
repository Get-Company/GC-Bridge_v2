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
        self.set_("Branche", "Murketing")

    def map_erp_customer_address_to_bridge(self, erp_anschrift_entity: ERPAnschriftenEntity,
                                           erp_ansprechpartner_entity: ERPAnsprechpartnerEntity):
        try:
            customer_address_entity = BridgeCustomerAddressEntity(
                id=erp_ansprechpartner_entity.get_id(),
                erp_combined_id=f"{self.get_id()};{erp_anschrift_entity.get_id()};{erp_ansprechpartner_entity.get_id()}",
                erp_nr=self.get_adrnr(),
                erp_ans_nr=erp_ansprechpartner_entity.get_ansnr(),
                erp_asp_nr=erp_ansprechpartner_entity.get_aspnr(),
                name1=erp_anschrift_entity.get_na1(),
                name2=erp_anschrift_entity.get_na2(),
                name3=erp_anschrift_entity.get_na3(),
                department=erp_anschrift_entity.get_department(),
                street=erp_anschrift_entity.get_street(),
                postal_code=erp_anschrift_entity.get_postal_code(),
                city=erp_anschrift_entity.get_city(),
                land=erp_anschrift_entity.get_land_iso2(),
                email=erp_anschrift_entity.get_email(),
                title=erp_ansprechpartner_entity.get_title(),
                first_name=erp_ansprechpartner_entity.get_first_name(),
                last_name=erp_ansprechpartner_entity.get_last_name(),
                created_at=erp_ansprechpartner_entity.get_erstdat(),
                edited_at=erp_ansprechpartner_entity.get_aenddat()
            )
            return customer_address_entity

        except Exception as e:
            # Log the error and return None
            self.logger.error(f"Error mapping ERPCustomerAdress to Bridge: {str(e)}")
            return None

    def get_adrnr(self):
        return self.get_("AdrNr")

    def get_reansnr(self):
        return self.get_("ReAnsNr")

    def get_email(self):
        billing_ansprechpartner = self.get_billing_ansprechpartner_entity()
        email = billing_ansprechpartner.get_("EMail1")
        return email

    def get_vat_id(self):
        return self.get_("UStId")

    def get_erp_combined_id(self):
        # Todo: Create the combined erp_id_string separated by ;
        # Example:
        # 55660;13420;56987
        # Address;Anschrift;Ansprechpartner
        pass

    def get_liansnr(self):
        return self.get_("LiAnsNr")

    def get_billing_address_entity(self):
        self.logger.info(f"Get the billing address from ERPAnschriftenEntity")
        return ERPAnschriftenEntity([self.get_adrnr(), self.get_reansnr()])

    def get_shipping_address_entity(self):
        return ERPAnschriftenEntity([self.get_adrnr(), self.get_liansnr()])

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

    def get_webshop_id_kz(self):
        return self.get_("WShopAdrKz")

    def __repr__(self):
        return f'Adresse {self.get_adrnr()}'
