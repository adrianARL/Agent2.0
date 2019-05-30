import cherrypy


@cherrypy.expose
class API:

    def __init__(self, agent, host='localhost', port=8000):
        self.agent = agent
        self.host = host
        self.port = port

    def start(self, silent_access=False):
        cherrypy.server.socket_host = self.host
        cherrypy.server.socket_port = self.port
        cherrypy.config.update({'log.screen': not silent_access})
        cherrypy.quickstart(API(self.agent))

    def stop(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def execute_service(self):
        pass
