from datetime import datetime
from pprint import pprint

from .BridgeAbstractController import BridgeAbstractController
from ..entities.BridgeOrderEntity import BridgeOrderEntity


class BridgeOrderController(BridgeAbstractController):
    def __init__(self):
        self._bridge_entity = BridgeOrderEntity()
        super().__init__(bridge_entity=self._bridge_entity)

    def get_all_orders(self):
        orders = self.get_entity().query.all()
        if orders:
            print(f"Found {len(orders)} orders")
            return orders
        else:
            print("No orders found")
            return None

    def get_orders_by_date(self, start_date=None, end_date=None, all_orders=False):
        # Implementieren Sie Ihre Logik hier, um die Daten zu filtern
        # basierend auf start_date, end_date, oder beiden
        # Beispiel:

        # Format für Datum und Zeit
        date_format = '%Y-%m-%dT%H:%M'

        if start_date and not isinstance(start_date, datetime):
            start_date = datetime.strptime(start_date, date_format)
            start_date = start_date.replace(second=0)

        if end_date and not isinstance(end_date, datetime):
            end_date = datetime.strptime(end_date, date_format)
            end_date = end_date.replace(second=0)

        query = BridgeOrderEntity.query
        if start_date:
            query = query.filter(BridgeOrderEntity.purchase_date >= start_date)
        if end_date:
            query = query.filter(BridgeOrderEntity.purchase_date <= end_date)

        if not all_orders:
            query = query.filter(BridgeOrderEntity.order_state == "open")

        return query.all(), start_date, end_date, all_orders

    def delete_all_orders(self):
        self.get_entity().query.delete()
        self._commit_and_close()

    def delete_order(self, bridge_order_id):
        order = self.get_entity().query.get(bridge_order_id)
        if order:
            try:
                self.db.session.delete(order)
                self._commit_and_close()
                return True
            except Exception as e:
                self.logger.error(f"Could not delete bridge_order_id{bridge_order_id}: e")
                return False
        else:
            return False
