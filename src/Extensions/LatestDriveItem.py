import glob
import os
from datetime import datetime
from typing import Dict

from ..BaseTypes import Checker, CheckResult


class LatestDriveItem(Checker):
    Type: str = "latest-drive-item"
    Glob: str
    Recursive: bool
    AgeSecondsWarning: int
    AgeSecondsError: int

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)

        self.Glob = settings["glob"]
        self.Recursive = settings["recursive"].lower() == 'true'
        self.AgeSecondsWarning = int(settings["age-seconds-warning"])
        self.AgeSecondsError = int(settings["age-seconds-error"])

    def GetName(self) -> str:
        return f"Latest drive item ({self.Glob})"

    async def DoCheckAsync(self) -> CheckResult:
        driveItems = glob.glob(self.Glob, recursive=self.Recursive)
        driveItems.sort()

        if any(driveItems):
            lastModified = datetime.fromtimestamp(os.path.getmtime(driveItems[-1]))
            age = (datetime.now() - lastModified).total_seconds()

            if age >= self.AgeSecondsError:
                return self.Error(f"Age of latest item: {self.FormatAge(age)}.")

            elif age >= self.AgeSecondsWarning:
                return self.Warning(f"Age of latest item: {self.FormatAge(age)}.")

            else:
                return self.Success()

        else:
            return self.Error("No items found.")

    def FormatAge(self, age: float) -> str:
        
        if age > 86400:
            return f"{round(age / 86400, 1)} days"

        elif age > 3600:
            return f"{round(age / 3600, 1)} hours"

        elif age > 60:
            return f"{round(age / 60, 1)} minutes"

        else:
            return f"{round(age, 1)} seconds"
