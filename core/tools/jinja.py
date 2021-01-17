import core.app
from core.configs.config import Config
from sanic.response import html
from jinja2 import Environment, PackageLoader


class Jinja:
	def __init__(self):
		self.env = Environment(
			loader=PackageLoader(Config.TEMPLATES_PACKAGE, Config.TEMPLATES_FOLDER,
		))

	def update_request_context(self, request, context):
		context.setdefault("request", request)
		context.update({
			"url_for": core.app.url_for
		})

	def render_string(self, template, request, **context):
		self.update_request_context(request, context)
		return self.env.get_template(template).render(**context)

	def render(self, template, request, **context):
		return html(self.render_string(template, request, **context))
