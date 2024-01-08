from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPAnsprechpartnerEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="Ansprechpartner",
            dataset_index=index or "AdrNrAnsNrAspNr",
            search_value=search_value,
            range_end=range_end
        )

    def map_erp_to_bridge(self):
        pass

    def map_bridge_to_erp(self, bridge_entity):
        pass

    def get_adrnr(self):
        try:
            adrnr = int(self.get_("AdrNr"))
            return adrnr
        except ValueError:
            print("Fehler: AdrNr ist kein gültiger Integer.")
            return None  # oder eine geeignete Standardaktion

    def get_ansnr(self):
        try:
            ansnr = int(self.get_("AnsNr"))
            return ansnr
        except ValueError:
            print("Fehler: AnsNr ist kein gültiger Integer.")
            return None  # oder eine geeignete Standardaktion

    def get_aspnr(self):
        try:
            aspnr = int(self.get_("AspNr"))
            return aspnr
        except ValueError:
            print("Fehler: AspNr ist kein gültiger Integer.")
            return None  # oder eine geeignete Standardaktion

    def get_email(self):
        return self.get_("EMail1")

    def get_title(self):
        # Changed to Anr which is the correct title like Frau and Herr
        return self.get_("Anr")

    def get_first_name(self):
        return self.get_("VNa")

    def get_last_name(self):
        return self.get_("NNa")

    def __repr__(self):
        return f'Ansprechpartner {self.get_id()} {self.get_("AdrNr")}-{self.get_("AnsNr")}-{self.get_("AspNr")} {self.get_("Anr")} {self.get_("NNa")} {self.get_("VNa")}'