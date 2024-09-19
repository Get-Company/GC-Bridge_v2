from datetime import datetime, timedelta
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

    def sync_all_from_bridge(self, set_relations=True, offset=0):
        """
        Sync all active bridge entities. Time taken for each entity to sync and
        an estimated remaining time after each sync are printed.

        Args:
            set_relations (bool): If true, it sets a relation while syncing an entity. Defaults to True.
            start_from (string): the erp_nr from which to start syncing entities.

        Raises:
            Any exception raised during the synchronization process will be caught and logged.
            :param offset: Skipping value
        """
        try:
            # Querying active bridge entities
            bridge_entities = self._bridge_controller.get_entity().query.filter_by(is_active=True).all()
        except Exception as e:
            self.logger.error(f'Failed to query bridge entities. Error: {e}')
            return

        start = datetime.now()  # Records the start time
        times = []  # Stores time taken by each entity to sync

        for i, bridge_entity in enumerate(bridge_entities):
            if i > offset:
                start_entity = datetime.now()  # Records start time of an entity sync
                print("Sync:", bridge_entity.get_erp_nr())
                try:
                    self.sync_one_from_bridge(bridge_entity=bridge_entity, set_relations=set_relations)

                except Exception as e:
                    self.logger.error(f'Failed to sync entity: {bridge_entity}. Error: {e}')
                    continue

                time_entity = datetime.now() - start_entity  # Calculates time taken by an entity to sync
                times.append(time_entity)

                # Formatting and printing sync time
                m, s = divmod(round(time_entity.total_seconds()), 60)
                print(f"{bridge_entity.get_erp_nr()} {i + 1}/{len(bridge_entities)} took {m}:{s} to sync!")

                if i > 0:
                    # Estimating and printing remaining time based on average sync time
                    avg_time = sum(times, timedelta()).total_seconds() / len(times)
                    estimated_time = round((len(bridge_entities) - (i + 1)) * avg_time)
                    est_m, est_s = divmod(estimated_time, 60)
                    print(f"Remaining: {est_m}:{est_s}")
            else:
                print(f"Skip {i} until Offset: {offset}")
                continue

        # Calculating, formatting and printing total sync time
        total_time = round((datetime.now() - start).total_seconds())
        total_m, total_s = divmod(total_time, 60)
        print(f"The total time for all entities to sync is {total_m} minutes {total_s} seconds.")

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

    def sync_one_from_bridge(self, bridge_entity, set_relations=True):
        print(f"Entity: {bridge_entity.get_translation().get_name()}")
        result = self.downsert(bridge_entity=bridge_entity, set_relations=set_relations)
        return result

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self):
        pass

    def get_entity(self):
        return self._sw6_entity

    def upsert(self, sw6_json_data):
        """
        Tries to either update(push) an existing bridge entity in the database, or insert a new one if it does not exist yet.

        Arguments:
            sw6_json_data: The JSON data of the bridge entity to be updated or inserted.

        Returns:
            The ID of the bridge entity in the database, if the operation is successful. None otherwise.
        """

        # Try to map the input data for a new bridge entity
        try:
            bridge_entity_new = self._sw6_entity.map_sw6_to_bridge(sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed to map SW6 to new BridgeEntity: {e}")
            return

        # Try to check if an existing entity can be found in the database
        try:
            bridge_entity_in_db = self.is_in_db(bridge_entity_new=bridge_entity_new, sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed to check if entity exists in DB: {e}")
            return

        # If an entity is found, prepare to update it
        if bridge_entity_in_db:
            self.logger.info(f"Prepare Update: {bridge_entity_in_db}")
            bridge_entity_for_db = bridge_entity_in_db.update(bridge_entity_new=bridge_entity_new)
            self.db.session.merge(bridge_entity_in_db)
        # Else, prepare to insert the new entity
        else:
            self.logger.info(f"Prepare Insert: {bridge_entity_in_db} ")
            bridge_entity_for_db = bridge_entity_new
            self.db.session.add(bridge_entity_for_db)

        # Try to flush the session to apply the modifications above
        try:
            self.db.session.flush()
        except Exception as e:
            self.logger.error(f"Failed to flush DB session: {e}")
            return

        # Try to retrieve the entity back from the session to get its ID after the flush operation
        try:
            self.db.session.refresh(bridge_entity_for_db)
            id = bridge_entity_for_db.id
        except Exception as e:
            self.logger.error(f"Failed to refresh entity: {e}")
            return

        # Add the entity back after refresh to ensure the session is updated
        self.db.session.add(bridge_entity_for_db)

        # Try to set relations for the entity
        try:
            self.logger.info("Set relations for the entity.")
            bridge_entity_for_db_with_relations = self.set_relations(bridge_entity=bridge_entity_for_db,
                                                                     sw6_json_data=sw6_json_data)
        except Exception as e:
            self.logger.error(f"Failed to set entity relations: {e}")
            return

        # Try to merge the updated entity into the session
        try:
            self.db.session.merge(bridge_entity_for_db_with_relations)
        except Exception as e:
            self.logger.error(f"Failed to merge entity with its relations into the session: {e}")
            return

        # Try to commit the session to finalize changes
        try:
            self.db.session.commit()
            return id
        except Exception as e:
            self.logger.error(f"Failed to commit changes to DB: {e}")

    def downsert(self, bridge_entity, set_relations=True):
        """Performs an upsert operation on the bridge entity. Update entity if it exists, else create a new one.

        Args:
            bridge_entity: The entity to be updated or created.

        Returns:
            Result of the patch operation if the entity exists; result of the post operation otherwise.
            :param bridge_entity:
            :param set_relations:
        """

        try:
            # sw6_payload_json = self.get_entity().map_bridge_to_sw6(bridge_entity)  # Map bridge entity to SW6 format
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