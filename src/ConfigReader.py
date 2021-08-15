from itertools import groupby
from typing import Dict, List, Tuple

from .BaseTypes import Config


class ConfigReader():

    def Read(self, filePath: str) -> Config:

        notifiers: List[Dict[str, str]] = []
        checks: List[Dict[str, str]] = []

        with open(filePath, "r") as file:

            section: str
            notifier: Dict[str, str] = None
            check: Dict[str, str] = None

            for line in file:

                # skip empty lines
                if self._isNullOrWhiteSpace(line):
                    notifier = None
                    check = None
                    continue

                # skip comments
                if line.startswith("#"):
                    continue

                # detect section
                if line.startswith("[notifiers]"):
                    section = "notifiers"
                    continue

                elif line.startswith("[checks]"):
                    section = "checks"
                    continue

                # go
                if section == "notifiers":

                    if notifier is None:
                        notifier = {}
                        notifiers.append(notifier)

                    (option, value) = self._parseOption(line)
                    notifier[option] = value

                elif section == "checks":

                    if check is None:
                        check = {}
                        checks.append(check)

                    (option, value) = self._parseOption(line)
                    check[option] = value

            for check in checks:
                if not "group" in check:
                    check["group"] = "Default"

        sortedChecks = sorted(checks, key=lambda check: check["group"])
        groupedCheckers = {key:list(group) for key, group in groupby(sortedChecks, key = lambda check: check["group"])}

        return Config(notifiers, groupedCheckers)

    def _isNullOrWhiteSpace(self, value: str):
        return not value or value.isspace()

    def _parseOption(self, rawOption: str) -> Tuple[str, str]:
        parts = rawOption.split("=", maxsplit=1)
        option = parts[0].lstrip().rstrip()
        value = parts[1].lstrip().rstrip()

        return (option, value)
