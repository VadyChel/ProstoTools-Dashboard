from core.tools.http import async_requests as requests
from core.configs import Config


class DiscordAPI:
    def __init__(self):
        self.CLIENT_ID = Config.CLIENT_ID
        self.CLIENT_SECRET = Config.CLIENT_SECRET
        self.CLIENT_TOKEN = Config.CLIENT_TOKEN
        self.REDIRECT_URI = Config.REDIRECT_URI
        self.SCOPE = Config.SCOPE
        self.DISCORD_TOKEN_URI = Config.DISCORD_TOKEN_URI
        self.DISCORD_API_URI = Config.DISCORD_API_URI

    async def get_access_token(self, code: str) -> str:
        """Return the access token of user
        Requires code

        """

        payload = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.REDIRECT_URI,
            "scope": self.SCOPE,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        access_token = await requests.post(
            url=self.DISCORD_TOKEN_URI, json=payload, headers=headers
        )  # Get a data from discord API
        json = await access_token.json()

        return json.get("access_token")


    async def get_user_data(self, access_token: str) -> list:
        """Return an user data and user guilds
        Requires user access token

        """

        url = self.DISCORD_API_URI + "/users/@me"

        headers = {"Authorization": f"Bearer {access_token}"}
        user_data = await requests.get(url=url, headers=headers)
        user_json = await user_data.json()
        user_data_guilds = await requests.get(
            url=url + "/guilds", headers=headers
        )  # Get a data from discord API
        user_guilds = await user_data_guilds.json()

        return [user_json, user_guilds]


    async def get_guild_channel_roles(self, guild_id: int) -> list:
        """Return a guild channels and roles
        Requires guild id

        """

        headers = {"Authorization": f"Bot {self.CLIENT_TOKEN}"}

        guild_channels_obj = await requests.get(
            url=self.DISCORD_API_URI + f"/guilds/{guild_id}/channels", headers=headers
        )  # Get a data from discord API
        guild_channels = await guild_channels_obj.json()
        guild_channels = sorted(
            guild_channels, key=lambda channel: channel["position"]
        )  # Sort a guild channels of position

        guild_roles_obj = await requests.get(
            url=self.DISCORD_API_URI + f"/guilds/{guild_id}/roles", headers=headers
        )  # Get a data from discord API
        guild_roles = await guild_roles_obj.json()
        guild_roles = sorted(
            guild_roles, key=lambda role: role["position"]
        )  # Sort a guild roles of position
        guild_roles.reverse()

        return [guild_channels, guild_roles]
