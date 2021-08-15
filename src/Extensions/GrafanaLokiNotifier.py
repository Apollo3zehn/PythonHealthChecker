import json
import os
from datetime import datetime
from typing import Dict, List

import requests

from ..BaseTypes import CheckResult, CheckResultType, Notifier


class GrafanaLokiNotifier(Notifier):
    Type: str = "grafana-loki"
    Url: str
    Labels: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)

        self.Url = settings["url"]
        self.Labels = settings["labels"]

    async def NotifyAsync(self, checkResult: Dict[str, List[CheckResult]]):

        url = f"{self.Url}/api/v1/push"

        headers = {
            'Content-type': 'application/json'
        }

        for (group, checkResults) in checkResult.items():

            for result in checkResults:

                timestamp = int(datetime.utcnow().timestamp() * 1e9)

                if (result.Message is not None and result.Message != ""):
                    message = f"[{group}] {result.Name} = {result.Message}"

                else:
                    message = f"[{group}] {result.Name}"

                if result.ResultType == CheckResultType.Warning:
                    level = "warning"

                elif result.ResultType == CheckResultType.Error:
                    level = "error"

                else:
                    level = "info"

                payload = {
                    "streams": [
                        { 
                            "stream": 
                            { 
                                "level": level 
                            }, 
                            "values": 
                            [ 
                                [ 
                                    timestamp,
                                    message 
                                ]
                            ]
                        }
                    ]
                }

                splittedLabels = self.Labels.split(",")

                for label in splittedLabels:
                    (key, value) = label.split("=", maxsplit=1)
                    key = key.lstrip().rstrip()
                    value = value.lstrip().rstrip()
                    payload["streams"][0]["stream"][key] = value

                reponse = requests.post(url, headers=headers, data=json.dumps(payload))

