import json
from datetime import datetime
from logging import Logger
from typing import Dict

import cherrypy

from .BaseTypes import CheckResult, CheckResultType


class Application:

    HtmlFilePath: str

    def __init__(self, htmlFilePath: str):
        self.HtmlFilePath = htmlFilePath

    @cherrypy.expose
    def index(self):
        return open(self.HtmlFilePath)

@cherrypy.expose
class API:

    Cache: Dict[str, CheckResult]
    Logger: Logger

    def __init__(self, cache: Dict[str, CheckResult], logger: Logger):
        self.Cache = cache
        self.Logger = logger
    
    def GET(self, identifier):

        if identifier in self.Cache:

            checkResult = self.Cache[identifier]

            checkResultDict = {
                "identifier": identifier,
                "name": checkResult.Name,
                "resultType": checkResult.ResultType.value,
                "message": checkResult.Message,
                "infoUrl": checkResult.InfoUrl,
                "created": checkResult.Created.isoformat()
            }

            checkResultJson = json.dumps(checkResultDict)
            cherrypy.response.headers['Content-Type'] = 'application/json'

            return checkResultJson.encode('utf8')

        else:
            raise cherrypy.HTTPError(status=404, message="The requested check result was not found.")

    def POST(self):

        # binary -> json
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        checkResultJson = json.loads(rawData)

        # create CheckResult
        identifier = checkResultJson["identifier"]
        name = checkResultJson["name"]
        resultType = CheckResultType(int(checkResultJson["resultType"]))
        message = checkResultJson["message"]
        infoUrl = checkResultJson["infoUrl"]
        notifiers = []

        checkResult = CheckResult(name, resultType, message, infoUrl, notifiers)

        # populate cache
        self.Logger(f"Fill cache with check result {identifier} (received via HTML POST).")
        self.Cache[identifier] = checkResult
