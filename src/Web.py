import cherrypy

class Controller(object):

    HtmlFilePath: str

    def __init__(self, htmlFilePath: str):
        self.HtmlFilePath = htmlFilePath

    @cherrypy.expose
    def index(self):
        return open(self.HtmlFilePath)
