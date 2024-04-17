from pprint import pprint
from datetime import datetime
# Handbuch 3.1.72
from .ERPAbstractController import ERPAbstractController
from .ERPConnectionController import ERPConnectionController
from ..entities.ERPVorgangEntity import ERPVorgangEntity
from .ERPArtikelController import ERPArtikelController
from src.modules.Bridge.controller.BridgeOrderController import BridgeOrderController
from src.modules.Bridge.controller.BridgeCustomerController import BridgeCustomerController
from .ERPAdressenController import ERPAdressenController


class ERPVorgangController(ERPAbstractController):
    def __init__(self, search_value=None, index=None, range_end=None):
        self._dataset_entity = ERPVorgangEntity(
            search_value=search_value,
            index=index,
            range_end=range_end
        )
        self._bridge_controller = BridgeOrderController()

        super().__init__(
            dataset_entity=self._dataset_entity,
            bridge_controller=self._bridge_controller,
            search_value=search_value
        )

    def downsert(self, bridge_entity):
        """ Timer Start """
        before = datetime.now()
        """ Timer Start """

        # 1 downsert customer
        bridge_customer_entity = ERPAdressenController().sync_order_addresses_from_bridge(
            bridge_entity=bridge_entity.customer,
            bridge_marketplace_entity=bridge_entity.marketplace
        )
        #
        # print(f"Customer {bridge_customer_entity.get_erp_nr()} ready. Now to the orders:")

        # 2 downsert order
        # for detail in bridge_entity.order_details:
        #     print(f"ArtNr: {detail.get_erp_nr()} Quantity: {detail.get_quantity()} - Sum: {detail.get_total_price()} ")
        erp_vorgang_entity = ERPVorgangController().sync_one_from_bridge(bridge_entity=bridge_entity)

        """ Timer End """
        after = datetime.now()
        time = after - before
        print(f"The script took {time}")
        """ Timer End """

    def get_entity(self):
        return self._dataset_entity

    def is_in_db(self, bridge_entity_new):
        pass

    def set_relations(self, bridge_entity):
        pass

    """ 
    Downsert
    """
    def sync_one_from_bridge(self, bridge_entity):
        erp_vorgang_entity = self.get_entity()
        erp_vorgang_entity.create_new_order(bridge_entity=bridge_entity)

        # erp_vorgang_beleg_nr = erp_vorgang_entity.get_beleg_nr()
        # print("Vorgang angelegt mit BelegNr:", erp_vorgang_beleg_nr)
        #
        # for detail in bridge_entity.order_details:
        #     erp_artikel_entity = ERPArtikelController().get_entity()
        #     unit = detail.get_unit()
        #     found = erp_artikel_entity.find_one(search_value=detail.get_erp_nr())
        #     if found:
        #         unit = erp_artikel_entity.get_unit(raw=True)
        #         print("Unit:", unit)
        #
        #     erp_vorgang_positionen_obj.Positionen.Add(detail.get_quantity(), unit, detail.get_erp_nr())
        #
        # erp_vorgang_positionen_obj.Post()

        return True

    def __del__(self):
        print("ERPVorgangEnity del called.")
        erp_co_ctrl = ERPConnectionController()

        erp_co_ctrl.close()

