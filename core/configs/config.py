import os


class Config:
	# Sanic config
	DEBUG = True

	# Jinja config
	TEMPLATES_PACKAGE = "core"
	TEMPLATES_FOLDER = "templates"

	# Db config
	DB_PASSWORD = os.getenv('DB_PASSWORD')
	DB_HOST = os.getenv('DB_HOST')
	DB_USER = os.getenv('DB_USER')
	DB_DATABASE = os.getenv('DB_DATABASE')

	# Client config
	CLIENT_ID = "700767394154414142"
	CLIENT_SECRET = "DsxERoWInGaqcX1CoJQu3QfNX7pak-Yd"
	SCOPE = "identify%20guilds"
	REDIRECT_URI = "http://127.0.0.1:5000/servers"
	DISCORD_LOGIN_URI = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
	DISCORD_TOKEN_URI = "https://discord.com/api/v8/oauth2/token"
	DISCORD_API_URI = "https://discord.com/api/v8"
	CLIENT_TOKEN = os.getenv("BOT_TOKEN")
