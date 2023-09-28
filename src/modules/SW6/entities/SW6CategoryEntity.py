from ..entities.SW6AbstractEntity import SW6AbstractEntity


class SW6CategoryEntity(SW6AbstractEntity):
    def __init__(self):
        self.endpoint_name = "category"
        super().__init__(endpoint_name=self.endpoint_name)

    def get_category_by_name(self, name):
        """Retrieves a category by its ID.

        Args:
            id (str): The ID of the category to retrieve.

        Returns:
            dict: The JSON response from the API.
        """
        self.set_filter("equals", "attributes.name", name)

        return self.get_list()

