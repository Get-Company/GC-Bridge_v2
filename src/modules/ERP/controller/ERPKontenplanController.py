from ..controller.ERPConnectionController import ERPConnectionController
from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPKontenplanEntity import ERPKontenplanEntity


class ERPKontenplanController(ERPAbstractController):

    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPKontenplanEntity(
            search_value=search_value,
            index=index,
            range_end=range_end
        )
        self._bridge_controller = None

        super().__init__(
            dataset_entity=self._dataset_entity,
            bridge_controller=self._bridge_controller,
            search_value=search_value
        )

    def is_in_db(self, bridge_entity_new): pass

    """ Relations """
    def set_relations(self, bridge_entity): pass

    def get_entity(self):
        """
        Retrieve the dataset entity of the controller.

        Note: This method is an implementation of the abstract method defined in
        the parent class ERPAbstractController. For a detailed explanation of its purpose
        and behavior, please refer to the documentation in ERPAbstractController.

        Returns:
            Dataset entity.

        Raises:
            ValueError: If dataset entity is not set.
        """
        if self._dataset_entity:
            return self._dataset_entity
        else:
            message = "Dataset entity is not set"
            self.logger.warning(message)
            raise ValueError(message)


