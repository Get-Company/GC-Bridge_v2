import json
from config import ERPConfig

from ..entities.ERPAbstractEntity import ERPAbstractEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity, BridgeCategoryTranslation
from src.modules.Bridge.entities.BridgeMediaEntity import BridgeMediaEntity


class ERPArtikelKategorienEntity(ERPAbstractEntity):
    """
    Representation of an ERP article categories entity inherited from ERPAbstractEntity.
    """

    def __init__(self, search_value=None, index=None, range_end=None):
        """
        Initializer for ERPArtikelKategorienEntity.

        :param search_value: The value used for searching.
        :param index: The index for the dataset, defaults to 'Nr' if not provided.
        :param range_end: The range end value.
        """
        super().__init__(
            dataset_name="ArtikelKategorien",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def map_erp_to_bridge(self):
        """
        Maps the current ERP article categories entity to a BridgeCategoryEntity.

        :return: A BridgeCategoryEntity instance with mapped values.
        """
        try:
            # Create a new instance of BridgeCategoryEntity
            category_entity = BridgeCategoryEntity(
                id=self.get_id(),
                erp_nr=self.get_erp_nr(),
                erp_nr_parent=self.get_erp_nr_parent(),
                tree_path=json.dumps(self.get_category_nr_path()),
                created_at=self.get_erstdat(),
                edited_at=self.get_aenddat()
            )
            self.logger.info(f"Category Enitiy mapped: {category_entity.id}:{category_entity.erp_nr}")

            cat_nr_path = self.get_category_nr_path()
            # Get the first and root element of the tree path.
            # Use the emthod get_languge_for_value classmethod in config.py to get the corresponding language
            language = ERPConfig.get_language_for_value(int(cat_nr_path[0]))

            category_translation = BridgeCategoryTranslation(
                language=language,
                name=self.get_name(),
                description=self.get_description(),
                description_short=self.get_description(),
                created_at=self.get_erstdat(),
                edited_at=self.get_aenddat()
            )

            # Create image entities and assign them
            medias = self.get_images_file_list()
            if medias:
                for media in medias:
                    name = self.get_med_file_name(media)
                    med = BridgeMediaEntity(
                        file_name=name,
                        file_type=self.get_med_file_type(media),
                        file_size=self.get_med_file_size(media),
                        title=name,
                        description=name
                    )
                    category_entity.media.append(med)

            self.logger.info(f"Category Translation Entity mapped: {category_translation.language} - {category_translation.name}")
            # Link the translation with the category
            category_entity.translations.append(category_translation)
            self.logger.info(f"Category Translation Entity appended to Category Entity.")
            return category_entity
        except Exception as e:
            self.logger.error(f"Error mapping ERPArtikelKategorien to Bridge: {str(e)}")
            return None

    def get_erp_nr(self):
        """
        Fetches the ERP number from the dataset.

        :return: ERP number.
        """
        return self.get_("Nr")

    def get_erp_nr_parent(self):
        """
        Fetches the parent ERP number from the dataset.

        :return: Parent ERP number.
        """
        return self.get_("ParentNr")

    def get_name(self):
        """
        Fetches the name/label from the dataset.

        :return: Name/label.
        """
        return self.get_("Bez")

    def get_description(self):
        """
        Fetches the information from the dataset.

        :return: Information.
        """
        return self.get_("Info")

    def get_memo(self):
        """
        Fetches the memo field from the dataset, assumed to serve as a short description.

        :return: Memo/short description.
        """
        return self.get_("Memo")

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

    def __repr__(self):
        return f'ArtikelKategorie {self.get_erp_nr() } - {self.get_name()}'


