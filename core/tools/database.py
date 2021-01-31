import typing
import json
import aiomysql
from core.configs.config import Config


class Database:
    async def prepare(self):
        self.pool = await aiomysql.create_pool(
            host=Config.DB_HOST,
            port=3306,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            db=Config.DB_DATABASE
        )

    async def get_db_guild_data(self, guild_id: int) -> dict:
        """Return a guild settings from database
        Requires a guild id

        """

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """SELECT * FROM guilds WHERE guild_id = %s AND guild_id = %s""",
                    (guild_id, guild_id),
                )
                guild_data = await cur.fetchone()

        # Create a dict with settings guild from database
        dict_guild_data = {
            "guild_id": int(guild_data[0]),
            "all_message": int(guild_data[2]),
            "textchannels_category": int(guild_data[3]),
            "max_warns": int(guild_data[4]),
            "exp_multi": float(guild_data[5]),
            "idea_channel": str(guild_data[6]),
            "timedelete_textchannel": int(guild_data[7]),
            "donate": guild_data[8] == "True",
            "prefix": str(guild_data[9]),
            "api_key": str(guild_data[10]),
            "server_stats": json.loads(guild_data[11]),
            "voice_channel": json.loads(guild_data[12]),
            "shop_list": json.loads(guild_data[13]),
            "ignored_channels": json.loads(guild_data[14]),
            "auto_mod": json.loads(guild_data[15]),
            "clans": json.loads(guild_data[16]),
            "moder_roles": json.loads(guild_data[17]),
            "auto_reactions": json.loads(guild_data[18]),
            "welcome": json.loads(guild_data[19]),
            "auto_roles": json.loads(guild_data[20]),
            "custom_commands": json.loads(guild_data[21]),
            "auto_responders": json.loads(guild_data[22]),
            "audit": json.loads(guild_data[23]),
            "rank_message": json.loads(guild_data[24]),
            'dict_server_stats': {
                'all': 'Все',
                'bots': 'Боты',
                'roles': 'Роли',
                'channels': 'Каналы',
                'members': 'Участники',
                "message": "Сообщения"
            }
        }

        return dict_guild_data

    async def execute(
            self, query: str, val: typing.Union[tuple, list] = (), fetchone: bool = False
    ) -> list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, val)
                await conn.commit()
                if fetchone:
                    data = await cur.fetchone()
                else:
                    data = await cur.fetchall()
        return data

