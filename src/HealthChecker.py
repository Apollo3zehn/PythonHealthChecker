import importlib
import inspect
import os
from itertools import groupby
from typing import Dict, List, Tuple

from BaseTypes import Checker, CheckResult, DefaultChecker


class HealthChecker:
    
    ChecksConfig: Dict[str, Dict[str, str]]
    CheckerTypes: List[Checker]

    def __init__(self, configFolderPath: str):
        # load config
        checkFilePath = os.path.join(configFolderPath, "checks.conf")
        self.ChecksConfig = self._readChecksConfig(checkFilePath)

        # load checkers
        plugindir = "src/extensions"
        pluginfiles = os.listdir(plugindir)
        modules = [importlib.import_module("extensions." + pluginfile.split('.')[0]) for pluginfile in pluginfiles]
        potentialCheckerTypes = [potentialCheckerType[1] for module in modules for potentialCheckerType in inspect.getmembers(module) if inspect.isclass(potentialCheckerType[1])]
        self.CheckerTypes = [checkerType for checkerType in potentialCheckerTypes if issubclass(checkerType, Checker) and not inspect.isabstract(checkerType)]

    async def CheckHealthAsync(self, ) -> Dict[str, List[CheckResult]]:
        return {group:await self._doChecksAsync(checks) for (group, checks) in self.ChecksConfig.items()}

    async def _doChecksAsync(self, checks):
        return [await self._getChecker(check).DoCheckAsync() for check in checks]

    def _getChecker(self, check) -> Checker:
        return next((checker(check) for checker in self.CheckerTypes if checker.Id == check["type"]), DefaultChecker(check))

    def _readChecksConfig(self, filePath: str) -> Dict[str, Dict[str, str]]:
        checks: List[Dict[str, str]] = []

        with open(filePath, "r") as file:

            check: Dict[str, str]

            for line in file:

                if line.startswith("["):
                    check = {}
                    groupName = line.lstrip("[").rstrip().rstrip("]")
                    check["group"] = groupName
                    checks.append(check)

                elif not self._isNullOrWhiteSpace(line):
                    (option, value) = self._parseOption(line)
                    check[option] = value

        result = {key:list(group) for key, group in groupby(checks, key = lambda check: check["group"])}

        return result

    def _parseOption(self, rawOption: str) -> Tuple[str, str]:
        parts = rawOption.split("=")
        option = parts[0].lstrip().rstrip()
        value = parts[1].lstrip().rstrip()

        return (option, value)

    def _isNullOrWhiteSpace(self, value: str):
        return not value or value.isspace()
