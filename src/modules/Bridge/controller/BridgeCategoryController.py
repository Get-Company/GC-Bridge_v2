from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeCategoryEntity import BridgeCategoryEntity
import json
import pandas as pd


class BridgeCategoryController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeCategoryEntity()
        super().__init__(bridge_entity=self._bridge_entity)

    def get_entity(self):
        return BridgeCategoryEntity()

    def get_main_category(self, tree_path):
        tree_path_list = json.loads(tree_path)
        main_category_id = tree_path_list[0]
        main_category = self._bridge_entity.query.filter_by(erp_nr=main_category_id).one_or_none()
        if main_category:
            return main_category
        else:
            return None

    def import_new_erp_ids(self):
        df = pd.read_excel("D:\\htdocs\\python\\GC-Bridge_v2\\categories_mix.xlsx")
        df = df.astype(int)
        for index, row in df.iterrows():
            try:

                nr = row['nr']
                nr_new = row['nr_new']
                nr_new_parent = row['nr_new_parent']

                print(f"Nr: {nr} wird zu {nr_new}")

                bridge_row = BridgeCategoryEntity().query.filter_by(erp_nr=nr).one_or_none()
                if bridge_row:
                    bridge_row.set_cat_nr(value=nr_new)
                    bridge_row.set_cat_parent_nr(value=nr_new_parent)
                    self.db.session.add(bridge_row)
                    self.db.session.commit()
            except Exception as e:
                print(f"Fehler beim Import: {e}")

        return True

