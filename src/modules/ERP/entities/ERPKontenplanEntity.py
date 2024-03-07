import datetime

from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPKontenplanEntity(ERPAbstractEntity):
    """
    Representation of an ERP article entity inherited from ERPAbstractEntity.
    """

    def __init__(self, search_value=None, index=None, range_end=None):
        """
        Initializer for ERPKontenplanEntity.

        :param search_value: The value used for searching.
        :param index: The index for the dataset, defaults to 'Nr' if not provided.
        :param range_end: The range end value.
        """
        super().__init__(
            dataset_name="Kontenplan",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end,
            filter_expression=None
        )

    def map_erp_to_bridge(self): pass

    def map_erp_translation_to_bridge(self): pass

    def map_bridge_to_erp(self, bridge_entity, erp_entity):
        self.set_ktonr(erp_entity.get_adrnr())
        self.set_bez(bridge_entity.standard_billing_address.get_title_firstname_lastname())
        self.set_kategorie('Personenkonto/Debitoren')
        self.set_ebbuchkz(1)

    def get_bez(self):
        return self.get_("Bez")

    def set_bez(self, bez):
        self.set_("Bez", bez)

    def get_ktonr(self):
        return self.get_("KtoNr")

    def set_ktonr(self, ktonr):
        self.set_("KtoNr", ktonr)

    def get_kategorie(self):
        return self.get_("Kategorie")

    def set_kategorie(self, kategorie):
        self.set_("Kategorie", kategorie, cast_type="Text")

    def get_ebbuchkz(self):
        return self.get_("EBBuchKz")

    def set_ebbuchkz(self, ebbuchkz):
        self.set_("EBBuchKz", ebbuchkz)

    def __repr__(self):
        return f'Kontenplan {self.get_ktonr()} - {self.get_bez()}'

