import importlib
import inspect
import os
import platform
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .BaseTypes import CheckResult, NotificationState

_lastRunId: str
_stageMap: Dict[str, NotificationState] = {}
_muteMap: Dict[str, NotificationState] = {}

def LoadExtensions() -> List:
    extensionFolderPath = "src/Extensions"
    extensionFiles = os.listdir(extensionFolderPath)
    modules = [_loadModule(extensionFile) for extensionFile in extensionFiles]
    extensions = [potentialExtension[1] for module in modules for potentialExtension in inspect.getmembers(module) if inspect.isclass(potentialExtension[1])]

    return extensions

def _loadModule(extensionFile: str):
    moduleName = f".{extensionFile.split('.')[0]}"
    packageName = "src.Extensions"
    module = importlib.import_module(moduleName, package=packageName)
    importlib.reload(module)

    return module

def PrepareLocalAppdata() -> str:

    system = platform.system()

    if system == "Linux":
        folderPath = os.path.join(os.getenv("HOME"), ".config", "PythonHealthChecker")

    elif system == "Windows":
        folderPath = os.path.join(os.getenv("LOCALAPPDATA"), "PythonHealthChecker")

    else:
        raise Exception(f"The platform '{system}' is not supported.")

    Path(folderPath).mkdir(parents=True, exist_ok=True)

    return folderPath

def ThrottleNotifications(checkResult: Dict[str, List[CheckResult]]) -> Dict[str, List[CheckResult]]:

    global _lastRunId
    global _stageMap
    global _muteMap

    now = datetime.now()
    currentRunId = uuid.uuid4()
    filteredCheckResult = {}

    # remove notifications older than 1 day
    _stageMap = { group:lastNotification for (group, lastNotification) in _stageMap.items() if now.date() == lastNotification.Date }
    _muteMap = { group:lastNotification for (group, lastNotification) in _muteMap.items() if now.date() == lastNotification.Date }

    # for each group
    for (group, results) in checkResult.items():

        filteredResults = []

        for checkResult in results:
            
            key = f"{group}/{checkResult.Name}/{checkResult.Message}"
            notificationState = NotificationState(currentRunId, now.date())

            # if check failed
            if checkResult.HasError:

                # if failed check was not yet notified today
                if not key in _muteMap:

                    # if check failed twice in a row
                    if key in _stageMap and _stageMap[key].RunId == _lastRunId:
                        filteredResults.append(checkResult)
                        _muteMap[key] = notificationState
                        _stageMap.pop(key)

                    else:
                        _stageMap[key] = notificationState                   

        if any(filteredResults):
            filteredCheckResult[group] = filteredResults

    _lastRunId = currentRunId

    return filteredCheckResult
