from core.tools.http.discord_api import DiscordAPI

discord_api = DiscordAPI()


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
        self.commands = data["commands"]

    async def get_guild(self, guild_id: int):
        return Guild(await discord_api.get_guild(guild_id))

    async def get_user(self, user_id: int):
        data = await discord_api.get_user(user_id)
        return User(data) if data is not None else None


class Guild:
    def __init__(self, data):
        self.id = int(data["id"])
        self.name = data["name"]
        self.roles = [Role(role_data) for role_data in data["roles"]]
        self.emojis = [Emoji(emoji_data) for emoji_data in data["emojis"]]
        # self.owner = User(await discord_api.get_user(data["owner_id"]))
        self.region = data["region"]
        self.icon = data["icon"]
        self.icon_url = (f"https://cdn.discordapp.com/icons/{self.id}/{self.icon}.png"
                         if self.icon is not None else "")


class User:
    def __init__(self, data):
        self.name = data["username"]
        self.discriminator = data["discriminator"]
        self.id = int(data["id"])
        self.avatar = data["avatar"]
        if self.avatar.startswith("a_"):
            self.avatar_url = f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.gif"
        else:
            self.avatar_url = f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"

    def __str__(self):
        return self.name+"#"+self.discriminator


class Emoji:
    def __init__(self, data):
        self.name = data["name"]
        self.id = data["id"]
        self.animated = data["animated"]


class Role:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.permissions = data["permissions"]
        self.position = data["position"]
