import asyncio
import inspect
import json
import os
from datetime import datetime
from typing import Dict, List

import aiohttp

from .BaseTypes import Checker, CheckResult, Config, DefaultChecker, Notifier
from .Extensions.ExternalCache import ExternalCacheChecker


class HealthChecker:
    
    Config: Config
    CheckerTypes: List[Checker]
    Cache: Dict[str, CheckResult]

    def __init__(self, config: Config, extensions: List, cache: Dict[str, CheckResult]):
        self.Config = config
        self.CheckerTypes = [checkerType for checkerType in extensions if issubclass(checkerType, Checker) and not inspect.isabstract(checkerType)]
        self.Cache = cache

    async def CheckHealthAsync(self) -> Dict[str, List[CheckResult]]:
        checkResult = {group:await self._doChecksAsync(checks) for (group, checks) in self.Config.Checkers.items()}
        return checkResult

    async def _doChecksAsync(self, checks: list) -> List[CheckResult]:
        # instantiate
        checkers = [self._getChecker(check) for check in checks]

        # clean up cache
        keysToDelete = []

        for key, value in self.Cache.items():
            if (value.AgeMinutes > 1440):
                keysToDelete.append(key)

        for key in keysToDelete:
            self.Cache.pop(key)

        # special handling for ExternalCacheChecker
        for checker in checkers:
            if type(checker).__name__ == "ExternalCacheChecker": # not working: type(checker) is ExternalCacheChecker
                checker.SetCheckResult(self.Cache.get(checker.Identifier, None))

        # go
        results = await asyncio.gather(*[checker.GetCheckResultAsync() for checker in checkers])

        for i, checker in enumerate(checkers):

            # put results into cache (where associated checker has an identifier)
            if "identifier" in checker.Settings:
                self.Cache[checker.Settings["identifier"]] = results[i]

            # share result?
            if "share-method" in checker.Settings:
                await self._shareResultAsync(checker.Settings, results[i])

        # return
        return results

    async def _shareResultAsync(self, settings: Dict[str, str], result: CheckResult):
        shareMethod = settings["share-method"]

        if (shareMethod == "http-post" and "share-target" in settings and "share-id" in settings):

            async with aiohttp.ClientSession(raise_for_status=False) as session:

                url = settings["share-target"]
                identifier = settings["share-id"]

                params = {
                    "identifier": identifier,
                    "name": result.Name,
                    "resultType": result.ResultType.value,
                    "message": result.Message,
                }

                data = json.dumps(params)
                response = await session.post(url, data=data)
                response.close()

    def _getChecker(self, check) -> Checker:
        return next((checker(check) for checker in self.CheckerTypes if checker.Type == check["type"]), DefaultChecker(check))
