import json
import os
from datetime import datetime
from typing import Dict
from urllib.parse import quote, urlparse
from urllib.request import urlopen

import aiohttp
import iso8601
from aiohttp.client import ClientResponseError
from src.BaseTypes import CheckResultType

from ..BaseTypes import Checker, CheckResult


class PingV4Checker(Checker):
    Type: str = "query-federated"
    Url: str
    RemoteIdentifier: str
    MaxAgeMinutes: int

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Url = settings["url"]
        self.RemoteIdentifier = settings["remote-identifier"]
        self.MaxAgeMinutes = int(settings["max-age-minutes"])

    def GetName(self) -> str:
        return self.RemoteIdentifier

    async def DoCheckAsync(self) -> CheckResult:
        
        parseResult = urlparse(self.Url)

        if parseResult.scheme == "file":
           
            try:
                with urlopen(self.Url) as file:
                    jsonByteString = file.read()

            except Exception:
                return self.Error("Could not query federated data.")

        elif parseResult.scheme == "http" or parseResult.scheme == "https":

            async with aiohttp.ClientSession(raise_for_status=True) as session:

                try:
                    url = f"{self.Url}/api/checkresults/{quote(self.RemoteIdentifier, safe='')}"

                    async with session.get(url) as response:
                        jsonByteString = await response.read()

                except Exception as ex:
                    return self.Error("Could not query federated data.")

        checkResultJson = json.loads(jsonByteString)

        # create CheckResult
        identifier = checkResultJson["identifier"]

        if (identifier != self.RemoteIdentifier):
            return self.Error("Requested and received identifiers do not match.")

        name = checkResultJson["name"]
        resultType = CheckResultType(int(checkResultJson["resultType"]))
        message = checkResultJson["message"]
        notifiers = []

        checkResult = CheckResult(name, resultType, message, self.Notifiers)
        checkResult.Created = iso8601.parse_date(checkResultJson["created"])

        if checkResult.AgeMinutes <= self.MaxAgeMinutes:
            return checkResult

        else:
            return self.Warning("Last check result too old.")
