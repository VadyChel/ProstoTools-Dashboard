import os
from core.tools.http import async_requests as requests


class Command:
    def __init__(self, data):
        self.name = data["name"]
        self.usage = data["usage"]
        self.description = data["description"]


class Client:
    def __init__(self, data):
        self.users = data["users"]
        self.guilds = data["guilds"]
        self.channels = data["channels"]
        self.cogs = [cog for cog in data["commands"].keys()]
        self.commands = [command for cog in data["commands"] for command in cog.keys()]


class ReceiveData:
    def __init__(self):
        self.url = "https://prosto-tools-api.herokuapp.com/"

    async def get_data(self):
        data = await requests.get(url=self.url + "private/client", headers={"token": os.getenv("BOT_TOKEN")})
        return Client(await data.json())
