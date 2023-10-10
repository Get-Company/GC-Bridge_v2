from ..BridgeCoreController import BridgeCoreController
from src import db


class BridgeAbstractController(BridgeCoreController):
    def __init__(self, bridge_entity):
        super().__init__()
        self._bridge_entity = bridge_entity

    def delete_all(self, buffer_size=100):
        """
        Deletes all entries associated with the bridge entity from the database.

        :param buffer_size: Number of entities to delete before committing to the database.
        """
        try:
            bridge_entities = self._bridge_entity.query.all()
            total_entities = len(bridge_entities)

            for index, bridge_entity in enumerate(bridge_entities, 1):
                self.logger.info(f"Deleting {bridge_entity}")
                db.session.delete(bridge_entity)

                # Print the current entity
                print(bridge_entity)

                # Commit every buffer_size entities
                if index % buffer_size == 0:
                    self.logger.info(f"Committing after {index} of {total_entities} entities (buffer size: {buffer_size}).")
                    self._commit_and_close()

            # Commit any remaining entities
            self.logger.info(f"Final commit after deleting all {total_entities} entities.")
            self._commit_and_close()
        except Exception as e:
            self.logger.error(f"Error deleting entities: {str(e)}")
            db.session.rollback()

    def _commit_and_close(self):
        """
        Commits the changes to the database and closes the session.
        """
        try:
            db.session.commit()
        except Exception as e:
            self.logger.error(f"Error committing changes to database: {str(e)}")
            db.session.rollback()
            raise
        finally:
            db.session.close()
