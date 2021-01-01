from core.configs.config import Config


# Create new class Utils
class Utils:
	async def dashboard_403_response(self, request, jinja, category: str, guild_data: list):
		return jinja.render(
			"dashboard.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.ctx.session.get("user_avatar"),
			login=request.ctx.session.get("user_state_login"),
			user_name=request.ctx.session.get("user_name"),
			guild_data=guild_data,
			category=category,
			alert=["danger", "У меня не хватает прав на создания канала"],
		)
