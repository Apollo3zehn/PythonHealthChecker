import os
from typing import Dict

from ..BaseTypes import Checker, CheckResult


class ExternalCacheChecker(Checker):
    Type: str = "external-cache"
    Identifier: str
    MaxAgeMinutes: int

    CheckResult: CheckResult

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Identifier = settings["identifier"]
        self.MaxAgeMinutes = int(settings["max-age-minutes"])

    def SetCheckResult(self, checkResult: CheckResult):
        self.CheckResult = checkResult

    def GetName(self) -> str:
        return self.Identifier

    async def DoCheckAsync(self) -> CheckResult:
        
        if self.CheckResult is not None:

            if self.CheckResult.AgeMinutes <= self.MaxAgeMinutes:
                self.CheckResult.Notifiers = self.Notifiers

                if self.CheckResult.InfoUrl is None:
                    self.CheckResult.InfoUrl = self.InfoUrl

                return self.CheckResult
                
            else:
                return self.Warning("Last check result too old.")

        return self.Warning("No check result found in cache.")
