import json

from .configs import Config
from sanic import response, Blueprint


bp = Blueprint('dashboard')


@bp.route("/dashboard/<guild_id:int>", methods=["POST", "GET"])
async def dashboard(request, guild_id):
	# Check if user is logging
	if not request.ctx.session.get("user_state_login"):
		return response.redirect(Config.DISCORD_LOGIN_URI)

	# Get the guilds, roles and channels
	datas_guild = await request.app.discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")
	guild_data = await request.app.database.get_db_guild_data(guild_id)
	new_idea_channel = 0

	if request.method == "POST":
		# Check if prefix is incorect introduced
		if len(request.form["new_prefix"]) < 1:
			return request.app.jinja.render(
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
		elif len(request.form["new_prefix"][0]) > 3:
			return request.app.jinja.render(
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
			new_prefix = request.form["new_prefix"][0]

		stats_dict = {
			'\xa0Все': 'all',
			'\xa0Боты': 'bots',
			'\xa0Участники': 'members',
			'\xa0Каналы': 'channels',
			'\xa0Роли': 'roles',
			"\xa0Сообщения": "message"
		}

		if 'server_stats_remove' in request.form:
			for item in request.form.getlist("server_stats_remove"):
				server_stats = guild_data['server_stats']
				try:
					deleted_channel = server_stats.pop(stats_dict["\xa0"+item])
					await request.app.discord_api.del_channel(deleted_channel)
				except:
					pass
		else:
			server_stats = guild_data['server_stats']

		if 'server_stats' in request.form:
			if stats_dict[request.form['server_stats'][0]] == "message":
				return
			category_id = None
			for channel in datas_guild[0]:
				if channel["name"] == "Статистика" and channel["type"] == 4:
					category_id = channel["id"]
					break

			if category_id is None:
				resp = await request.app.discord_api.create_guild_channel(
					guild_id, name="Статистика", type=4, position=0
				)
				if resp.status == 403:
					return request.app.utils.dashboard_403_response(
						request, "global",
						[[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]], guild_data, datas_guild]
					)
				category_id = (await resp.json())["id"]

			resp = await request.app.discord_api.create_guild_channel(
				guild_id,
				name=request.form['server_stats'][0].replace("\xa0", ""),
				parent_id=category_id,
				type=2,
				permission_overwrites=[{
					"id": guild_id,
					"type": 0,
					"deny": 0x00100000,
					"allow": None
				}]
			)

			if resp.status == 403:
				return request.app.utils.dashboard_403_response(
					request, "global",
					[[guild_id, guilds[str(guild_id)][0], guilds[str(guild_id)][1]], guild_data, datas_guild]
				)

			channel_id = int((await resp.json())["id"])
			server_stats = guild_data['server_stats']
			server_stats.update({stats_dict[request.form['server_stats'][0]]: channel_id})
		else:
			server_stats = guild_data['server_stats']

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
				if "\xa0" + channel["name"] == request.form["react_channel"][0]:
					react_channels = list(guild_data["react_channels"])
					react_channels.append(int(channel["id"]))
		else:
			react_channels = guild_data["react_channels"]

		sql = """UPDATE guilds SET prefix = %s, idea_channel = %s, react_channels = %s, server_stats = %s WHERE guild_id = %s"""
		val = (
			str(new_prefix),
			int(new_idea_channel),
			json.dumps(list(react_channels)),
			json.dumps(server_stats),
			int(guild_id),
		)
		await request.app.database.execute(sql, val)

	guild_data = await request.app.database.get_db_guild_data(guild_id)
	return request.app.jinja.render(
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

	guild_data = await request.app.database.get_db_guild_data(guild_id)
	datas_guild = await request.app.discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return request.app.jinja.render(
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

	guild_data = await request.app.database.get_db_guild_data(guild_id)
	datas_guild = await request.app.discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return request.app.jinja.render(
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

	guild_data = await request.app.database.get_db_guild_data(guild_id)
	datas_guild = await request.app.discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return request.app.jinja.render(
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

	guild_data = await request.app.database.get_db_guild_data(guild_id)
	datas_guild = await request.app.discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return request.app.jinja.render(
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

	guild_data = await request.app.database.get_db_guild_data(guild_id)
	datas_guild = await request.app.discord_api.get_guild_channel_roles(guild_id)
	guilds = request.ctx.session.get("user_guilds")

	return request.app.jinja.render(
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
