# Imports
import json
import mysql.connector

from .configs import Config
from .tools import ReceiveData, Jinja, Utils, Database, DiscordAPI
from sanic import response, Blueprint

conn = mysql.connector.connect(
	user=Config.DB_USER, passwd=Config.DB_PASSWORD, host=Config.DB_HOST, db=Config.DB_DATABASE
)
cursor = conn.cursor(buffered=True)
bp = Blueprint('main_routes')
jinja = Jinja()
get_api_data = ReceiveData().get_data
discord_api = DiscordAPI()
database = Database()
utils = Utils()


@bp.route("/")
async def index(request):
	# client = await get_api_data()
	cursor.execute(
		"""SELECT count FROM bot_stats WHERE entity = 'all commands'"""
	)  # Database query
	amout_used_commands = cursor.fetchall()[::-1][0]

	try:
		return jinja.render(
			"index.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.cookies.get("user_avatar"),
			login=request.cookies.get("user_state_login"),
			user_name=request.cookies.get("user_name"),
			bot_stats=[len(client.guilds), len(client.users), amout_used_commands],
		)
	except:
		return jinja.render(
			"index.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			bot_stats=[0, 0, amout_used_commands],
		)


@bp.route("/servers")
async def servers(request):
	code = request.args.get("code")  # Get code from url
	access_token = await discord_api.get_access_token(code)  # Get an user access token

	if code:  # If code is not None, it redirects to the servers page

		# Work with session
		await utils.set_cookie(request, "access_token", access_token)
		await utils.set_cookie(request, "user_state_login", access_token)
		return response.redirect("/servers")

	access_token = request.cookies.get("access_token")
	user_datas = await discord_api.get_user_data(access_token)

	# If length of username the biggest than 16, it is shorting the username and it is unating a username and disciminator
	if len(user_datas[0]["username"]) > 16:
		user_name = (
			user_datas[0]["username"][:14] + "...#" + user_datas[0]["discriminator"]
		)
	else:
		user_name = user_datas[0]["username"] + "#" + user_datas[0]["discriminator"]

	user_hash_avatar = user_datas[0]["avatar"]
	user_id = user_datas[0]["id"]

	# Check if user has not default avatar
	if user_hash_avatar:

		# Check if useravatar is animated
		if user_hash_avatar.startswith("a_"):
			user_avatar = (
				f"https://cdn.discordapp.com/avatars/{user_id}/{user_hash_avatar}.gif"
			)
		else:
			user_avatar = (
				f"https://cdn.discordapp.com/avatars/{user_id}/{user_hash_avatar}.png"
			)
	else:
		user_avatar = "https://cdn.discordapp.com/attachments/717783820308316272/743448353672790136/1.png"

	# Write the user data to session
	await utils.set_cookie(request, "user_name", user_name)
	await utils.set_cookie(request, "user_avatar", user_avatar)

	datas = []
	session_guild_datas = {}
	guilds = [
		str(guild) for guild in client.guilds
	]  # Get the id client guilds in format string

	try:

		# Check if the user has more permissions on guild and check if bot on this guild
		for guild in user_datas[1]:
			bot = False
			guild_id = guild["id"]
			guild_icon = guild["icon"]
			guild_perms = guild["permissions"]
			guild_perms |= guild["permissions"]
			guild_name = guild["name"]
			if len(guild_name) > 14:
				guild_name = guild_name[:14] + "..."

			# Check the user permissions on guild
			if guild_perms & 0x20 == 0x20:
				manage_server = True
			else:
				manage_server = False

			# Check if bot on the guild
			if str(guild_id) in guilds:
				bot = True

			# Add guild data to variable datas
			if not guild_icon and manage_server:
				datas.append(
					[
						"https://cdn.discordapp.com/attachments/717783820308316272/743448353672790136/1.png",
						bot,
						guild_name,
						guild_id,
					]
				)
				session_guild_datas.update(
					{
						guild["id"]: [
							"https://cdn.discordapp.com/attachments/717783820308316272/743448353672790136/1.png",
							guild["name"],
						]
					}
				)
			elif guild_icon and manage_server:
				session_guild_datas.update(
					{
						guild["id"]: [
							f"https://cdn.discordapp.com/icons/{guild_id}/{guild_icon}.png",
							guild["name"],
						]
					}
				)
				datas.append(
					[
						f"https://cdn.discordapp.com/icons/{guild_id}/{guild_icon}.png",
						bot,
						guild_name,
						guild_id,
					]
				)
	except:
		pass

	if "user_guilds" in request.cookies.keys():
		if request.cookies.get("user_guilds") != session_guild_datas:
			await utils.set_cookie(request, "user_guilds", session_guild_datas)
	else:
		await utils.set_cookie(request, "user_guilds", session_guild_datas)

	return jinja.render(
		"servers.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		datas=datas,
		avatar=request.cookies.get("user_avatar"),
		login=request.cookies.get("user_state_login"),
		user_name=request.cookies.get("user_name"),
	)


