from abc import abstractmethod
from pprint import pprint

from src import db
from ..SW6CoreController import SW6CoreController


class SW6AbstractController(SW6CoreController):
    def __init__(self, sw6_entity, bridge_controller=None):
        self._sw6_entity = sw6_entity
        self.db = db
        self.db.session.autoflush = False
        self._bridge_controller = bridge_controller
        super().__init__()

    def sync_all_to_bridge(self, **kwargs):
        pass

    def sync_all_from_bridge(self):
        # sw6_json_list = self.get_entity().get_api_list()
        # for sw6_json_data in sw6_json_list["data"]:
        #     self.downsert(sw6_json_data=sw6_json_data)
        pass

    def sync_one_to_bridge(self, sw6_json_data=None, sw6_entity_id=None):
        if sw6_json_data:
            bridge_entity_id = self.upsert(sw6_json_data=sw6_json_data)
            if bridge_entity_id:
                return bridge_entity_id

        if sw6_entity_id:
            sw6_json_data = self.get_entity().get_api_(id=sw6_entity_id)
            bridge_entity_id = self.upsert(sw6_json_data=sw6_json_data['data'])
            if bridge_entity_id:
                return bridge_entity_id

        if not sw6_json_data and not sw6_entity_id:
            self.logger.error("Neither sw6_json_data nor sw6_entity_id are set. Set at least 1 of them")
            return

    def sync_one_from_bridge(self, bridge_id):
        bridge_entity =self._bridge_controller.get_entity().query.get(bridge_id)
        if bridge_entity:
            self.downsert(bridge_entity)

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass

    def get_entity(self):
        return self._sw6_entity

    def upsert(self, sw6_json_data):
        try:
            # Map the data to a new bridge entity
            bridge_entity_new = self._sw6_entity.map_sw6_to_bridge(sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed to map SW6 to new BridgeEntity: {e}")
            return

        try:
            # Check for existing entity
            bridge_entity_in_db = self.is_in_db(bridge_entity_new=bridge_entity_new, sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed to check if entity exists in DB: {e}")
            return

        if bridge_entity_in_db:
            self.logger.info(f"Prepare Update: {bridge_entity_in_db}")
            bridge_entity_for_db = bridge_entity_in_db.update(bridge_entity_new=bridge_entity_new)
            self.db.session.merge(bridge_entity_in_db)
        else:
            self.logger.info(f"Prepare Insert: {bridge_entity_in_db} ")
            bridge_entity_for_db = bridge_entity_new
            self.db.session.add(bridge_entity_for_db)

        try:
            # Flush it first, for we have the relations to set
            self.db.session.flush()
        except Exception as e:
            self.logger.error(f"Failed to flush DB session: {e}")
            return

        try:
            # Refresh the entity, to get it back from the flush with its id
            self.db.session.refresh(bridge_entity_for_db)
            id = bridge_entity_for_db.id
        except Exception as e:
            self.logger.error(f"Failed to refresh entity: {e}")
            return

        self.db.session.add(bridge_entity_for_db)

        try:
            # Set relations
            self.logger.info("Set relations for the entity.")
            bridge_entity_for_db_with_relations = self.set_relations(bridge_entity=bridge_entity_for_db, sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed to set entity relations: {e}")
            return
        try:
            self.db.session.merge(bridge_entity_for_db_with_relations)
        except Exception as e:
            self.logger.error(f"Failed to merge entity with its relations into the session: {e}")
            return
        try:
            self.db.session.commit()
            return id
        except Exception as e:
            self.logger.error(f"Failed to commit changes to DB: {e}")

    def downsert(self, bridge_entity):

        sw6_json_data = self.get_entity().map_bridge_to_sw6(bridge_entity)
        pprint(sw6_json_data)
        return True


    @abstractmethod
    def is_in_db(self, bridge_entity_new, sw6_json_data):
        pass

    def is_in_sw6(self, bridge_entity):
        pass

    @abstractmethod
    def set_relations(self, bridge_entity, sw6_json_data):
        """
        This method calls the upsert method before setting the relation. Adjustments are necessary in some children

        :param bridge_entity:
        :param sw6_json_data:
        :return: bridge_entity
        """
        pass