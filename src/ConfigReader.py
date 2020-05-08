from itertools import groupby
from typing import Dict, List, Tuple

from .BaseTypes import Config


class ConfigReader():

    def Read(self, filePath: str) -> Config:

        notifiers: List[Dict[str, str]] = []
        checks: List[Dict[str, str]] = []

        with open(filePath, "r") as file:

            section: str
            notifier: Dict[str, str]
            check: Dict[str, str]

            for line in file:

                # skip empty lines
                if self._isNullOrWhiteSpace(line):
                    continue

                # detect section
                if line.startswith("# notifications"):
                    section = "notifiers"
                    continue

                elif line.startswith("# checks"):
                    section = "checks"
                    continue

                # go
                if section == "notifiers":

                    if line.startswith("["):
                        notifier = {}
                        id = line.lstrip("[").rstrip().rstrip("]")
                        notifier["id"] = id
                        notifiers.append(notifier)

                    else:
                        (option, value) = self._parseOption(line)
                        notifier[option] = value

                elif section == "checks":

                    if line.startswith("["):
                        check = {}
                        groupName = line.lstrip("[").rstrip().rstrip("]")
                        check["group"] = groupName
                        checks.append(check)

                    else:
                        (option, value) = self._parseOption(line)
                        check[option] = value

        groupedCheckers = {key:list(group) for key, group in groupby(checks, key = lambda check: check["group"])}

        return Config(notifiers, groupedCheckers)

    def _isNullOrWhiteSpace(self, value: str):
        return not value or value.isspace()

    def _parseOption(self, rawOption: str) -> Tuple[str, str]:
        parts = rawOption.split("=")
        option = parts[0].lstrip().rstrip()
        value = parts[1].lstrip().rstrip()

        return (option, value)
