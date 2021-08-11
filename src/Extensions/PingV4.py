import os
import platform
from typing import Dict

from ..BaseTypes import Checker, CheckResult


class PingV4Checker(Checker):
    Type: str = "ping-v4"
    Address: str
    Name: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Address = settings["address"]

        if ("name" in settings):
            self.Name = settings["name"]
        else:
            self.Name = None

    def GetName(self) -> str:
        return f"Ping v4 ({self.Address})"

    async def DoCheckAsync(self) -> CheckResult:

        system = platform.system()

        if system == "Linux":
            success = not os.system(f"ping {self.Address} -c 1 >/dev/null 2>&1")

        elif system == "Windows":
            success = not os.system(f"ping {self.Address} -n 1 > nul 2>&1")

        else:
            raise Exception(f"The platform '{system}' is not supported.")

        if success:
            
            if (self.Name is None):
                return self.Success()
            else:
                return self.Success(self.Name)

        else:

            if (self.Name is None):
                return self.Error(f"Could not reach host.")
            else:
                return self.Error(f"Could not reach host ({self.Name}).")
