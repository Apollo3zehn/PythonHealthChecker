import json
import os
from typing import Dict
from urllib.parse import quote

import aiohttp
from aiohttp.client import ClientResponseError
from src.BaseTypes import CheckResultType

from ..BaseTypes import Checker, CheckResult


class PingV4Checker(Checker):
    Type: str = "query-federated"
    Url: str
    RemoteIdentifier: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Url = settings["url"]
        self.RemoteIdentifier = settings["remote-identifier"]

    def GetName(self) -> str:
        return self.RemoteIdentifier

    async def DoCheckAsync(self) -> CheckResult:
        
        async with aiohttp.ClientSession(raise_for_status=True) as session:

            try:
                url = f"{self.Url}/api/checkresults/{quote(self.RemoteIdentifier, safe='')}"

                async with session.get(url) as response:
                    jsonString = await response.text()
                    checkResultJson = json.loads(jsonString)

                    # create CheckResult
                    identifier = checkResultJson["identifier"]
                    name = checkResultJson["name"]
                    resultType = CheckResultType(int(checkResultJson["resultType"]))
                    message = checkResultJson["message"]
                    notifiers = []

                    checkResult = CheckResult(name, resultType, message, notifiers)

                    return checkResult

            except Exception as ex:
                return self.Error("Could not query federated data.")
