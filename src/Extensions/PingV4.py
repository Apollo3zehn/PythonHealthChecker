import os
from typing import Dict

from ..BaseTypes import Checker, CheckResult

class PingV4Checker(Checker):
    Type: str = "ping-v4"
    Address: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.Address = settings["address"]

    def GetName(self) -> str:
        return f"Ping v4 ({self.Address})"

    async def DoCheckAsync(self) -> CheckResult:
        success = not os.system('ping %s -n 1 > nul 2>&1' % (self.Address,))

        if success:
            return self.Success()
        else:
            return self.Error("Could not reach host.")
