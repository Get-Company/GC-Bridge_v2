from src import create_app
from pprint import pprint
from datetime import datetime, timedelta

from src.modules.ERP.controller.ERPAdressenController import ERPAdressenController

before = datetime.now()

buchner_ctrl = ERPAdressenController(10026)


# print(hans_ctrl.shipping_address().get_("Na2"))

after = datetime.now()
time = after - before
print(f"The script took {time}")
# app = create_app()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=True)

