from .configs import Config
from sanic.exceptions import NotFound, ServerError
from sanic import Blueprint

bp = Blueprint('exceptions')


@bp.exception(NotFound)
async def not_found_error(request, exception):
	"""Catch the 404 code error
	And return html page

	"""

	try:
		return request.app.jinja.render(
			"error_404.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.ctx.session.get("user_avatar"),
			login=request.ctx.session.get("user_state_login"),
			user_name=request.ctx.session.get("user_name"),
		)
	except:
		return request.app.jinja.render(
			"error_404.html", request, url=Config.DISCORD_LOGIN_URI
		)


@bp.exception(ServerError)
async def internal_error(request, exception):
	"""Catch the 500 code error
	And return html page

	"""

	try:
		return request.app.jinja.render(
			"error_500.html",
			request,
			url=Config.DISCORD_LOGIN_URI,
			avatar=request.ctx.session.get("user_avatar"),
			login=request.ctx.session.get("user_state_login"),
			user_name=request.ctx.session.get("user_name"),
			error=exception,
		)
	except:
		return request.app.jinja.render(
			"error_500.html", request, url=Config.DISCORD_LOGIN_URI, error=exception
		)
