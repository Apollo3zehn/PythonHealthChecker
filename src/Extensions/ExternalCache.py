import os
from typing import Dict

from ..BaseTypes import CacheEntry, Checker, CheckResult


class ExternalCacheChecker(Checker):
    Type: str = "external-cache"
    Identifier: str
    MaxAgeMinutes: int

    Cache: Dict[str, CacheEntry]

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Identifier = settings["identifier"]
        self.MaxAgeMinutes = int(settings["max-age-minutes"])

    def SetCache(self, cache: Dict[str, CacheEntry]):
        self.Cache = cache

    def GetName(self) -> str:
        return self.Identifier

    async def DoCheckAsync(self) -> CheckResult:
        
        if self.Cache is not None and self.Identifier in self.Cache:

            cacheEntry = self.Cache[self.Identifier]
            
            if cacheEntry.AgeMinutes <= self.MaxAgeMinutes:
                return cacheEntry.CheckResult
                
            return self.Warning("Last check result too old.")

        return self.Warning("No check result found in cache.")
