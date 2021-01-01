from . import async_requests as requests
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
            url=self.DISCORD_TOKEN_URI, data=payload, headers=headers
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

    async def get_guild(self, guild_id: int):
        """Return a guild data
        Requires guild id

        """

        headers = {"Authorization": f"Bot {self.CLIENT_TOKEN}"}

        guild_obj = await requests.get(
            url=self.DISCORD_API_URI + f"/guilds/{guild_id}", headers=headers
        )  # Get a data from discord API
        guild = await guild_obj.json()
        return guild

    async def get_user(self, user_id: int):
        """Return a user data
        Requires user id

        """

        headers = {"Authorization": f"Bot {self.CLIENT_TOKEN}"}

        user_obj = await requests.get(
            url=self.DISCORD_API_URI + f"/user/{user_id}", headers=headers
        )  # Get a data from discord API
        user = await user_obj.json()
        if user_obj.status == 404:
            return None
        return user

    async def create_guild_channel(self, guild_id: int, **kwargs):
        """Create a guild channel
        Requires guild id and channel name

        """
        headers = {
            "Authorization": f"Bot {self.CLIENT_TOKEN}",
            "Content-Type": "application/json"
        }

        response = await requests.post(
            url=self.DISCORD_API_URI+f"/guilds/{guild_id}/channels", json=kwargs, headers=headers
        )
        return response

    async def get_channel(self, channel_id: int):
        """Return a guild channel
        Requires channel id

        """
        headers = {"Authorization": f"Bot {self.CLIENT_TOKEN}"}

        channel_obj = await requests.get(
            url=self.DISCORD_API_URI+f"/channels/{channel_id}", headers=headers
        )
        channel = await channel_obj.json()
        return channel

    async def del_channel(self, channel_id: int):
        """Delete a guild channel
        Requires channel id

        """
        headers = {
            "Authorization": f"Bot {self.CLIENT_TOKEN}",
            "Content-Type": "application/json"
        }

        response = await requests.delete(
            url=self.DISCORD_API_URI+f"/channels/{channel_id}", headers=headers
        )
        return response

    async def send_message(self, channel_id: int, **kwargs):
        """Send message to channel
        Requires guild id and channel name

        """
        headers = {
            "Authorization": f"Bot {self.CLIENT_TOKEN}",
            "Content-Type": "application/json"
        }

        response = await requests.post(
            url=self.DISCORD_API_URI+f"/channels/{channel_id}/messages", json=kwargs, headers=headers
        )
        return response
