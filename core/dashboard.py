import json

from .configs import Config
from .tools import Jinja, ReceiveData, DiscordAPI, Database
from sanic import response, Blueprint


bp = Blueprint('dashboard')
jinja = Jinja()
get_api_data = ReceiveData().get_data
discord_api = DiscordAPI()


@bp.route("/dashboard/<guild_id:int>", methods=["POST", "GET"])
async def dashboard(request, guild_id):

	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	# Get the guilds, roles and channels
	datas_guild = await discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")
	guild_data = await Database.get_db_guild_data(guild_id)
	new_idea_channel = 0

	if request.method == "POST":

		# Check if prefix is incorect introduced
		if len(request.form["new_prefix"]) < 1:
			return jinja.render(
				"dashboard.html",
				request,
				url=Config.DISCORD_LOGIN_URI,
				avatar=request.ctx.session.get("user_avatar"),
				login=request.ctx.session.get("user_state_login"),
				user_name=request.ctx.session.get("user_name"),
				guild_data=[
					[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
					guild_data,
					datas_guild,
				],
				category="global",
				alert=["danger", "Укажите префикс"],
			)
		elif len(request.form["new_prefix"]) > 3:
			return jinja.render(
				"dashboard.html",
				request,
				url=Config.DISCORD_LOGIN_URI,
				avatar=request.ctx.session.get("user_avatar"),
				login=request.ctx.session.get("user_state_login"),
				user_name=request.ctx.session.get("user_name"),
				guild_data=[
					[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
					guild_data,
					datas_guild,
				],
				category="global",
				alert=["danger", "Префикс должен быть меньше 4 символов"],
			)
		else:
			new_prefix = request.form["new_prefix"]

		# Purge commands setting
		if request.form["clear_commands"] == "\xa0Выключена":
			new_purge = 0
		elif request.form["clear_commands"] == "\xa0Включена":
			new_purge = 1
		else:
			return response.json(request.form["clear_commands"])

		# Idea channel setting
		if "idea_channel" in request.form:
			for channel in datas_guild[0]:
				if "\xa0" + channel["name"] == request.form["idea_channel"]:
					new_idea_channel = int(channel["id"])
		else:
			new_idea_channel = guild_data["idea_channel"]

		# Check if user delete react channel
		if "react_channels_remove" in request.form:
			for item in request.form.getlist("react_channels_remove"):
				react_channels = guild_data["react_channels"]
				for channel in datas_guild[0]:
					if channel["name"] == item:
						try:
							react_channels.remove(channel["id"])
						except:
							pass
		else:
			react_channels = guild_data["react_channels"]

		# Check if user add react channel
		if "react_channel" in request.form:
			for channel in datas_guild[0]:
				if "\xa0" + channel["name"] == request.form["react_channel"]:
					react_channels = list(guild_data["react_channels"])
					react_channels.append(int(channel["id"]))
		else:
			react_channels = guild_data["react_channels"]

		sql = """UPDATE guilds SET prefix = %s, `purge` = %s, idea_channel = %s, react_channels = %s WHERE guild_id = %s"""
		val = (
			str(new_prefix),
			int(new_purge),
			int(new_idea_channel),
			json.dumps(list(react_channels)),
			int(guild_id),
		)

		cursor.execute(sql, val)  # Database query
		conn.commit()

	guild_data = await Database.get_db_guild_data(guild_id)
	return jinja.render(
		"dashboard.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.ctx.session.get("user_avatar"),
		login=request.ctx.session.get("user_state_login"),
		user_name=request.ctx.session.get("user_name"),
		guild_data=[
			[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
			guild_data,
			datas_guild,
		],
		category="global",
	)


@bp.route("/dashboard/<guild_id:int>/moderation", methods=["POST", "GET"])
async def dashboard_moderation(request, guild_id):

	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	guild_data = await Database.get_db_guild_data(guild_id)
	datas_guild = await discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return jinja.render(
		"dashboard.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.ctx.session.get("user_avatar"),
		login=request.ctx.session.get("user_state_login"),
		user_name=request.ctx.session.get("user_name"),
		guild_data=[
			[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
			guild_data,
			datas_guild,
		],
		category="moderation",
	)


@bp.route("/dashboard/<guild_id:int>/economy", methods=["POST", "GET"])
async def dashboard_economy(request, guild_id):

	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	guild_data = await Database.get_db_guild_data(guild_id)
	datas_guild = await discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return jinja.render(
		"dashboard.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.ctx.session.get("user_avatar"),
		login=request.ctx.session.get("user_state_login"),
		user_name=request.ctx.session.get("user_name"),
		guild_data=[
			[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
			guild_data,
			datas_guild,
		],
		category="economy",
	)


@bp.route("/dashboard/<guild_id:int>/levels", methods=["POST", "GET"])
async def dashboard_levels(request, guild_id):

	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	guild_data = await Database.get_db_guild_data(guild_id)
	datas_guild = await discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return jinja.render(
		"dashboard.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.ctx.session.get("user_avatar"),
		login=request.ctx.session.get("user_state_login"),
		user_name=request.ctx.session.get("user_name"),
		guild_data=[
			[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
			guild_data,
			datas_guild,
		],
		category="levels",
	)


@bp.route("/dashboard/<guild_id:int>/welcome", methods=["POST", "GET"])
async def dashboard_welcome(request, guild_id):

	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	guild_data = await Database.get_db_guild_data(guild_id)
	datas_guild = await discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return jinja.render(
		"dashboard.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.ctx.session.get("user_avatar"),
		login=request.ctx.session.get("user_state_login"),
		user_name=request.ctx.session.get("user_name"),
		guild_data=[
			[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
			guild_data,
			datas_guild,
		],
		category="welcome",
	)


@bp.route("/dashboard/<guild_id:int>/utils", methods=["POST", "GET"])
async def dashboard_utils(request, guild_id):

	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	guild_data = await Database.get_db_guild_data(guild_id)
	datas_guild = await discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return jinja.render(
		"dashboard.html",
		request,
		url=Config.DISCORD_LOGIN_URI,
		avatar=request.ctx.session.get("user_avatar"),
		login=request.ctx.session.get("user_state_login"),
		user_name=request.ctx.session.get("user_name"),
		guild_data=[
			[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]],
			guild_data,
			datas_guild,
		],
		category="utils",
	)
