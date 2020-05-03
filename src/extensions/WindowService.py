from typing import Dict

import psutil

from BaseTypes import Checker, CheckResult


class WindowServiceChecker(Checker):
    Id: str = "windows-service"
    ServiceName: str

    def __init__(self, settings: Dict[str, str]):
        self.ServiceName = settings["name"]

    async def DoCheckAsync(self) -> CheckResult:

        name = f"Window Service ({self.ServiceName})"

        try:
            service = psutil.win_service_get(self.ServiceName)
            service = service.as_dict()

            if service['status'] == 'running':
                return CheckResult(name, False, "")
            else:
                return CheckResult(name, True, "The service is not started.")

        except:
            return CheckResult(name, True, "The service does not exist.")
