from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPArtikelKategorienEntity(ERPAbstractEntity):
    def __init__(self, search_value=None):
        # the first value should be the most used index_field
        # If the value for the field isn't given, the very first item is used [0]
        self.index_field = "Nr"
        self.dataset_name = 'ArtikelKategorien'

        super().__init__(
            dataset_name=self.dataset_name,
            index_field=self.index_field,
            search_value=search_value
        )

    def get_parent_nr(self, current_nr=None):
        if current_nr:
            self.set_search_value(search_value=current_nr)
        try:
            parent_nr = self.get_(search_value=self.get_search_value(), return_field="ParentNr")
            return parent_nr
        except Exception as e:
            print("Error on finding Parent of Nr", current_nr, e)

    def has_parent(self, current_nr):
        try:
            parent_nr = self.get_parent_nr(current_nr=current_nr)
            if not parent_nr or parent_nr != 0:
                return False
            else:
                return True
        except Exception as e:
            print("Error on finding Parent and returning Ture/False of Nr", current_nr, e)






