import inspect
from logging import Logger
from typing import Dict, List

from .BaseTypes import CheckResult, Config, Notifier


class NotifyManager:
    
    Config: Config
    NotifierTypes: List[Notifier]
    Logger: Logger

    def __init__(self, config: Config, extensions: List, logger: Logger):
        self.Config = config
        self.NotifierTypes = [notifierType for notifierType in extensions if issubclass(notifierType, Notifier) and not inspect.isabstract(notifierType)]
        self.Logger = logger

    async def NotifyAsync(self, checkResult: Dict[str, List[CheckResult]]):

        notifiers = [self._getNotifier(notify) for notify in self.Config.Notifiers]

        for notifier in notifiers:
            filteredCheckResult = {}

            for (group, results) in checkResult.items():
                filteredResults = [result for result in results if notifier.Id in result.Notifiers]

                if any(filteredResults):
                    filteredCheckResult[group] = filteredResults

            if any(filteredCheckResult):
                self.Logger.info(f"Notifier {notifier.Id} notifies group {group}.")

                try:
                    await notifier.NotifyAsync(filteredCheckResult)
                except Exception as ex:
                    self.Logger.error(msg=str(ex), exc_info=ex)

    def _getNotifier(self, notify) -> Notifier:
        return next((notifier(notify) for notifier in self.NotifierTypes if notifier.Type == notify["type"]))
