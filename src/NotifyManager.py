import inspect
from typing import Dict, List

from .BaseTypes import CheckResult, Config, Notifier


class NotifyManager:
    
    Config: Config
    NotifierTypes: List[Notifier]

    def __init__(self, config: Config, extensions: List):
        self.Config = config
        self.NotifierTypes = [notifierType for notifierType in extensions if issubclass(notifierType, Notifier) and not inspect.isabstract(notifierType)]

    async def NotifyAsync(self, checkResult: Dict[str, List[CheckResult]]):

        notifiers = [self._getNotifier(notify) for notify in self.Config.Notifiers]

        for notifier in notifiers:
            filteredCheckResult = {}

            for (group, results) in checkResult.items():
                filteredResults = [result for result in results if notifier.Id in result.Notifiers]

                if any(filteredResults):
                    filteredCheckResult[group] = filteredResults

            if any(filteredCheckResult):
                await notifier.NotifyAsync(filteredCheckResult)

    def _getNotifier(self, notify) -> Notifier:
        return next((notifier(notify) for notifier in self.NotifierTypes if notifier.Type == notify["type"]))
