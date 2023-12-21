from datetime import datetime

from src import create_app
from pprint import pprint

""" Timer Start """
before = datetime.now()
""" Timer Start """

app, db = create_app()

""" Timer End """
after = datetime.now()
time = after - before
print(f"The script took {time}")
""" Timer End """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=True)

