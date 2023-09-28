import json

from ..entities.ERPAbstractEntity import ERPAbstractEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity, BridgeCategoryTranslation


class ERPArtikelKategorienEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="ArtikelKategorien",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def map_erp_to_bridge(self):
        # Erstellen einer neuen Instanz von BridgeCategoryEntity
        category_entity = BridgeCategoryEntity(
            erp_nr=self.get_("Nr"),
            erp_nr_parent=self.get_("ParentNr"),
            tree_path=json.dumps(self.get_category_nr_path()),
            created_at=self.get_("ErstDat"),
            edited_at=self.get_("AendDat")
        )

        # Erstellen einer neuen Instanz von BridgeCategoryTranslationEntity
        category_translation = BridgeCategoryTranslation(
            language='DE_de',  # Angenommen, dass die Sprache Deutsch ist, da das Feld im Dataset nicht spezifiziert ist
            name=self.get_("Bez"),
            description=self.get_("Info"),
            description_short=self.get_("Memo")  # Angenommen, dass Memo als kurze Beschreibung dient
        )

        # Verknüpfen der Translation mit der Kategorie
        category_entity.translations.append(category_translation)

        return category_entity

    def get_available_categories(self):
        """
        Retrieve the maximum available number of article categories from the ERP's special object.

        This method interacts with the 'soAppObject' special object in the ERP to determine
        the total available article categories.

        Returns:
            int or bool: The number of available article categories if successful, otherwise False.
        """
        try:
            # Get the 'soAppObject' using the method from the parent class
            erp_app = self.get_erp_app_object()

            # If the erp_app object is not available, return False
            if not erp_app:
                return False

            # Retrieve the maximum available article categories from the 'soAppObject'
            available_categories = erp_app.GetAppVar(self._erp_app_var["ArtikelKategorien"])

            # If the available categories are not fetched successfully, log a warning and return False
            if not available_categories:
                self.logger.warning("Unable to determine the available article categories.")
                return False

            # Log the successful retrieval of available categories
            self.logger.info(f"Successfully retrieved {available_categories} available article categories from the ERP.")

            return int(available_categories)

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the available article categories: {str(e)}")
            return False

    def get_category_nr_path(self):
        """
        Retrieve the category number path, convert it into a list of integers,
        and return the list. The first number in the path should also be the
        first number in the returned list.

        :return: A list of integers representing the category number path,
                 or an empty list if the path is None or cannot be processed.
        """
        try:
            # Retrieve the raw number path
            path_raw = self.get_("NrPath")  # e.g., "11/1/110"

            if path_raw:
                # Split the raw path string into a list of strings,
                # then convert each string to an integer
                path_list = [int(nr) for nr in path_raw.split('/')]

                # Log the successfully processed number path
                self.logger.info(f"Successfully processed number path: {path_list}")

                return path_list

            else:
                # Log a warning if path_raw is None or an empty string
                self.logger.warning("The number path is None or empty.")

        except ValueError as e:
            # Log an error if a part of the path is not convertible to an integer
            self.logger.error(f"Error converting number path to integers: {e}")

        except Exception as e:
            # Catch any other exceptions that may occur
            self.logger.error(f"An unexpected error occurred: {e}")
        # Return an empty list in case of an error or if path_raw is None or empty
        return []


