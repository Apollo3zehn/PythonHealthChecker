import asyncio
import inspect
import json
import os
from datetime import datetime
from logging import Logger
from typing import Dict, List

import aiohttp

from .BaseTypes import Checker, CheckResult, Config, DefaultChecker, Notifier
from .Extensions.ExternalCache import ExternalCacheChecker


class HealthChecker:
    
    Config: Config
    CheckerTypes: List[Checker]
    Cache: Dict[str, CheckResult]
    Logger: Logger

    def __init__(self, config: Config, extensions: List, cache: Dict[str, CheckResult], logger: Logger):
        self.Config = config
        self.CheckerTypes = [checkerType for checkerType in extensions if issubclass(checkerType, Checker) and not inspect.isabstract(checkerType)]
        self.Cache = cache
        self.Logger = logger

        for checkerType in self.CheckerTypes:
            logger.info(f"Loaded checker {checkerType.Type}.")

    async def CheckHealthAsync(self) -> Dict[str, List[CheckResult]]:
        checkResult = {group:await self._doChecksAsync(checks) for (group, checks) in self.Config.Checkers.items()}
        return checkResult

    async def _doChecksAsync(self, checks: list) -> List[CheckResult]:
        self.Logger.info(f"Instantiate checkers.")
        checkers = [self._getChecker(check) for check in checks]

        self.Logger.info(f"Clean up cache.")
        keysToDelete = []

        for key, value in self.Cache.items():
            if (value.AgeMinutes > 1440):
                keysToDelete.append(key)

        for key in keysToDelete:
            self.Logger.info(f"Delete cache entry {key}.")
            self.Cache.pop(key)

        # special handling for ExternalCacheChecker
        for checker in checkers:
            if type(checker).__name__ == "ExternalCacheChecker": # not working: type(checker) is ExternalCacheChecker
                checkResult = self.Cache.get(checker.Identifier, None)

                if checkResult is not None:
                    group = checker.Settings["group"]
                    checkerType = checker.Settings["type"]
                    self.Logger.info(f"Provide cached check result {checker.Identifier} to checker {checkerType} in group {group}.")

                checker.SetCheckResult(self.Cache.get(checker.Identifier, None))

        self.Logger.info(f"Execute checks.")
        results = await asyncio.gather(*[checker.GetCheckResultAsync() for checker in checkers])

        for i, checker in enumerate(checkers):

            group = checker.Settings["group"]
            checkerType = checker.Settings["type"]
            self.Logger.info(f"Post process checker {checkerType} in group {group}.")

            # put results into cache (where associated checker has an identifier)
            if "identifier" in checker.Settings:
                identifier = checker.Settings["identifier"]
                self.Logger.info(f"Fill cache with check result {identifier}.")
                self.Cache[identifier] = results[i]

            # share result?
            if "share-method" in checker.Settings:
                self.Logger.info(f"Share check result.")
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
