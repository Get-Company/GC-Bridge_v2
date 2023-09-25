from ..controller.ERPAbstractController import ERPAbstractController
from ..entities.ERPArtikelEntity import ERPArtikelEntity
from ..entities.ERPArtikelKategorienEntity import ERPArtikelKategorienEntity


class ERPArtikelController(ERPAbstractController):
    """
    Examples:

        Get the Bez from the cat of the product 204116
        art_ctrl = ERPArtikelController(204116)
        categories = art_ctrl.get_categories()
        for cat in categories:
            print(ERPArtikelKategorienController(cat).get_entity().get_("Bez"))

        Get the images as a list
        art_ctrl = ERPArtikelController(204116)
        image_paths = art_ctrl.get_img>_files
        if image_paths:
            for img in image_paths:
                print(img)

        Get Tax informations
        art_ctrl = ERPArtikelController(204116)
        fields = art_ctrl.price_infos().items()
        for key,value in fields:
            print(f"{key}: {value}")

    """

    def __init__(self, search_value=None):
        self._dataset_entity = ERPArtikelEntity(search_value=search_value)
        self._category_dataset_entity = ERPArtikelKategorienEntity()

        super().__init__(
            dataset_entity=self._dataset_entity
        )

    def get_entity(self):
        """
        Retrieve the dataset entity of the controller.

        Note: This method is an implementation of the abstract method defined in
        the parent class ERPAbstractController. For a detailed explanation of its purpose
        and behavior, please refer to the documentation in ERPAbstractController.

        Returns:
            Dataset entity.

        Raises:
            ValueError: If dataset entity is not set.
        """
        if self._dataset_entity:
            return self._dataset_entity
        else:
            message = "Dataset entity is not set"
            self.logger.warning(message)
            raise ValueError(message)

    def get_umsatz(self,  jahr, return_field):
            ums = self._dataset_entity.get_nested_ums(jahr, return_field)
            if ums:
                self.logger.info(f"Umsatz retrieved successfully. {ums}")
            else:
                self.logger.warning("No Umsatz retrieved")
            return ums

    def get_categories(self):
        """
        Retrieve all the category numbers available in the ERP.

        This method fetches each category number from 'ArtKat1' up to the maximum available
        category number determined by the `get_available_categories` method.

        Returns:
            list[int] or bool: A list of all available category numbers if successful, otherwise False.

        Raises:
            Exception: If there's an issue retrieving the category numbers.
        """
        try:
            # Initialize the ERPArtikelKategorienEntity to fetch available categories

            available_categories = self._category_dataset_entity.get_available_categories()

            # If available_categories is False or not an integer, return False
            if not isinstance(available_categories, int):
                self.logger.warning("Unable to determine the total available categories.")
                return False

            # Retrieve each category number from 'ArtKat1' up to 'ArtKat{available_categories}'
            categories = [self.get_entity().get_(f"ArtKat{i}") for i in range(1, available_categories + 1)]

            # Remove empty or None category numbers from the list
            categories = [cat for cat in categories if cat]

            # Log the successful retrieval of category numbers
            self.logger.info(f"Successfully retrieved {len(categories)} category numbers from the ERP.")

            return categories

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the category numbers: {str(e)}")
            return False

    def category(self, catnr=None):
        if not catnr:
            categories = self.get_categories()
            catnr = categories[0]
        return ERPArtikelKategorienEntity(catnr)

    def price_infos(self):
        infos = {
            "Steuerschlüssel": self._dataset_entity.get_("StSchl"),
            "Steuerschlüsselart": self._dataset_entity.get_("StSchlArt"),
            "Steuerverteilung": self._dataset_entity.get_("StVert"),
            "Steuerverteilung Netto": self._dataset_entity.get_("StVertNt"),
            "Steuerverteilung Steuer": self._dataset_entity.get_("StVertSt"),
            "Steuerverteilung Brutto": self._dataset_entity.get_("StVertBt"),
        }
        return infos
