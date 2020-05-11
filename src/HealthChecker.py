import inspect
import os
from typing import Dict, List

from .BaseTypes import Checker, CheckResult, Config, DefaultChecker, Notifier


class HealthChecker:
    
    Config: Config
    CheckerTypes: List[Checker]

    def __init__(self, config: Config, extensions: List):
        self.Config = config
        self.CheckerTypes = [checkerType for checkerType in extensions if issubclass(checkerType, Checker) and not inspect.isabstract(checkerType)]

    async def CheckHealthAsync(self) -> Dict[str, List[CheckResult]]:
        checkResult = {group:await self._doChecksAsync(checks) for (group, checks) in self.Config.Checkers.items()}
        return checkResult

    async def _doChecksAsync(self, checks) -> List[CheckResult]:
        checkers = [self._getChecker(check) for check in checks]
        return [await checker.GetCheckResultAsync() for checker in checkers]

    def _getChecker(self, check) -> Checker:
        return next((checker(check) for checker in self.CheckerTypes if checker.Type == check["type"]), DefaultChecker(check))
