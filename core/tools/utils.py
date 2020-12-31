

# Create new class Utils
class Utils:
	async def set_cookie(self, request, cookie_name, value):
		request.cookies[cookie_name] = value
		request.cookies[cookie_name]["secure"] = True

