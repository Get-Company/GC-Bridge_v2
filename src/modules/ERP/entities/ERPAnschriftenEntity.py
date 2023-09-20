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

    def get_ansprechpartner_entity(self):
        return ERPAnsprechpartnerEntity(
            [
            self.get_("AdrNr"),
            self.get_("AnsNr"),
            self.get_("AspNr")
            ]
        )





