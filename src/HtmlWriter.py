import os
from datetime import datetime
from typing import Dict, List

from .BaseTypes import CheckResult


class HtmlWriter:

    IndexFilePath: str

    def __init__(self, indexFilePath: str):
        self.IndexFilePath = indexFilePath

        if not os.path.isfile(self.IndexFilePath):
            with open(self.IndexFilePath, "w") as file:
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
        }}, 10000);
    </script>
</body>
</html>
"""

        with open(self.IndexFilePath, "w") as file:
            file.write(renderFragment)

    def _getGroupContent(self, group: str, checkResults: List[CheckResult]) -> str:
        joinChar = "\n"
        contents = [self._getContent(checkResult) for checkResult in sorted(checkResults, key = lambda x: not x.HasError)]
        renderFragment = f"""
<h2>{group}</h2>
<div class="group">
    {joinChar.join(contents)}
</div>
"""
        return renderFragment

    def _getContent(self, checkResult: CheckResult) -> str:
        
        if checkResult.HasError:
            error = " error"
            content = f'<div class="check-icon"><i class="fas fa-exclamation-circle"></i></div>'
        else:
            error = " "
            content = f'<div class="check-icon"><i class="fas fa-check"></i></div>'

        content += '<div class="check-wrapper">'
        content += f'<div class="check-type">{checkResult.Name}</div>'

        if checkResult.Message != "":
            content += f'<div class="check-message">{checkResult.Message}</div>'

        content += '</div>'

        renderFragment = f"""
<div class="check-result{error}">
    {content}
</div>
"""

        return renderFragment
