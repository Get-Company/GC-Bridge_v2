import datetime
import os
from pprint import pprint
import requests

from ..entities.ERPAbstractEntity import ERPAbstractEntity
from config import ERPConfig, GCBridgeConfig

class ERPLagerEntity(ERPAbstractEntity):
    """
    Representation of an ERP lager entity inherited from ERPAbstractEntity.
    """

    def __init__(self, search_value=None, index=None, range_end=None):
        """
        Initializer for ERPLagerEntity.

        :param search_value: The value used for searching.
        :param index: The index for the dataset, defaults to 'Nr' if not provided.
        :param range_end: The range end value.
        """
        super().__init__(
            dataset_name="Lager",
            dataset_index=index or "ArtNrLagNr",
            search_value=search_value,
            range_end=range_end
        )

    def map_erp_to_bridge(self):
        pass

    def get_id(self):
        """
        Fetches the ID from the dataset.
        :return: ID or None if the value is None or can't be converted to an integer.
        """
        try:
            id_value = self.get_("ID")
            if id_value is None:
                self.logger.warning("ID is empty.")
                return None

            return int(id_value)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{id_value}' into an integer for ID.")
            return None

    def get_description(self):
        """
        Fetches the description (Bezeichnung) from the dataset.
        :return: Description or None if not found or an error occurs.
        """
        try:
            bez = self.get_("Bez")
            if bez is None:
                self.logger.warning("Bezeichnung is empty.")
                return None
            return str(bez)
        except Exception as e:
            self.logger.error(f"An error occurred while retrieving the description: {str(e)}")
            return None

    def get_stock(self):
        """
        Fetches the stock quantity (Lagermenge) from the dataset.
        :return: Stock quantity as an integer or None if the value is None or can't be converted to an integer.
        """
        try:
            mge = self.get_("Mge")
            if mge is None:
                self.logger.warning("Lagermenge is empty.")
                return None

            return int(mge)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{mge}' into an integer for stock quantity.")
            return None

    def get_lagernummer(self):
        """
        Fetches the Lager number (Lagernummer) from the dataset.
        :return: Lager number as a string or None if not found.
        """
        lagernummer = self.get_("LagNr")
        if lagernummer is None:
            self.logger.warning("Lagernummer is empty.")
            return None

        return str(lagernummer)

    def get_position(self):
        """
        Fetches the position (Pos) from the dataset.
        :return: Position as a string or None if not found.
        """
        pos = self.get_("Pos")
        if pos is None:
            self.logger.warning("Position (Pos) is empty.")
            return None

        return str(pos)

    """
    Inventur
    """
    def get_inventurmenge_gueltig(self):
        """
        Fetches the validity of inventory quantity (Inventurmenge gültig).
        :return: Boolean indicating if inventory quantity is valid or None if not found.
        """
        inv_mge_kz = self.get_("InvMgeKz")
        if inv_mge_kz is None:
            self.logger.warning("Inventurmenge gültig is empty.")
            return None

        return bool(inv_mge_kz)

    def get_inventurmenge(self):
        """
        Fetches the inventory quantity (Inventurmenge).
        :return: Inventory quantity as a double or None if the value is None or can't be converted.
        """
        try:
            inv_mge = self.get_("InvMge")
            if inv_mge is None:
                self.logger.warning("Inventurmenge is empty.")
                return None

            return float(inv_mge)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{inv_mge}' into a double for Inventurmenge.")
            return None

    def get_inventurdatum(self):
        """
        Fetches the inventory date (Inventurdatum) from the dataset.
        :return: Inventory date as a datetime object or None if not found or can't be parsed.
        """
        try:
            inv_dat = self.get_("InvDat")
            if inv_dat:
                # Convert pywintypes.datetime to standard datetime.datetime
                inv_dat = datetime.datetime(inv_dat.year, inv_dat.month, inv_dat.day)
                return inv_dat
            else:
                self.logger.warning("Inventurdatum is empty.")
                return None
        except (ValueError, IndexError, TypeError) as e:
            self.logger.error(f"An error occurred while processing the Inventurdatum: {str(e)}")
            return None

    def get_lagermenge_bei_inventur(self):
        """
        Fetches the stock quantity at the time of inventory entry (Lagermenge bei Eintragung der Inventurmenge).
        :return: Stock quantity as a double or None if the value is None or can't be converted.
        """
        try:
            inv_lag_mge = self.get_("InvLagMge")
            if inv_lag_mge is None:
                self.logger.warning("Lagermenge bei Eintragung der Inventurmenge is empty.")
                return None

            return float(inv_lag_mge)
        except (ValueError, TypeError):
            self.logger.error(f"Error on converting '{inv_lag_mge}' into a double for Lagermenge bei Eintragung der Inventurmenge.")
            return None

    def __repr__(self):
        return f'Artikel {self.get_nr()} - {self.get_name()}'

