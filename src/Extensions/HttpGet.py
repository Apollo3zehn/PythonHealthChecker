import os
import re
from typing import Dict

import aiohttp
from aiohttp.client import ClientResponseError

from ..BaseTypes import CacheEntry, Checker, CheckResult


class HttpGetChecker(Checker):
    Type: str = "http-get"
    Url: str
    Regex: str

    Cache: Dict[str, CacheEntry]

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Url = settings["url"]
        self.Regex = settings["regex"]

    def GetName(self) -> str:
        return self.Url

    async def DoCheckAsync(self) -> CheckResult:
        
        async with aiohttp.ClientSession(raise_for_status=True) as session:

            try:
                async with session.get(self.Url) as response:
                    content = await response.text()
                    match = re.search(self.Regex, content)

                    if (match is None):
                        return self.Error("Regular expression did not match.")
                    else:
                        return self.Success()

            except Exception as ex:
                return self.Error("Could not HTTP-GET data.")
