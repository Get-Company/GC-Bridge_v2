from pprint import pprint

from ..entities.SW6AbstractEntity import SW6AbstractEntity
from src.modules.Bridge.entities.BridgeCategoryEntity import BridgeCategoryEntity
from lib_shopware6_api_base import Criteria, EqualsFilter


class SW6CategoryEntity(SW6AbstractEntity):
    def __init__(self):
        self.endpoint_name = "category"
        super().__init__(endpoint_name=self.endpoint_name)

    def map_bridge_to_sw6(self, bridge_entity):

        # Normal mapping
        payload = {
            'id': bridge_entity.get_sw6_id(),
            'displayNesteProducts': True,
            'type': 'page',
            'productAssignmentType': 'product',
            'name': bridge_entity.get_translation().get_name()
        }

        # Translations
        # payload.update(
        #     {
        #         'translations': self.get_translations(
        #             bridge_entity=bridge_entity
        #         )
        #     }
        # )

        # Parent SW6 id
        if bridge_entity.get_cat_parent_nr() is not None:
            try:
                parent_category_entity = BridgeCategoryEntity().query.filter_by(cat_nr=bridge_entity.get_cat_parent_nr()).one_or_none()
                payload.update(
                    {
                        'parentId': parent_category_entity.get_sw6_id()
                    }
                )
            except Exception as e:
                print(f"Error on fetching sw6_id from cat_nr {bridge_entity.get_cat_nr()} of parent_cat_nr {bridge_entity.get_cat_parent_nr()}, {e} ")

        return payload

    def get_translations(self, bridge_entity):
        translations = {
            "de-DE": {
                "name": bridge_entity.get_translation().get_name(),
                "description":bridge_entity.get_translation().get_description()
            },
            "en-GB": {
                "name": self.ai_translate_to(
                    text=bridge_entity.get_translation().get_name(),
                    language="GB_en"
                ),
                "description": self.ai_translate_to(
                    text=bridge_entity.get_translation().get_description(),
                    language="GB_en"
                )
            },
            "es-ES": {
                "name": self.ai_translate_to(
                    text=bridge_entity.get_translation().get_name(),
                    language="ES_es"
                ),
                "description": self.ai_translate_to(
                    text=bridge_entity.get_translation().get_description(),
                    language="ES_es"
                )
            },
            "fr-FR": {
                "name": self.ai_translate_to(
                    text=bridge_entity.get_translation().get_name(),
                    language="FR_fr"
                ),
                "description": self.ai_translate_to(
                    text=bridge_entity.get_translation().get_description(),
                    language="FR_fr"
                )
            }
        }
        return translations

    def is_in_sw6(self, bridge_entity):
        pprint(bridge_entity.get_tree_path_names_as_list())
        payload = Criteria()
        if bridge_entity.get_translation().get_sw6_id():
            print("Search SW6Category by ID:", bridge_entity.get_translation().get_sw6_id())
            payload.filter.append(EqualsFilter(field='id', value=bridge_entity.get_translation().get_sw6_id()))
        else:
            print("Search SW6Category by name:", bridge_entity.get_translation().get_name())
            payload.filter.append(EqualsFilter(field='name', value=bridge_entity.get_translation().get_name()))

        payload.associations["parent"] = Criteria()

        endpoint = self.sw6_client.request_post(f"/search/{self._endpoint_name}", payload=payload)
        return endpoint

