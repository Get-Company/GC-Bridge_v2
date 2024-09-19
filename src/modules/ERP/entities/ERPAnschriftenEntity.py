import json

from ..entities.ERPAbstractEntity import ERPAbstractEntity
from ..entities.ERPAnsprechpartnerEntity import ERPAnsprechpartnerEntity


class ERPAnschriftenEntity(ERPAbstractEntity):
    def __init__(self, erp, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="Anschriften",
            dataset_index=index or "AdrNrAnsNr",
            erp=erp,
            search_value=search_value,
            range_end=range_end
        )

    def map_erp_to_bridge(self):
        pass

    def map_bridge_to_erp(self, bridge_entity, erp_adresse_entity, address_type):
        # Make sure, if we have already some anschriften
        # to add the new one at the end
        ansnr = 0
        erp_anschriften_entity = erp_adresse_entity.get_anschriften()
        last_ansnr = erp_anschriften_entity.get_range_count()
        if last_ansnr:
            ansnr = last_ansnr + 1

        new_anschrift = ERPAnschriftenEntity()
        new_anschrift.append()
        new_anschrift.set_adrnr(erp_adresse_entity.get_adrnr())
        new_anschrift.set_ansnr(ansnr)
        new_anschrift.set_na1(bridge_entity.get_name1())
        new_anschrift.set_na2(bridge_entity.get_name2())
        new_anschrift.set_na3(bridge_entity.get_name3())
        new_anschrift.set_email(bridge_entity.get_email())
        new_anschrift.set_street(bridge_entity.get_street())
        new_anschrift.set_postal_code(bridge_entity.get_postal_code())
        new_anschrift.set_city(bridge_entity.get_city())
        new_anschrift.set_land(bridge_entity.get_land())
        if address_type == 'billing':
            new_anschrift.set_stdrekz(1)
        elif address_type == 'shipping':
            new_anschrift.set_stdlikz(1)
        new_anschrift.post()

        # 2. Now get the entity
        new_anschrift_in_erp = ERPAnschriftenEntity()
        new_anschrift_in_erp.find_one(search_value=[erp_adresse_entity.get_adrnr(), ansnr])
        return new_anschrift_in_erp

    def update(self, bridge_entity, erp_adresse_entity, address_type):
        updated_id = self.get_id()
        try:
            self.edit_()
            self.set_na1(bridge_entity.get_name1() + " Updated")
            self.set_na2(bridge_entity.get_name2())
            self.set_na3(bridge_entity.get_name3())
            # Set E-Mail of Anschrift only on new customers !
            # self.set_email(bridge_entity.get_email())
            self.set_street(bridge_entity.get_street())
            self.set_postal_code(bridge_entity.get_postal_code())
            self.set_city(bridge_entity.get_city())
            self.set_land(bridge_entity.get_land())
            if address_type == 'billing':
                print("Is Billing, set stdrekz on", updated_id)
                self.set_stdrekz(1)
            elif address_type == 'shipping':
                print("Is shipping, set stdlikz on", updated_id)
                self.set_stdlikz(1)
            self.post()

            erp_anschrift_entity_updated = ERPAnschriftenEntity()
            erp_anschrift_entity_updated.find_one(search_value=updated_id, dataset_index='ID')
            return erp_anschrift_entity_updated

        except Exception as e:
            print("Could not update Anschrift", updated_id)
            raise

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

    def set_ansprechpartner(self, value):
        self.set_("Ansprechpartner", value)  # Bitte prüfen Sie den richtigen Key

    def get_adrnr(self):
        return self.get_("AdrNr")

    def set_adrnr(self, value):
        self.set_("AdrNr", value)

    def get_ansnr(self):
        return self.get_("AnsNr")

    def set_ansnr(self, value):
        self.set_("AnsNr", value)

    def get_na1(self):
        return self.get_("Na1")

    def set_na1(self, value):
        self.set_("Na1", value)

    def get_na2(self):
        return self.get_("Na2")

    def set_na2(self, value):
        self.set_("Na2", value)

    def get_na3(self):
        return self.get_("Na3")

    def set_na3(self, value):
        self.set_("Na3", value)

    def get_department(self):
        # No fitting field found, returning None
        return None

    def set_department(self, value):
        pass

    def get_street(self):
        return self.get_("Str")

    def set_street(self, value):
        self.set_("Str", value)

    def get_postal_code(self):
        return self.get_("PLZ")

    def set_postal_code(self, value):
        self.set_("PLZ", value)

    def get_city(self):
        return self.get_("Ort")

    def set_city(self, value):
        self.set_("Ort", value)

    def get_land(self):
        return self.get_("LandKennz")

    def set_land(self, value):
        self.set_("LandKennz", value)

    def get_land_details(self, filter_list=None):
        land_code_raw = self.get_("Land")
        land_code = str(land_code_raw).zfill(3)
        land_details = self.api_get_country_by_ccn3(ccn3=land_code, filter_list=filter_list)
        return land_details

    def get_land_iso2(self):
        land_json = self.get_land_details(filter_list=['cca2'])

        return land_json[0]['cca2']

    def get_email(self):
        return self.get_("EMail1")

    def set_email(self, value):
        self.set_("EMail1", value)

    def get_stdrekz(self):
        return self.get_("StdReKz")

    def set_stdrekz(self, value):
        self.set_("StdReKz", value)

    def get_stdlikz(self):
        return self.get_("StdLiKz")

    def set_stdlikz(self, value):
        self.set_("StdLiKz", value)

    def reset_stdrekz_and_stdlikz(self):
        self.edit_()
        self.set_stdrekz(0)
        self.set_stdlikz(0)
        self.post()

    def __repr__(self):
        return f'Anschrift {self.get_id()} {self.get_("AdrNr")}-{self.get_("AnsNr")} {self.get_("Na1")} {self.get_("Na2")} {self.get_("Na3")}'
