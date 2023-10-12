from ..BridgeCoreController import BridgeCoreController
from src import db


class BridgeAbstractController(BridgeCoreController):
    def __init__(self, bridge_entity):
        super().__init__()
        self._bridge_entity = bridge_entity
        self.db = db

    def delete_all(self, buffer_size=100):
        """
        Deletes all entries associated with the bridge entity from the database.

        :param buffer_size: Number of entities to delete before committing to the database.
        """
        try:
            self._bridge_entity.query.delete()
            self._commit_and_close()
            # Commit any remaining entities
            self.logger.info(f"Commit after deleting all entities.")
            self._commit_and_close()
        except Exception as e:
            self.logger.error(f"Error deleting entities: {str(e)}")
            self.db.session.rollback()

    def _commit_and_close(self):
        """
        Commits the changes to the database and closes the session.
        """
        try:
            self.db.session.commit()
        except Exception as e:
            self.logger.error(f"Error committing changes to database: {str(e)}")
            self.db.session.rollback()
            raise
        finally:
            self.db.session.close()
