from ..entities.ERPAbstractEntity import ERPAbstractEntity


class ERPArtikelKategorienEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):
        super().__init__(
            dataset_name="ArtikelKategorien",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def get_parent_nr(self):
        """
        Retrieve the parent number of the current dataset.

        Returns:
            int: The parent number if found, otherwise False.

        Raises:
            Exception: If there's an issue retrieving the parent number.
        """
        try:
            parent_nr = self.get_("ParentNr")
            self.logger.info(f"Successfully retrieved ParentNr: {parent_nr} for dataset '{self._dataset_name}'.")
            return parent_nr
        except Exception as e:
            self.logger.error(f"Error on finding Parent of Nr {self.get_('Nr')} for dataset '{self._dataset_name}': {str(e)}")
            raise

    def has_parent(self):
        """
        Check if the current dataset has a parent.

        Returns:
            bool: True if the dataset has a parent, otherwise False.

        Raises:
            Exception: If there's an issue determining if the dataset has a parent.
        """
        try:
            parent_nr = self.get_parent_nr()
            if not parent_nr or parent_nr == 0:
                self.logger.info(f"Dataset '{self._dataset_name}' does not have a parent.")
                return False
            else:
                self.logger.info(f"Dataset '{self._dataset_name}' does have a parent. Parent ID: {parent_nr}")
                return True
        except Exception as e:
            self.logger.error(f"Error on determining if dataset '{self._dataset_name}' has a parent: {str(e)}")
            raise

    def get_category_path(self):
        """
        Retrieve the category path from the topmost to the lowest level.

        Returns:
            list[int]: A list of category numbers from topmost to lowest level.

        Raises:
            Exception: If there's an issue retrieving the category path.
        """
        try:
            nr_path_str = self.get_("NrPath")
            nr_path_list = [int(nr) for nr in nr_path_str.split('/') if nr]
            self.logger.info(f"Successfully retrieved category path for dataset '{self._dataset_name}': {nr_path_list}.")
            return nr_path_list
        except Exception as e:
            self.logger.error(f"Error on retrieving category path for dataset '{self._dataset_name}': {str(e)}")
            raise