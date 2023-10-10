from ..entities.ERPAbstractEntity import ERPAbstractEntity
from ..entities.ERPAnschriftenEntity import ERPAnschriftenEntity
from ..entities.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity


class ERPAdressenEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):

        super().__init__(
            dataset_name="Adressen",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def get_reansnr(self):
        return self.get_("ReAnsNr")

    def get_liansnr(self):
        return self.get_("LiAnsNr")

    def get_adrnr(self):
        return self.get_("AdrNr")

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

    def get_addresses_range(self):
        addresses_range = ERPAnschriftenEntity(
            search_value=[self.adrnr, 0],
            range_end=[self.adrnr, 9999]
        )
        return addresses_range

    def get_contacts(self):
        contacts_range = ERPAnsprechpartnerEntity(
            search_value=[self.adrnr, 0 , 0],
            range_end=[self.adrnr,9999,9999]
        )
        return contacts_range

    def map_erp_to_bridge(self):
        pass






