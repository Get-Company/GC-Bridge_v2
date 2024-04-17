from pprint import pprint

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

    def map_bridge_to_erp(self, bridge_entity, erp_adresse_entity, erp_anschrift_entity):
        try:
            aspnr = 0
            erp_ansprechpartner_entity = erp_anschrift_entity.get_ansprechpartner()
            last_aspnr = erp_ansprechpartner_entity.get_range_count()
            if last_aspnr:
                print(f"We have {last_aspnr} Ansprechpartner in Anschrift {erp_anschrift_entity.get_ansnr()} in AdrNr: {erp_adresse_entity.get_adrnr()}")
                aspnr = last_aspnr + 1

            new_ansprechpartner = ERPAnsprechpartnerEntity()
            new_ansprechpartner.append()
            new_ansprechpartner.set_adrnr(erp_adresse_entity.get_adrnr())
            new_ansprechpartner.set_ansnr(erp_anschrift_entity.get_ansnr())
            new_ansprechpartner.set_aspnr(aspnr)
            new_ansprechpartner.set_email(bridge_entity.get_email())
            new_ansprechpartner.set_anrede(bridge_entity.get_title())
            new_ansprechpartner.set_first_name(bridge_entity.get_first_name())
            new_ansprechpartner.set_last_name(bridge_entity.get_last_name())
            new_ansprechpartner.set_("AnspAufbau", 6)  # 6 Pos in Dropdown - means: Title Vorname Zusatz Vorsatz Nachname)
            new_ansprechpartner.set_ansprechpartner(f"{bridge_entity.get_title()} {bridge_entity.get_first_name()} {bridge_entity.get_last_name()}")
            new_ansprechpartner.post()
        except Exception as a:
            print("Creating Ansprechpartner", erp_adresse_entity.get_adrnr(), erp_anschrift_entity.get_ansnr(), a)

        # Now get the entity
        new_ansprechpartner_in_erp = ERPAnsprechpartnerEntity()
        new_ansprechpartner_in_erp.find_one(search_value=[erp_adresse_entity.get_adrnr(), erp_anschrift_entity.get_ansnr(), aspnr])
        return new_ansprechpartner_in_erp

    def update(self, bridge_entity, erp_adresse_entity, erp_anschrift_entity, erp_ansprechpartner_entity):
        updated_id = self.get_id()
        try:
            self.edit_()
            self.set_title(bridge_entity.get_title())
            self.set_first_name(bridge_entity.get)
            self.set_last_name(bridge_entity.get_last_name())
            self.post()

            erp_ansprechpartner_entity_updated = ERPAnsprechpartnerEntity()
            erp_ansprechpartner_entity_updated.find_one(search_value=updated_id, dataset_index='ID')
            return erp_ansprechpartner_entity_updated

        except Exception as e:
            print("Could not update Anschrift", updated_id)
            raise

    def get_adrnr(self):
        try:
            adrnr = int(self.get_("AdrNr"))
            return adrnr
        except ValueError:
            print("Fehler: AdrNr ist kein gültiger Integer.")
            return None  # oder eine geeignete Standardaktion

    def set_adrnr(self, value):
        try:
            adrnr = int(value)
            self.set_("AdrNr", adrnr)
        except ValueError:
            print("Fehler: Der eingegebene Wert ist kein gültiger Integer.")

    def get_ansnr(self):
        try:
            ansnr = int(self.get_("AnsNr"))
            return ansnr
        except ValueError:
            print("Fehler: AnsNr ist kein gültiger Integer.")
            return None  # oder eine geeignete Standardaktion

    def set_ansnr(self, value):
        try:
            ansnr = int(value)
            self.set_("AnsNr", ansnr)
        except ValueError:
            print("Fehler: Der eingegebene Wert ist kein gültiger Integer.")

    def get_aspnr(self):
        try:
            aspnr = int(self.get_("AspNr"))
            return aspnr
        except ValueError:
            print("Fehler: AspNr ist kein gültiger Integer.")
            return None  # oder eine geeignete Standardaktion

    def set_aspnr(self, value):
        try:
            aspnr = int(value)
            self.set_("AspNr", aspnr)
        except ValueError:
            print("Fehler: Der eingegebene Wert ist kein gültiger Integer.")

    def get_email(self):
        return self.get_("EMail1")

    def set_email(self, value):
        self.set_("EMail1", value)

    def get_title(self):
        # Changed to Anr which is the correct title like Frau and Herr
        return self.get_("Anr")

    def set_title(self, value):
        self.set_("Anr", value)

    def get_anrede(self):
        self.get_("Anr")

    def set_anrede(self, value):
        self.set_("Anr", value)

    def get_first_name(self):
        return self.get_("VNa")

    def set_first_name(self, value):
        self.set_("VNa", value)

    def get_last_name(self):
        return self.get_("NNa")

    def set_last_name(self, value):
        self.set_("NNa", value)

    def get_ansprechpartner(self):
        return self.get_("Ansp")

    def set_ansprechpartner(self, value):
        self.set_("Ansp", value)

    def __repr__(self):
        return f'Ansprechpartner {self.get_id()} {self.get_("AdrNr")}-{self.get_("AnsNr")}-{self.get_("AspNr")} {self.get_("Anr")} {self.get_("NNa")} {self.get_("VNa")}'