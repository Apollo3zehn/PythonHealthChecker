import json
from datetime import datetime
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

    def __init__(self, cache: Dict[str, CheckResult]):
        self.Cache = cache
    
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
        self.Cache[identifier] = checkResult
