from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPArtikelEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):

        super().__init__(
            dataset_name="Artikel",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def get_nested_ums(self, jahr, return_field):
        ums = self.get_nested_("Ums", "Jahr", jahr, return_field)
        return ums

    def get_nested_stgums(self, jahr, return_field):
        stg_ums = self.get_nested_("StGUms", "Jahr", jahr, return_field)
        return stg_ums

    def get_nested_sliums(self, jahr, return_field):
        """Stücklistenumsatz"""
        stg_ums = self.get_nested_("SLiUms", "Jahr", jahr, return_field)
        return stg_ums
