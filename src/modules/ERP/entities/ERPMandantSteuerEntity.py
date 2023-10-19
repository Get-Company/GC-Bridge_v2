from ..entities.ERPAbstractEntity import ERPAbstractEntity
from src.modules.Bridge.entities.BridgeTaxEntity import BridgeTaxEntity


class ERPMandantSteuerEntity(ERPAbstractEntity):
    def __init__(self, search_value=None, index=None, range_end=None):

        super().__init__(
            dataset_name="Mandant",
            dataset_index=index or "Nr",
            search_value=search_value,
            range_end=range_end
        )

    def get_tax_fields(self, stschl:int) -> dict:
        """
        Retrieves tax-related fields for a given tax identifier.

        Args:
            stschl (str): The tax identifier to search for.

        Returns:
            dict: A dictionary containing relevant tax fields.
        """
        try:
            tax_field = {
                "StSchl": self.get_nested_(nested_dataset_name="Ust", index_field="Nr", search_value=stschl, return_field="StSchl"),
                "Bez": self.get_nested_(nested_dataset_name="Ust", index_field="Nr", search_value=stschl, return_field="Bez"),
                "Sz": self.get_nested_(nested_dataset_name="Ust", index_field="Nr", search_value=stschl, return_field="Sz")
            }
            return tax_field
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving tax fields for StSchl {stschl}: {e}")
            raise

    def map_erp_to_bridge(self, stschl):
        tax_fields = self.get_tax_fields(stschl=stschl)
        tax_entity = BridgeTaxEntity(
            id=self.get_id(),
            erp_nr=tax_fields["StSchl"],
            description=tax_fields["Bez"],
            key=tax_fields["Sz"]
        )
        return tax_entity

    def __repr__(self):
        return f'Mandant'






