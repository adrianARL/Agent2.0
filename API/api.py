import cherrypy
import pymongo
import requests


@cherrypy.expose
class API(object):

    IP_DB = '10.0.2.16'
    # IP_DB = '127.0.0.1'
    PORT_DB = 27017

    def __init__(self, agent, host='localhost', port=8000):
        self.agent = agent
        self.host = host
        self.port = port
        self.leader_url = "http://{}:8000".format(self.agent.node_info['leaderIP'])
        client = pymongo.MongoClient(self.IP_DB, self.PORT_DB)
        self.agent_collection = client.globalDB.nodes
        self.service_catalog = client.globalDB.service_catalog

    def GET(self, obj=None, id=None):
        if obj == "agent":
            if id:
                # devolver info del agent
                pass
            else:
                #devolver info de todos los agent
                pass
        elif obj == "service":
            if id:
                # devolver info del service
                pass
            else:
                #devolver info de todos los services
                pass

    @cherrypy.tools.json_in()
    def POST(self, action=None):
        print(action, cherrypy.request.json)
        if action == "register_agent":
            pass
        elif action == "request_service":
            pass
        elif action == "execute_service":
            pass
        elif action == "response_service":
            pass

    @cherrypy.tools.json_in()
    def PUT(self, action=None):
        if action == "update_agent":
            pass

    def DELETE(self, action=None):
        if action == "delete_agent":
            pass

    def OPTIONS(self):
        print("opcioneeeeees")
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Origin, Content-Type'
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Content-Type'] = '*'
        possible_methods = ('PUT', 'DELETE', 'PATCH', 'POST')
        methods = [http_method for http_method in possible_methods
                   if hasattr(self, http_method)]
        cherrypy.response.headers['Access-Control-Allow-Methods'] = ','.join(methods)

    def start(self, silent_access=False):
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [
                    ('Access-Control-Allow-Origin', '*'),
                    ('Content-Type', '*')
                ]
            }
        }
        cherrypy.config.update({'log.screen': not silent_access})
        cherrypy.server.socket_host = self.host
        cherrypy.server.socket_port = self.port
        cherrypy.quickstart(API(self.agent), '/', conf)

    def stop(self):
        cherrypy.engine.exit()

    def register_agent(self):
        if cherrypy.request.method == "POST":
            body = cherrypy.request.json
            try:
                nodeID = self.agent_collection.find_and_modify(query= { '_id': 'nodeID' },update= { '$inc': {'seq': 1}}, new=True ).get('seq')
                body['_id'] = str(int(nodeID))
                body['nodeID'] = str(int(nodeID))
                body['leaderID'] = self.agent.node_info["nodeID"]
                self.agent_collection.insert_one(body)
            except pymongo.errors.DuplicateKeyError as e:
                nodeID = post_topoDB(body)
            return str(int(nodeID))

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

    def delete_agent(self):
        if cherrypy.request.method == "DELETE":
            selec = cherrypy.request.json
            self.agent_collection.delete_one(selec)

    def update_agent(self):
        if cherrypy.request.method == "PUT":
            body = cherrypy.request.json
            id = body['nodeID'].strip("0")
            self.agent_collection.update({'_id': id},{"$set":body},True)

    def get_service(self, input=None):
        if cherrypy.request.method == "GET":
            input = cherrypy.request.json
        if input:
            selec = {"_id": input["service_id"]}
            service = self.service_catalog.find_one(selec);
            return service
        else:
            return None

    def request_service(self):
        if cherrypy.request.method == "POST":
            service = cherrypy.request.json
            self.agent.service_execution.request_service(service)

    def execute_service(self, service=None):
        if cherrypy.request.method == "POST":
            service = cherrypy.request.json
        if service:
            self.agent.runtime.execute_service(service)

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
                self.agent.node_info['nodeID'] = str(int(nodeID))
                self.agent_collection.insert_one(self.agent.node_info)
                status_code = 200
        if status_code == 200:
            self.agent.node_info["nodeID"] = nodeID
            print("Se ha registrado el agent correctamente con id {}".format(self.agent.node_info["nodeID"]))
        else:
            print("No se ha podido registrar el agent")

    def delegate_service(self, service, agent_ip):
        try:
            status_code = requests.post("http://"+agent_ip+":8000/execute_service", json=service).status_code
        except Exception as e:
            print(e)
            status_code = -1
        if status_code != 200:
            print("No se ha podido delegar el servicio {} al agent".format(service["service_id"]))

    def request_service_to_leader(self, service):
        try:
            status_code = requests.post(self.leader_url+"/request_service", json=service).status_code
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
