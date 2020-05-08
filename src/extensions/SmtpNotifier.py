import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Dict, List

from ..BaseTypes import CheckResult, Notifier


class SmtpNotifier(Notifier):
    Type: str = "smtp"
    Security: str
    Address: str
    Port: int
    Password: str
    From: str
    To: str
    Subject: str

    def __init__(self, settings: Dict[str, str]):
        super().__init__(settings)

        self.Security = settings["security"]
        self.Server = settings["server"]
        self.Port = int(settings["port"])
        self.Password = settings["password"]
        self.From = settings["from"]
        self.To = settings["to"]
        self.Subject = settings["subject"]

    async def NotifyAsync(self, checkResult: Dict[str, List[CheckResult]]):

        if self.Security == "starttls":

            context = ssl.SSLContext(ssl.PROTOCOL_TLS)

            with smtplib.SMTP(self.Server, self.Port) as server:
                try:
                    server.starttls(context=context)
                    server.login(self.From, self.Password)

                    message = EmailMessage()
                    message.set_content("abc")
                    message['Subject'] = self.Subject
                    message['From'] = self.From
                    message['To'] = self.To
                    message.add_alternative(self.GetHtmlMessage(checkResult), subtype='html')

                    server.send_message(message)

                except Exception as e:
                    print(e)
                    
        else:
            raise Exception(f"The security type '{self.Security}' is not supported.")

    def GetHtmlMessage(self, result: Dict[str, List[CheckResult]]) -> str:

        contents = [self._getGroupContent(group, checkResults) for (group, checkResults) in result.items()]
        joinChar = "\n"
        renderFragment = f"""
<!DOCTYPE html>
<html>
<head>
</head>
<body style="color: #e6e6e6; background-color: #1A1A1A">
    <div class="main">
        {joinChar.join(contents)}
    </div>
</body>
</html>
"""

        return renderFragment

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

        renderFragment = f"""
<div class="check-result" style="margin-bottom: 10px;">
    <h4 class="check-type" style="margin-bottom: 5px; margin-left: 20px;">{checkResult.Name}</h4>
    <div class="check-message" style="margin-left: 40px;">{checkResult.Message}</div>
</div>
"""

        return renderFragment