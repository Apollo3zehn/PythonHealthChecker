import json
from datetime import datetime
from typing import Dict

import cherrypy

from .BaseTypes import CacheEntry, CheckResult, CheckResultType


class Application:

    HtmlFilePath: str

    def __init__(self, htmlFilePath: str):
        self.HtmlFilePath = htmlFilePath

    @cherrypy.expose
    def index(self):
        return open(self.HtmlFilePath)

@cherrypy.expose
class API:
    Cache: Dict[str, CacheEntry]

    def __init__(self, cache: Dict[str, CacheEntry]):
        self.Cache = cache
    
    def POST(self):
        # binary -> json
        rawData = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        checkResultJson = json.loads(rawData)

        # create CheckResult
        identifier = checkResultJson["identifier"]
        name = checkResultJson["name"]
        resultType = CheckResultType(int(checkResultJson["resultType"]))
        message = checkResultJson["message"]
        notifiers = []

        checkResult = CheckResult(name, resultType, message, notifiers)

        # populate cache
        self.Cache[identifier] = CacheEntry(checkResult, datetime.now())
