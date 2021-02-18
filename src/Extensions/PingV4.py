import os
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
        success = not os.system('ping %s -n 1 > nul 2>&1' % (self.Address,))

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
