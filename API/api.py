import cherrypy
import pymongo
import requests


@cherrypy.expose
class API:

    IP_DB = '10.0.2.16'
    PORT_DB = 27017

    def __init__(self, agent, host='localhost', port=8000):
        self.agent = agent
        self.host = host
        self.port = port
        self.leader_url = "http://{}:8000".format(self.agent.node_info['leaderIP'])
        client = pymongo.MongoClient(self.IP_DB, self.PORT_DB)
        self.agent_collection = client.globalDB.nodes
        self.service_catalog = client.globalDB.service_catalog

    def start(self, silent_access=False):
        cherrypy.server.socket_host = self.host
        cherrypy.server.socket_port = self.port
        cherrypy.config.update({'log.screen': not silent_access})
        cherrypy.quickstart(API(self.agent))

    def stop(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    # Register agent a la topoDB
    def register_agent(self):
        if cherrypy.request.method == "POST":
            body = cherrypy.request.json
            try:
                nodeID = self.agent_collection.find_and_modify(query= { '_id': 'nodeID' },update= { '$inc': {'seq': 1}}, new=True ).get('seq')
                body['_id'] = str(int(nodeID))
                self.agent_collection.insert_one(body)
            except pymongo.errors.DuplicateKeyError as e:
                nodeID = post_topoDB(body)
            return str(int(nodeID))

    # Get all agents from topoDB
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_agents(self, **kwargs):
        print(kwargs)
        print(cherrypy.request.method)
        if cherrypy.request.method == "GET":
            selec = cherrypy.request.json
            try:
                agent_list=[]
                print("Entro al try")
                print(selec)
                for agent_mongo in self.agent_collection.find(selec):
                    agent_list.append(agent_mongo)
                return agent_list
            except:
                print("Entro except!!!!")
                print(selec)


    @cherrypy.expose
    @cherrypy.tools.json_in()
    # Delete agent from topoDB
    def delete_agent(self):
        if cherrypy.request.method == "DELETE":
            selec = cherrypy.request.json
            self.agent_collection.delete_one(selec)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    # Update agent info to topoDB
    def update_agent(self):
        if cherrypy.request.method == "PUT":
            body = cherrypy.request.json
            id = body['nodeID'].strip("0")
            self.agent_collection.update({'_id': id},{"$set":body},True)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_service(self):
        if cherrypy.request.method == "GET":
            selec = cherrypy.request.json
            service = self.service_catalog.find(selec);
            return service

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def request_service(self):
        if cherrypy.request.method == "POST":
            service = cherrypy.request.json
            self.agent.SEX.request_service(service)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def execute_service(self):
        if cherrypy.request.method == "POST":
            service = cherrypy.request.json
            self.agent.RT.execute_service(service)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def response_service(self):
        if cherrypy.request.method == "POST":
            service_result = cherrypy.request.json
            self.agent.SEX.add_service_result(service_result)

    def register_to_leader(self):
        try:
            registered = requests.post(self.leader_url + "/register_agent", json=self.agent.node_info)
            status_code = registered.status_code
        except:
            status_code = -1
        if status_code == 200:
            print("Se ha registrado el agent correctamente")
            self.agent.node_info["nodeID"] = registered.text.zfill(10)
        else:
            print("No se ha podido registrar el agent")
