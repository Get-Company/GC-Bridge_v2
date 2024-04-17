import time
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
        bridge_entities = self._bridge_controller.get_entity().query.filter_by(active=True).all()

        for bridge_entity in bridge_entities:
            time.sleep(1)
            self.sync_one_from_bridge(bridge_entity=bridge_entity)

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

    def sync_one_from_bridge(self, bridge_entity):
        print(f"Entity: {bridge_entity.get_translation().get_name()}")
        result = self.downsert(bridge_entity=bridge_entity)
        return result

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
        """Performs an upsert operation on the bridge entity. Update entity if it exists, else create a new one.

        Args:
            bridge_entity: The entity to be updated or created.

        Returns:
            Result of the patch operation if the entity exists; result of the post operation otherwise.
        """

        try:
            sw6_payload_json = self.get_entity().map_bridge_to_sw6(bridge_entity)  # Map bridge entity to SW6 format
            is_in_sw6 = self.is_in_sw6(bridge_entity=bridge_entity)  # Check if entity exists in SW6

            if is_in_sw6:  # If entity exists in SW6 data
                sw6_json_data = self.get_entity().update(
                    sw6_json_data=is_in_sw6['data'],
                    bridge_entity=bridge_entity
                )  # Update entity data
                result = self.get_entity().patch_(sw6_json_data=sw6_json_data)  # Perform patch operation
                print(f"Updated Bridge Entity: {bridge_entity.get_sw6_id()}")
                return result

            else:  # If entity doesn't exist in SW6 data
                sw6_json_data = self.get_entity().map_bridge_to_sw6(
                    bridge_entity=bridge_entity)  # Map bridge entity to SW6 format
                result = self.get_entity().post_(sw6_json_data=sw6_json_data)  # Perform post operation
                print(f"Created Bridge Entity: {bridge_entity.get_sw6_id()}")
                return result
        except Exception as e:
            self.logger.error(f"Error while performing upsert operation: {e}")  # Log error

    @abstractmethod
    def is_in_db(self, bridge_entity_new, sw6_json_data):
        pass

    def is_in_sw6(self, bridge_entity):
        """
        Function to check if the entity is present in SW6 system.

        Args:
            self: An instance of the class.
            bridge_entity: An instance of the object.

        Returns:
            On success, it returns the response received from SW6 system.
            On failure, it returns None.
        """

        # Check if the provided bridge_entity has a sw6_id
        if not bridge_entity.get_sw6_id():
            # Log the missed sw6_id
            self.logger.warning("No sw6_id found")
            # Return None as there's no sw6_id provided
            return None

        try:
            # Attempt to get the entity with the given sw6_id
            response = self.get_entity().search_api_by_(index_field="id",
                                                        search_value=bridge_entity.get_sw6_id())
            if response:
                # Check if 'total' in response is 0 or 1
                total = response.get('total', 0)
                if total == 0:
                    return None  # if 'total' is 0, return response
                elif total == 1:
                    # Log the successful search
                    self.logger.info(f"Found {bridge_entity.get_sw6_id()} in SW6: {response}")
                    return response
                else:
                    raise ValueError(
                        f"Invalid 'total' value, expected either 0 or 1 on {self.get_entity()._endpoint_name} with id: {bridge_entity.get_sw6_id()}")  # raise error if 'total' is not 0 or 1
        except Exception as e:
            # Exception handling, logging the error message
            self.logger.error(f"Error on category search in sw6 by id: {bridge_entity.get_sw6_id()}, {str(e)}")

        # Return None in case of error or no response
        return None

    @abstractmethod
    def set_relations(self, bridge_entity, sw6_json_data):
        """
        This method calls the upsert method before setting the relation. Adjustments are necessary in some children

        :param bridge_entity:
        :param sw6_json_data:
        :return: bridge_entity
        """
        pass