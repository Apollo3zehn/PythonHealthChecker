import cherrypy

class Controller(object):

    @cherrypy.expose
    def index(self):
        return open('./src/wwwroot/index.html')