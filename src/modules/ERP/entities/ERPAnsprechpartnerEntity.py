from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPAnsprechpartnerEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="Ansprechpartner",
            dataset_index=index or "AdrNrAnsNrAspNr",
            search_value=search_value,
            range_end=range_end
        )

    def __repr__(self):
        return f'Ansprechpartner'