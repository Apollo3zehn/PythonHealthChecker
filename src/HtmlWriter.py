import os
from datetime import datetime
from typing import Dict, List

from .BaseTypes import CheckResult, CheckResultType


class HtmlWriter:

    _indexFilePath: str
    _refreshInterval: int

    def __init__(self, indexFilePath: str, refreshInterval: int):
        self._indexFilePath = indexFilePath
        self._refreshInterval = refreshInterval

        if not os.path.isfile(self._indexFilePath):
            with open(self._indexFilePath, "w") as file:
                file.write("""
<h2>The checks are currently being executed, please wait a moment ...</h2>
<script>
    setTimeout(function() {{
        location.reload();
    }}, 10000);
</script>
""")

    def WriteResult(self, result: Dict[str, List[CheckResult]]):

        contents = [self._getGroupContent(group, checkResults) for (group, checkResults) in result.items()]
        joinChar = "\n"

        renderFragment = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Health Checker</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" type="text/css" href="static/lib/font-awesome/css/all.min.css" />
    <link rel="stylesheet" type="text/css" href="static/site.css">
</head>
<body>
    <div class="headline">
        <h1>Health Checker</h1>
        <div class="time">Last update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
    </div>
    <div class="main">
        {joinChar.join(contents)}
    </div>
    <script src="static/lib/font-awesome/js/all.min.js"></script>
    <script>
        setTimeout(function() {{
            location.reload();
        }}, {self._refreshInterval * 1000});
    </script>
</body>
</html>
"""

        with open(self._indexFilePath, "w") as file:
            file.write(renderFragment)

    def _getGroupContent(self, group: str, checkResults: List[CheckResult]) -> str:
        joinChar = "\n"
        contents = [self._getContent(checkResult) for checkResult in checkResults]
        renderFragment = f"""
<h2>{group}</h2>
<div class="group">
    {joinChar.join(contents)}
</div>
"""
        return renderFragment

    def _getContent(self, checkResult: CheckResult) -> str:

        warning = " "
        error = " "

        if checkResult.ResultType == CheckResultType.Success:
            content = f'<div class="check-icon"><i class="fas fa-check"></i></div>'

        elif checkResult.ResultType == CheckResultType.Warning:
            warning = " warning"
            content = f'<div class="check-icon"><i class="fas fa-exclamation-circle"></i></div>'

        elif checkResult.ResultType == CheckResultType.Error:
            error = " error"
            content = f'<div class="check-icon"><i class="fas fa-exclamation-circle"></i></div>'

        else:
            raise Exception(f"The check result type '{checkResult.ResultType}' is unknown")
            

        content += '<div class="check-wrapper">'
        content += f'<div class="check-type">{checkResult.Name}</div>'

        if checkResult.Message != "":
            content += f'<div class="check-message">{checkResult.Message}</div>'

        content += '</div>'

        renderFragment = f"""
<div class="check-result{warning}{error}">
    {content}
</div>
"""

        return renderFragment
