import os
from . import async_requests as requests
from core.models import Client


class ReceiveData:
    def __init__(self):
        self.url = "http://api.prosto-tools.ml/api/"

    async def get_data(self):
        data = await requests.get(url=self.url + "private/client", headers={"Authorization": os.getenv("MAIN_BOT_TOKEN")})
        return Client(await data.json())
