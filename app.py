
# Imports
import mysql.connector
import asyncio_redis

from sanic import Sanic
from sanic_session import Session
from sanic_jinja2 import SanicJinja2

# Initialize objects
app = Sanic(__name__)
# app.update_config('ProstoToolsDashboard.config.Config')
app.static('/static', './static/css')
jinja = SanicJinja2(app)
session = Session()

# Run the app
if __name__ == "__main__":
	app.run(port=5000, debug=True)