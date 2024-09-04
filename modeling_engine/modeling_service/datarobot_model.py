import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

import aiofiles
import datarobot as dr
from aiohttp import ClientResponse, ClientSession


class AsyncModel(dr.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @asynccontextmanager
    async def _make_request(self, method: str, url: str, **kwargs) -> ClientResponse:
        async with ClientSession() as session:
            async with session.request(method=method, url=url, **kwargs) as resp:
                yield resp

    async def download_model_package_file(self, filepath: Path):
        url = f"{self._client.endpoint}/projects/{self.project_id}/models/{self.id}/modelPackageFile/prepare/"
        async with self._make_request(
            "POST", url, headers=self._client.headers
        ) as post_resp:
            location = post_resp.headers.get("Location", {})
        while True:
            async with self._make_request(
                "GET", location, headers=self._client.headers
            ) as get_resp:
                if get_resp.status != 200:
                    raise Exception(
                        f"Failed to download model package file: {get_resp.content}"
                    )
                if get_resp.headers["Content-Type"] == "application/octet-stream":
                    async with aiofiles.open(filepath, "wb") as file:
                        await file.write(await get_resp.read())
                    break
                await asyncio.sleep(1)

    async def to_dict(self):
        async with self._make_request(
            method="get",
            url=f"{self._client.endpoint}/projects/{self.project_id}/models/{self.id}/",
            headers=self._client.headers,
        ) as resp:
            return await resp.json()
