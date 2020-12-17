import os
import json
import aiomysql


class Database:
    async def get_db_guild_data(self, guild_id: int) -> dict:
        """Return a guild settings from database
        Requires a guild id

        """

        conn = await aiomysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password=os.getenv("DB_PASSWORD"),
            db='data'
        )

        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT * FROM guilds WHERE guild_id = %s AND guild_id = %s""",
                (guild_id, guild_id),
            )
            guild_data = await cur.fetchone()
        conn.close()

        donate = guild_data[8]
        react_channels = []

        # Re-work string "bool" format in bool
        if donate == "True":
            donate = True
        elif donate == "False":
            donate = False

        # Int channels ids re-work in string format
        for channel in json.loads(guild_data[17]):
            react_channels.append(str(channel))

        # Create a dict with settings guild from database
        dict_guild_data = {
            "guild_id": int(guild_data[0]),
            "purge": int(guild_data[1]),
            "all_message": int(guild_data[2]),
            "textchannels_category": int(guild_data[3]),
            "max_warns": int(guild_data[4]),
            "exp_multi": float(guild_data[5]),
            "idea_channel": str(guild_data[6]),
            "timedelete_textchannel": int(guild_data[7]),
            "donate": donate,
            "prefix": str(guild_data[9]),
            "server_stats": json.loads(guild_data[10]),
            "voice_channel": json.loads(guild_data[11]),
            "shop_list": json.loads(guild_data[12]),
            "ignored_channels": json.loads(guild_data[13]),
            "auto_mod": json.loads(guild_data[14]),
            "clans": json.loads(guild_data[15]),
            "moder_roles": json.loads(guild_data[16]),
            "react_channels": set(react_channels),
            "welcome": json.loads(guild_data[18]),
        }

        return dict_guild_data
