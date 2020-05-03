from abc import ABC, abstractmethod
from typing import Dict


class CheckResult:
    Name: str
    HasError: bool
    Message: str

    def __init__(self, name: str, hasError: bool, message: str):
        self.Name = name
        self.HasError = hasError
        self.Message = message

class Checker(ABC):
    @abstractmethod
    async def DoCheckAsync(self) -> CheckResult:
        pass

class DefaultChecker(Checker):
    Id: str = "default"
    Type: str

    def __init__(self, settings: Dict[str, str]):
        self.Type = settings["type"]

    async def DoCheckAsync(self) -> CheckResult:
        return CheckResult("", True, f"Could not find checker for type '{self.Type}'.")
