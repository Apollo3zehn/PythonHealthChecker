from abc import ABC, abstractmethod
from typing import Dict, List


class Config:
    Notifiers: List[Dict[str, str]]
    Checkers: Dict[str, List[Dict[str, str]]]

    def __init__(self, notifiers: List[Dict[str, str]], checkers: Dict[str, List[Dict[str, str]]]):
        self.Notifiers = notifiers
        self.Checkers = checkers

class CheckResult:
    Name: str
    HasError: bool
    Message: str
    Notifiers: List[str]

    def __init__(self, name: str, hasError: bool, message: str, notifiers: List[str]):
        self.Name = name
        self.HasError = hasError
        self.Message = message
        self.Notifiers = notifiers

class Checker(ABC):

    Notifiers: List[str]

    def __init__(self, settings: Dict[str, str]):
        if "notifiers" in settings:
            self.Notifiers = [notifier.strip() for notifier in settings["notifiers"].split(",")]
        else:
            self.Notifiers = []

    def Success(self, name: str, message: str = "") -> CheckResult:
        return CheckResult(name, False, message, self.Notifiers)

    def Error(self, name: str, message: str) -> CheckResult:
        return CheckResult(name, True, message, self.Notifiers)

    @abstractmethod
    async def DoCheckAsync(self) -> CheckResult:
        pass

class DefaultChecker(Checker):
    Id: str = "default"
    Type: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Type = settings["type"]

    async def DoCheckAsync(self) -> CheckResult:
        return self.Error("Unknown", f"Could not find checker '{self.Type}'.")

class Notifier(ABC):

    Id: str

    def __init__(self, settings: Dict[str, str]):
        self.Id = settings["id"]

    @abstractmethod
    async def NotifyAsync(self):
        pass
