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
                body['leaderID'] = self.agent.node_info["nodeID"]
                self.agent_collection.insert_one(body)
            except pymongo.errors.DuplicateKeyError as e:
                nodeID = post_topoDB(body)
            return str(int(nodeID))

    # Get all agents from topoDB
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_agents(self, selec=None):
        if cherrypy.request.method == "GET":
            selec = cherrypy.request.json
        try:
            agent_list=[]
            for agent_mongo in self.agent_collection.find(selec):
                agent_list.append(agent_mongo)
            return agent_list
        except Exception as e:
            print(e)


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
    def get_service(self, input=None):
        if cherrypy.request.method == "GET":
            input = cherrypy.request.json
        if input:
            selec = {"_id": input["service_id"]}
            service = self.service_catalog.find_one(selec);
            return service
        else:
            return None

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def request_service(self):
        if cherrypy.request.method == "POST":
            service = cherrypy.request.json
            self.agent.service_execution.request_service(service)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def execute_service(self, service=None):
        if cherrypy.request.method == "POST":
            service = cherrypy.request.json
        if service:
            self.agent.runtime.execute_service(service)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def response_service(self):
        if cherrypy.request.method == "POST":
            service_result = cherrypy.request.json
            print(service_result)
            # self.agent.service_execution.add_service_result(service_result)

    def register_to_leader(self):
        try:
            registered = requests.post(self.leader_url + "/register_agent", json=self.agent.node_info)
            status_code = registered.status_code
            nodeID = registered.text.zfill(10)
        except:
            status_code = -1
            if self.agent.node_info["role"] != "agent":
                nodeID = self.agent_collection.find_and_modify(query= { '_id': 'nodeID' },update= { '$inc': {'seq': 1}}, new=True ).get('seq')
                self.agent.node_info['_id'] = str(int(nodeID))
                self.agent_collection.insert_one(self.agent.node_info)
                status_code = 200
        if status_code == 200:
            self.agent.node_info["nodeID"] = nodeID
            print("Se ha registrado el agent correctamente con id {}".format(self.agent.node_info["nodeID"]))
        else:
            print("No se ha podido registrar el agent")

    def request_service_to_leader(self, service):
        try:
            status_code = requests.post(self.leader_url + "/request_service", json=service).status_code
        except Exception as e:
            print(e)
            status_code = -1
        if status_code != 200:
            print("No se ha podido pedir el servicio {} al leader".format(service["service_id"]))

    def send_result(self, result, agent_ip):
        try:
            requests.post("http://"+agent_ip+":8000/response_service", json=result)
        except Exception as e:
            print(e)



    def register_cloud_agent(self):
        body = self.agent.node_info
        try:
            body['_id'] = "0"
            body["nodeID"] = "0".zfill(10)
            self.agent_collection.insert_one(body)
        except pymongo.errors.DuplicateKeyError as e:
            pass
        except Exception as e:
            print(e)
