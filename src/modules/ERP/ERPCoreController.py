from ..ModulesCoreController import ModulesCoreController
from ..ERP.controller.ERPConnectionController import ERPConnectionController

class ERPCoreController(ModulesCoreController):
    def __init__(self):

        self._current_erp_combined_id = None

        super().__init__()
    """     
    Abstract Methods, defined in ModulesCoreController
    These Methods must be overwritten. If there is no use of it simply do a pass!
    """

    def sync_all_to_bridge(self):
        pass

    def sync_all_from_bridge(self, bridge_entities):
        pass

    def sync_one_to_bridge(self):
        pass

    def sync_one_from_bridge(self, bridge_entity):
        pass

    def sync_changed_to_bridge(self):
        pass

    def sync_changed_from_bridge(self, bridge_entities):
        pass

    def update_erp_combined_id(self, adress_id=0, anschrift_id=0, ansprechpartner_id=0):
        # Check if current_erp_combined_id is None and set a default value if needed
        if self._current_erp_combined_id is None:
            self._current_erp_combined_id = '0;0;0'

        # Zerlegt die aktuelle self._current_erp_combined_id in eine Liste von Strings
        current_ids = self._current_erp_combined_id.split(';')

        # Überschreiben der Werte, die als Parameter gegeben wurden
        # 0 bedeutet, dass kein neuer Wert angegeben wurde
        if adress_id != 0:
            current_ids[0] = str(adress_id)
        if anschrift_id != 0:
            current_ids[1] = str(anschrift_id)
        if ansprechpartner_id != 0:
            current_ids[2] = str(ansprechpartner_id)

        # Setzen und Zurückgeben der aktualisierten self._current_erp_combined_id
        self._current_erp_combined_id = ';'.join(current_ids)
        return True

    def set_erp_combined_id(self, erp_combined_id):
        if erp_combined_id:
            self._current_erp_combined_id = erp_combined_id
        else:
            self.logger.error("No erp_combined_id was given:", erp_combined_id)

    def get_erp_combined_id_part(self, index):
        """
        Returns the corresponding part of the ERP combined ID based on the provided index.
        The index can be 0 (for 'address ID'), 1 (for 'an 'Anschrift' ID), or 2 (for 'Ansprechpartner' ID).
        If the ERP combined ID is not present or the provided index is not 0, 1, or 2, this method returns False.
        If the index part of the ERP combined ID is 0, this method returns None.

        Parameters:
            index (int): The index of the part of the ERP combined ID to return.
                         Can be 0, 1, or 2.

        Returns:
            str/bool/None: The corresponding part of the ERP combined ID or None if the part is 0.
                           If the ERP combined ID is not present or the provided index is not 0, 1, or 2, returns False.
        """
        index_names = {0: 'address ID', 1: 'Anschrift ID', 2: 'Ansprechpartner ID'}
        try:
            # Validate the index parameter
            if index in (0, 1, 2) and self._current_erp_combined_id:
                part = self._current_erp_combined_id.split(';')[index]
                return None if part == '0' else part
            else:
                print(f"Invalid index {index} or ERP combined ID is not set. Returning False.")
                return False
        except Exception as e:
            # Log and reraise the exception if there's an unhandled situation
            print(f"Exception when getting {index_names.get(index, 'unknown')} part from ERP combined ID: {e}")
            raise

    def get_erp_combined_id_address_id(self):
        """
        Returns the 'address ID' part of the ERP combined ID.
        If the ERP combined ID is not set or invalid, returns False.
        If the 'address ID' part of ERP combined ID is 0, returns None.
        """
        return self.get_erp_combined_id_part(0)

    def get_erp_combined_id_anschrift_id(self):
        """
        Returns the 'Anschrift ID' part of the ERP combined ID.
        If the ERP combined ID is not set or invalid, returns False.
        If the 'Anschrift ID' part of ERP combined ID is 0, returns None.
        """
        return self.get_erp_combined_id_part(1)

    def get_erp_combined_id_ansprechpartner_id(self):
        """
        Returns the 'Ansprechpartner ID' part of the ERP combined ID.
        If the ERP combined ID is not set or invalid, returns False.
        If the 'Ansprechpartner ID' part of ERP combined ID is 0, returns None.
        """
        return self.get_erp_combined_id_part(2)