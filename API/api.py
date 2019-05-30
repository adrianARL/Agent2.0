import cherrypy


@cherrypy.expose
class API:

    def __init__(self, agent, host='10.1.136.179', port=8000):
        self.agent = agent
        self.host = host
        self.port = port

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def execute_service(self):
        self.agent.desde_API(cherrypy.request.json)
        return "Voy a ejecutar el servicio"

    def start(self, silent_access=True):
        cherrypy.server.socket_host = self.host
        cherrypy.server.socket_port = self.port
        cherrypy.config.update({'log.screen': not silent_access})
        cherrypy.quickstart(API(self.agent))

    def stop(self):
        cherrypy.engine.exit()
