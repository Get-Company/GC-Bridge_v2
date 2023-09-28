from src import create_app
from pprint import pprint
from datetime import datetime, timedelta

from config import SW6Config

app, db = create_app()
# from lib_shopware6_api_base import Shopware6AdminAPIClientBase, Criteria, EqualsFilter
# sw6_client = Shopware6AdminAPIClientBase(SW6Config)
# id = 'e2f18bf14dd54320952d73a0af868dde'
# category = sw6_client.request_get(f"/category/{id}")
# pprint(category)
# payload = Criteria()
# payload.filter.append(EqualsFilter('name', "Plantafeln"))
# category = sw6_client.request_post("/category", payload=payload)
# pprint(category)


""" Timer End """
# after = datetime.now()
# time = after - before
# print(f"The script took {time}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=True)

