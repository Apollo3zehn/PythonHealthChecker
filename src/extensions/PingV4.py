import os
from typing import Dict

from BaseTypes import Checker, CheckResult

class PingV4Checker(Checker):
    Id: str = "ping-v4"
    Address: str

    def __init__(self, settings: Dict[str, str]):
        self.Address = settings["address"]

    async def DoCheckAsync(self) -> CheckResult:
        success = not os.system('ping %s -n 1 > nul 2>&1' % (self.Address,))
        name = f"Ping v4 ({self.Address})"

        if success:
            return CheckResult(name, False, "")
        else:
            return CheckResult(name, True, "Could not reach host.")
