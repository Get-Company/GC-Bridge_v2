from pprint import pprint

from sqlalchemy.exc import NoResultFound, MultipleResultsFound

import config
from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPLagerEntity import ERPLagerEntity


class ERPLagerController(ERPAbstractController):
    """

    """
    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPLagerEntity(
            search_value=search_value,
            index=index,
            range_end=range_end
        )
        self._bridge_controller = None

        super().__init__(
            dataset_entity=self._dataset_entity,
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new):
        pass

    def get_entity(self):
        return self._dataset_entity

    def set_relations(self, bridge_entity):
        pass
