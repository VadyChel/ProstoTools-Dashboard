
# Imports
from .configs.config import Config
from .dashboard import bp as dashboard
from .exceptions import bp as exceptions
from .views import bp as views
from sanic import Sanic
from sanic_session import Session

# Initialize objects
app = Sanic(__name__)
app.update_config(Config)
app.static('/static', './static')
app.blueprint(dashboard)
app.blueprint(exceptions)
app.blueprint(views)

Session(app)

# Run the app
def create_app():
	app.run(port=5000, debug=True)