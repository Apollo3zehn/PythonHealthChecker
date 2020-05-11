import importlib
import inspect
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .BaseTypes import CheckResult

_notificationState: Dict[int, datetime] = {}

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

    global _notificationState

    now = datetime.now()
    _notificationState = { group:lastNotification for (group, lastNotification) in _notificationState.items() if now.date() == lastNotification.date() }
    # _notificationState = { group:lastNotification for (group, lastNotification) in _notificationState.items() if (now - lastNotification).total_seconds() <= 30 }
    filteredCheckResult = {}

    for (group, results) in checkResult.items():

        filteredResults = []

        for checkResult in results:
            
            key = f"{group}/{checkResult.Name}/{checkResult.Message}"

            # if check error occured recently
            if checkResult.HasError and not key in _notificationState:
                filteredResults.append(checkResult)
                _notificationState[key] = now

        if any(filteredResults):
            filteredCheckResult[group] = filteredResults

    return filteredCheckResult
