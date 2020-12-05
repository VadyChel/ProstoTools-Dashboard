import os

class Config:
	# Sanic config
	DEBUG = True

	# Jinja config
	TEMPLATES_PACKAGE = "core"
	TEMPLATES_FOLDER = "templates"

	# Db config
	DB_PASSWORD = os.environ.get('DB_PASSWORD') or '9fr8-PkM;M4+'
	HOST = os.environ.get('DB_HOST') or 'localhost'
	USER = os.environ.get('DB_USER') or 'root'
	DATABASE = os.environ.get('DB_DATABASE') or 'data'