@bp.route("/commands")
async def commands(request):
	try:
		return jinja.render(
			"commands.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.cookies.get("user_avatar"),
			login=request.cookies.get("user_state_login"),
			user_name=request.cookies.get("user_name"),
			client=client,
		)
	except:
		return jinja.render(
			"commands.html", request, url=Config.DISCORD_LOGIN_URI, client=client
		)


@bp.route("/profile")
async def profile(request):

	# Check if user is logging
	if not request.cookies.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	access_token = request.cookies.get(
		"access_token"
	)  # Get the user access token form request.ctx.session
	user_datas = await discord_api.get_user_data(access_token)

	sql_1 = """SELECT money FROM users WHERE user_id = %s AND user_id = %s"""
	val_1 = (user_datas[0]["id"], user_datas[0]["id"])

	cursor.execute(sql_1, val_1)  # Database query
	list_money = cursor.fetchall()
	money = 0

	# Get all money from all user guilds
	all_money = [str(i[0]) for i in list_money]
	for num in all_money:
		money += int(num)

	sql_2 = """SELECT bio FROM global_users_data WHERE user_id = %s AND user_id = %s"""
	val_2 = (user_datas[0]["id"], user_datas[0]["id"])

	cursor.execute(sql_2, val_2)  # Database query
	bio = cursor.fetchone()[0]

	return jinja.render(
		"profile.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.cookies.get("user_avatar"),
		login=request.cookies.get("user_state_login"),
		user_name=request.cookies.get("user_name"),
		user_data=[user_datas[0]["id"], len(user_datas[1]), money, bio],
	)


@bp.route("/stats")
async def stats(request):
	channels = len(
		[str(channel.id) for guild in client.guilds for channel in guild.channels]
	)

	try:
		return jinja.render(
			"stats.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.cookies.get("user_avatar"),
			login=request.cookies.get("user_state_login"),
			user_name=request.cookies.get("user_name"),
			bot_stats=[channels, len(client.guilds), len(client.users)],
		)
	except:
		return jinja.render(
			"stats.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			bot_stats=[channels, len(client.guilds), len(client.users)],
		)


@bp.route("/transactions")
async def transactions(request):

	# Check if user is logging
	if not request.cookies.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	access_token = request.cookies.get(
		"access_token"
	)  # Get the user access token form session
	user_datas = await discord_api.get_user_data(access_token)

	sql = """SELECT transantions FROM users WHERE user_id = %s AND user_id = %s"""
	val = (user_datas[0]["id"], user_datas[0]["id"])

	cursor.execute(sql, val)  # Database query
	data = cursor.fetchall()
	transactions = [
		t
		for transactions in data
		for transaction in transactions
		for t in json.loads(transaction)
	]
	for t in transactions:
		if isinstance(t["to"], int):
			t.update({"to": client.get_user(int(t["to"]))})

		if isinstance(t["from"], int):
			t.update({"from": client.get_user(int(t["from"]))})

		guild_icon = client.get_guild(int(t["guild_id"])).icon_url
		if str(guild_icon) == "":
			guild_icon = "https://cdn.discordapp.com/attachments/717783820308316272/743448353672790136/1.png"
		t.update({"guild_icon": guild_icon})

	return jinja.render(
		"transactions.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.cookies.get("user_avatar"),
		login=request.cookies.get("user_state_login"),
		user_name=request.cookies.get("user_name"),
		transactions=transactions,
	)


@bp.route("/leaderboard")
async def leaderboard(request):
	cursor.execute(
		"""SELECT money, reputation, exp, level, coins, user_id FROM users ORDER BY exp DESC LIMIT 100"""
	)  # Database query
	data = cursor.fetchall()
	users = {}

	for user in data:
		if client.get_user(int(user[5])) is not None:
			users.update(
				{
					user[5]: {
						"exp": user[2],
						"reputation": user[1],
						"money": user[0],
						"lvl": user[3],
						"coins": user[4],
						"avatar": client.get_user(int(user[5])).avatar_url,
						"user": client.get_user(int(user[5])).name
						+ client.get_user(int(user[5])).discriminator,
					}
				}
			)

	users_list = sorted(users, key=lambda user: users[user]["exp"], reverse=True)
	try:
		return jinja.render(
			"leaderboard.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.cookies.get("user_avatar"),
			login=request.cookies.get("user_state_login"),
			user_name=request.cookies.get("user_name"),
			users_data=users,
			users_list=users_list,
		)
	except:
		return jinja.render(
			"leaderboard.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			users_data=users,
			users_list=users_list,
		)


@bp.route("/logout")
async def logout(request):
	"""Logout function"""

	# Work with session
	del request.cookies["access_token"]
	del request.cookies["user_state_login"]
	del request.cookies["user_name"]
	del request.cookies["user_avatar"]
	del request.cookies["user_guilds"]

	return response.redirect("/")