import os
from typing import Dict

from ..BaseTypes import CacheEntry, Checker, CheckResult


class ExternalCacheChecker(Checker):
    Type: str = "external-cache"
    Identifier: str
    MaxAgeMinutes: int

    CacheEntry: CacheEntry

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Identifier = settings["identifier"]
        self.MaxAgeMinutes = int(settings["max-age-minutes"])

    def SetCacheEntry(self, cacheEntry: CacheEntry):
        self.CacheEntry = cacheEntry

    def GetName(self) -> str:
        return self.Identifier

    async def DoCheckAsync(self) -> CheckResult:
        
        if self.CacheEntry is not None:

            if self.CacheEntry.AgeMinutes <= self.MaxAgeMinutes:
                cacheEntry.CheckResult.Notifiers = self.Notifiers
                return self.CacheEntry.CheckResult
                
            return self.Warning("Last check result too old.")

        return self.Warning("No check result found in cache.")
