from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPArtikelKategorienEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="ArtikelKategorien",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

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