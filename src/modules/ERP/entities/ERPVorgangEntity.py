from pprint import pprint

from .ERPAbstractEntity import ERPAbstractEntity
from .ERPArtikelEntity import ERPArtikelEntity


class ERPVorgangEntity(ERPAbstractEntity):
    def __init__(self, erp, search_value=None, index=None, range_end=None):
        """
        Initializer for ERPArtikelEntity.

        :param search_value: The value used for searching.
        :param index: The index for the dataset, defaults to 'Nr' if not provided.
        :param range_end: The range end value.
        """

        super().__init__(
            dataset_name="Vorgang",
            dataset_index=index or "BelegNr",
            erp=erp,
            search_value=search_value,
            range_end=range_end,
            filter_expression=None
        )

        self.order = None
        self.bridge_order = None  # Holds the order from the bridge
        self.erp_beleg_nr = None

    def get_erp_app_object_vorgang(self):
        """
        Retrieve the 'soAppObject' special object from the ERP.

        Returns:
            object or bool: The 'soAppObject' if successful, otherwise False.
        """
        try:
            # Fetch the special ERP object named 'soAppObject'
            erp_app = self._erp.GetSpecialObject(self._erp_special_objects["soVorgang"])

            # If the erp_app object is not available, log a warning and return False
            if not erp_app:
                self.logger.warning("Unable to fetch the 'soAppObject' from the ERP.")
                return None

            # Log the successful retrieval of 'soAppObject'
            self.logger.info(f"Successfully retrieved 'soAppObject' from the ERP.")

            return erp_app

        except Exception as e:
            self.logger.error(f"An error occurred while fetching the 'soAppObject': {str(e)}")
            return None

    def create_new_order(self, bridge_entity):
        self.order = self.get_erp_app_object_vorgang()
        try:
            if self.order:
                self.order.Append(113, bridge_entity.customer.get_erp_nr())
        except AttributeError:
            self.logger.error(f"'{self.order}' object has no attribute 'Append'.")
            return False

        self._created_dataset = self.order.DataSet

        order_nr = f"SW6_{bridge_entity.get_order_number()}"
        self.set_("AuftrNr", order_nr)
        self.set_("Bez", f"GC Webshop-Bestellung Nr. EC{order_nr} vom {bridge_entity.get_purchase_date()}")

        for detail in bridge_entity.order_details:
            self.add_order_positions(order_detail=detail)

        vorgang_nr = self.order.DataSet.Fields("BelegNr").AsString
        print("Vorgang:", vorgang_nr)

        self.order.Post()

        return True

    def map_erp_to_bridge(self):
        pass

    def map_bridge_to_erp(self, bridge_entity):
        try:
            self.bridge_order = bridge_entity
            self.order = self.get_erp_app_object_vorgang()

            self.order.Append(113, '10026')

            for order_detail in bridge_entity.order_details:
                self.add_order_positions(order_detail=order_detail)

            erp_order_id = self.order.DataSet.Fields['BelegNr'].AsString
            print(f"erp_order_id: {erp_order_id}")

            self._created_dataset = self.order.DataSet

            # Set additional information in 'AuftrNr' field
            self.set_('AuftrNr', "SW6_neu")
            self.set_('SuchBeg',"CLisoeup")

            # Save the order
            self.order.Post()

        except Exception as e:
            # If an error occurs while saving the order, cancel and resume
            self.order.Cancel()
            print(f"An error occurred while saving the order: {str(e)}")

        finally:
            # Clear the `order` attribute
            self.order = None

    def add_order_positions(self, order_detail):
        """
        Add order positions with details from bridge_entity_order_details.
        Args:
            bridge_entity_order_details (list): Details for each order position to add.
        """

        # Assume that pos_detail has 'quantity', 'unit', 'id', and 'price' fields
        erp_product = ERPArtikelEntity(search_value=order_detail.get_erp_nr())
        self.order.Positionen.Add(
            order_detail.get_quantity(),
            erp_product.get_unit(raw=True),
            order_detail.get_erp_nr()
        )
        self.order.Positionen.DataSet.Edit()

        # Set price for this item position
        EPr = self.order.Positionen.DataSet.Fields("EPr").GetEditObject(self._edit_objects_dict["etBetragGrp"])
        # EPr.GesNetto = order_detail.get_unit_price()
        EPr.GesNetto = order_detail.get_total_price()
        EPr.Save()

