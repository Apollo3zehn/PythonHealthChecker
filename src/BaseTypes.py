from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from enum import Enum
from typing import Dict, List


class Config:
    Notifiers: List[Dict[str, str]]
    Checkers: Dict[str, List[Dict[str, str]]]

    def __init__(self, notifiers: List[Dict[str, str]], checkers: Dict[str, List[Dict[str, str]]]):
        self.Notifiers = notifiers
        self.Checkers = checkers

class CheckResultType(Enum):
    Success = 1
    Warning = 2
    Error = 3

class CheckResult:
    Name: str
    ResultType: CheckResultType
    Message: str
    InfoUrl: str
    Notifiers: List[str]
    Created: datetime

    def __init__(self, name: str, resultType: CheckResultType, message: str, infoUrl: str, notifiers: List[str]):
        self.Name = name
        self.ResultType = resultType
        self.Message = message
        self.InfoUrl = infoUrl
        self.Notifiers = notifiers
        self.Created = datetime.utcnow().replace(tzinfo=timezone.utc)

    @property
    def AgeMinutes(self):
        return (datetime.utcnow().replace(tzinfo=timezone.utc) - self.Created).total_seconds()/60

    @property
    def HasError(self):
        return self.ResultType == CheckResultType.Error

class Checker(ABC):

    InfoUrl: str
    Notifiers: List[str]
    Settings: Dict[str, str]

    def __init__(self, settings: Dict[str, str]):

        self.Settings = settings

        # url
        if "info-url" in settings:
            self.InfoUrl = settings["info-url"]
        else:
            self.InfoUrl = None

        # notifiers
        if "notifiers" in settings:
            self.Notifiers = [notifier.strip() for notifier in settings["notifiers"].split(",")]
        else:
            self.Notifiers = []


    def Success(self, message: str = "") -> CheckResult:
        return CheckResult(self.GetName(), CheckResultType.Success, message, self.InfoUrl, self.Notifiers)

    def Warning(self, message: str) -> CheckResult:
        return CheckResult(self.GetName(), CheckResultType.Warning, message, self.InfoUrl, self.Notifiers)

    def Error(self, message: str) -> CheckResult:
        return CheckResult(self.GetName(), CheckResultType.Error, message, self.InfoUrl, self.Notifiers)
    
    async def GetCheckResultAsync(self) -> CheckResult:
        try:
            return await self.DoCheckAsync()
        except Exception as ex:

            try:
                return self.Error(str(ex))

            except Exception as ex2:
                return CheckResult("Failed check", CheckResultType.Error, str(ex2), self.InfoUrl, self.Notifiers)

    @abstractmethod
    def GetName(self) -> str:
        pass

    @abstractmethod
    async def DoCheckAsync(self) -> CheckResult:
        pass

class DefaultChecker(Checker):
    Id: str = "default"
    Type: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Type = settings["type"]

    def GetName(self) -> str:
        return "Unknown"

    async def DoCheckAsync(self) -> CheckResult:
        return self.Error(f"Could not find checker '{self.Type}'.")

class Notifier(ABC):

    Id: str

    def __init__(self, settings: Dict[str, str]):
        self.Id = settings["id"]

    @abstractmethod
    async def NotifyAsync(self):
        pass

class NotificationState():
    RunId: str
    Date: date

    def __init__(self, runId: str, date: date):
        self.RunId = runId
        self.Date = date