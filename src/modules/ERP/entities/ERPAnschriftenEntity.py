from ..entities.ERPAbstractEntity import ERPAbstractEntity
from ..entities.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity


class ERPAnschriftenEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="Anschriften",
            dataset_index=index or "AdrNrAnsNr",
            search_value=search_value,
            range_end=range_end
        )

    def get_ansprechpartner(self, max=20):
        return ERPAnsprechpartnerEntity(
            search_value=[
                self.get_("AdrNr"),
                self.get_("AnsNr"),
                0
            ],
            range_end=[
                self.get_("AdrNr"),
                self.get_("AnsNr"),
                max
            ]
        )

    def map_erp_to_bridge(self):
        pass

    def map_bridge_to_erp(self, bridge_entity):
        pass

    def get_na1(self):
        return self.get_("Na1")

    def get_na2(self):
        return self.get_("Na2")

    def get_na3(self):
        return self.get_("Na3")

    def get_department(self):
        # No fitting field found, returning None
        return None

    def get_street(self):
        return self.get_("Str")

    def get_postal_code(self):
        return self.get_("PLZ")

    def get_city(self):
        return self.get_("Ort")

    def get_land(self):
        return self.get_("LandKennz")

    def get_email(self):
        return self.get_("EMail1")

    def __repr__(self):
        return f'Anschrift {self.get_id()} {self.get_("AdrNr")}-{self.get_("AnsNr")} {self.get_("Na1")} {self.get_("Na2")} {self.get_("Na3")}'
