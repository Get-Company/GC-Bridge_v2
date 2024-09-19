from pprint import pprint

from sqlalchemy import asc, text, case

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

    def build_tree(self, parent_id=None):
        """ Recursive function to build category tree. """
        tree = []

        # Fetch categories with the given parent_id and order them by after_category_id
        categories = (BridgeCategoryEntity.query
                      .filter_by(parent_category_id=parent_id)
                      .order_by(asc(BridgeCategoryEntity.after_category_id))
                      .all())

        for category in categories:
            # Add category node
            node = {
                'data': {
                    'type_of': 'category',
                    'id': category.id,
                    'after_category_id': category.after_category_id,
                    'parent_category_id': category.parent_category_id,
                    'title': category.get_translation().get_name(),
                    'sw6_id': category.sw6_id,
                },
                'nodes': []  # Initialize nodes as empty, products or sub-categories will be added next
            }

            # Add related products as nodes under the category
            # if category.products:
            #     for product in category.products:
            #         prod_cat_assoc = category.get_prod_cat_assoc(product)
            #
            #         product_node = {
            #             'data': {
            #                 'id': product.get_id(),
            #                 'type_of': 'product',
            #                 'title': product.get_translation().get_name(),
            #                 # Replace with your method to get product name
            #                 'category_id': category.get_id(),  # Assuming we use the same ERP number
            #                 'sort': prod_cat_assoc.get_sort(),
            #             },
            #             'nodes': []  # Products don't have child nodes
            #         }
            #         node['nodes'].append(product_node)  # Add product nodes under the category node

            # Recursive call for child categories and add them under the category node
            node['nodes'].extend(self.build_tree(category.id))

            # Add the fully constructed category node to the tree
            tree.append(node)

        return tree

    def move_category(self, moved, source, target, target_next_node):
        print("Moved:")
        pprint(moved)
        print("Source:")
        pprint(source)
        print("Target")
        pprint(target)
        print("Target Next Node:")
        pprint(target_next_node)

        moved_entity = self.get_entity().query.get(moved['id'])
        # To move a category element, we need to do 3 things:
        # 1. Set the after_category_id of the former next element
        old_next_entity = BridgeCategoryEntity.query.filter_by(after_category_id=moved['id']).first()
        print("Old Next Entity:")
        pprint(old_next_entity)
        # 2. Set the after_category_id of the moved element
        # 3. Set the after_category_id of the new next element
        return True

    def __repr__(self):
        return f'Bridge Category Entity ID: {self.id} - ERPNr: {self.erp_nr} - CatNr: {self.cat_nr}'

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

    def sync_all_to_bridge(self):
        print("No Categories in ERP. Bridge is handling all of them!")
        return True

    def sync_one_to_bridge(self):
        print("No Categories in ERP. Bridge is handling all of them!")
        return True

    def sync_changed_to_bridge(self):
        print("No Categories in ERP. Bridge is handling all of them!")
        return True

    def sync_changed_from_bridge(self):
        print("No Categories in ERP. Bridge is handling all of them!")
        return True

    def sync_all_from_bridge(self):
        print("No Categories in ERP. Bridge is handling all of them!")
        return True

    def sync_one_from_bridge(self):
        print("No Categories in ERP. Bridge is handling all of them!")
        return True
