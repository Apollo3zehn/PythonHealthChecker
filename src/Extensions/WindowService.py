from typing import Dict

import psutil

from ..BaseTypes import Checker, CheckResult


class WindowServiceChecker(Checker):
    Type: str = "windows-service"
    ServiceName: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)
        self.ServiceName = settings["name"]

    def GetName(self) -> str:
        return f"Window Service ({self.ServiceName})"

    async def DoCheckAsync(self) -> CheckResult:

        try:
            service = psutil.win_service_get(self.ServiceName)
            service = service.as_dict()

            if service['status'] == 'running':
                return self.Success()
            else:
                return self.Error("The service is not started.")

        except:
            return self.Error("The service does not exist.")
