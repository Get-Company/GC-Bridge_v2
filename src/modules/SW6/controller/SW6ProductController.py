from pprint import pprint

from ..controller.SW6AbstractController import SW6AbstractController
from ..entities.SW6ProductEntity import SW6ProductEntity
from ..controller.SW6MediaController import SW6MediaController
from src.modules.Bridge.controller.BridgeProductController import BridgeProductController


class SW6ProductController(SW6AbstractController):

    def __init__(self):

        self._bridge_controller = BridgeProductController()

        super().__init__(
            sw6_entity=SW6ProductEntity(),
            bridge_controller=self._bridge_controller
        )

    def is_in_db(self, bridge_entity_new, sw6_json_data):
        bridge_product_entity_in_db = self._bridge_controller.get_entity().query.filter_by(erp_nr=bridge_entity_new.erp_nr).one_or_nne()
        if bridge_product_entity_in_db:
            self.logger.info(f"Entity {bridge_entity_new.api_id} found in the db!")
            return bridge_product_entity_in_db
        else:
            self.logger.info(f"No Entity {bridge_entity_new.api_id} found in the db!")
            return None

    def set_relations(self, bridge_entity, sw6_json_data):
        pass

    def downsert(self, bridge_entity, set_relations=True):
        sw6_payload_json = self.get_entity().map_bridge_to_sw6(bridge_entity)
        SW6MediaController().upsert_product_media(bridge_entity=bridge_entity)

        result = self.get_entity().bulk_uploads(sw6_json_data=sw6_payload_json)
        # When both, product and media, are uploaded - relate them
        SW6MediaController().set_product_media_relation(bridge_entity=bridge_entity)
        self.set_cover_media(bridge_entity=bridge_entity)

        return result

    def set_cover_media(self, bridge_entity):
        bridge_media_cover_entity = bridge_entity.get_cover_image()
        result = self.get_entity().search_api_ids_by_(
            index_field=["productId", "mediaId"],
            search_value=[bridge_entity.get_sw6_id(), bridge_media_cover_entity.get_sw6_id()],
            endpoint_name="product-media"
        )
        if result['total'] == 1:
            self.get_entity().set_cover_media(bridge_entity=bridge_entity,product_media_id=result["data"][0])

    def deactivate_in_saleschannel(self, bridge_entity):
        sw6_entity = SW6ProductController().get_entity()

        assocs = bridge_entity.marketplace_prices_assoc
        for assoc in assocs:
            sw6_entity.delete_visibility(visibility_id=assoc.get_sw6_visibility_id())

        SW6ProductController().sync_one_from_bridge(bridge_entity=bridge_entity)

    def sync_sw6_ids(self):
        pass
