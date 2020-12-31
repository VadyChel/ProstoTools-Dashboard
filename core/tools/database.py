import typing
import json
import aiomysql
from core.configs.config import Config


class Database:
    @staticmethod
    def str_to_bool(string):
        return string == "True"

    @classmethod
    async def prepare(cls):
        cls.pool = await aiomysql.create_pool(
            host=Config.DB_HOST,
            port=3306,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_DATABASE
        )

    @classmethod
    async def get_db_guild_data(cls, guild_id: int) -> dict:
        """Return a guild settings from database
        Requires a guild id

        """

        async with cls.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """SELECT * FROM guilds WHERE guild_id = %s AND guild_id = %s""",
                    (guild_id, guild_id),
                )
                guild_data = await cur.fetchone()

        donate = guild_data[8]
        react_channels = []

        # Re-work string "bool" format in bool
        if donate == "True":
            donate = True
        elif donate == "False":
            donate = False

        # Int channels ids re-work in string format
        for channel in json.loads(guild_data[19]):
            react_channels.append(str(channel))

        # Create a dict with settings guild from database
        dict_guild_data = {
            "guild_id": int(guild_data[0]),
            "purge": int(guild_data[1]),
            "log_channel": int(guild_data[2]),
            "all_message": int(guild_data[3]),
            "textchannels_category": int(guild_data[3]),
            "max_warns": int(guild_data[5]),
            "exp_multi": float(guild_data[6]),
            "idea_channel": str(guild_data[7]),
            "timedelete_textchannel": int(guild_data[8]),
            "donate": cls.str_to_bool(guild_data[9]),
            "prefix": str(guild_data[10]),
            "api-key": str(guild_data[11]),
            "server_stats": json.loads(guild_data[12]),
            "voice_channel": json.loads(guild_data[13]),
            "shop_list": json.loads(guild_data[14]),
            "ignored_channels": json.loads(guild_data[15]),
            "auto_mod": json.loads(guild_data[16]),
            "clans": json.loads(guild_data[17]),
            "moder_roles": json.loads(guild_data[18]),
            "react_channels": set(react_channels),
            "welcome": json.loads(guild_data[20]),
            "auto_roles": json.loads(guild_data[21])
        }

        return dict_guild_data

    @classmethod
    async def execute(
            cls, query: str, val: typing.Union[tuple, list] = (), fetchone: bool = False
    ) -> list:
        async with cls.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, val)
                await conn.commit()
                if fetchone:
                    data = await cur.fetchone()
                else:
                    data = await cur.fetchall()
        return data

