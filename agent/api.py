import cherrypy
import pymongo
import requests
import json
import datetime


@cherrypy.expose
class API(object):

    def __init__(self, agent, host='localhost', port=8000):
        self.agent = agent
        self.host = host
        self.port = port
        self.leader_url = "http://{}:8000".format(self.agent.node_info['leaderIP'])
        if self.agent.node_info["role"] != "agent":
            client = pymongo.MongoClient(self.agent.node_info["ipDB"], self.agent.node_info["portDB"])
            self.agent_collection = client.globalDB.nodes
            self.service_catalog = client.globalDB.service_catalog
        today = datetime.date.today()

    def GET(self, obj=None, id=None):
        if obj == "agent":
            return self.return_data(self.get_agents(id))
        elif obj == "service":
            return self.return_data(self.get_service(id))
        elif obj == "alive":
            return "Alive".encode()

    @cherrypy.tools.json_in()
    def POST(self, action=None):
        info = cherrypy.request.json
        result = ""
        if action == "register_agent":
            result = self.register_agent(info)
        elif action == "request_service":
            result = self.request_service(info)
        elif action == "execute_service":
            result = self.execute_service(info)
        elif action == "response_service":
            result = self.response_service(info)
        return self.return_data(result)

    @cherrypy.tools.json_in()
    def PUT(self, action=None):
        info = cherrypy.request.json
        if action == "update_agent":
            self.update_agent(info)

    def DELETE(self, action=None):
        info = cherrypy.request.json
        if action == "delete_agent":
            self.delete_agent(info)

    def OPTIONS(self, a=None, b=None):
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Origin, Content-Type'
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Content-Type'] = '*'
        possible_methods = ('PUT', 'DELETE')
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

    def register_agent(self, body):
        try:
            nodeID = self.agent_collection.find_and_modify(query= { '_id': 'nodeID' },update= { '$inc': {'seq': 1}}, new=True ).get('seq')
            body['_id'] = str(int(nodeID))
            body['nodeID'] = str(int(nodeID)).zfill(10)
            body['leaderID'] = self.agent.node_info["nodeID"]
            body['ipDB'] = self.agent.node_info["ipDB"]
            body['portDB'] = self.agent.node_info["portDB"]
            self.agent_collection.insert_one(body)
            self.agent.agents_alive[body["myIP"]] = 1
        except pymongo.errors.DuplicateKeyError as e:
            nodeID = self.register_agent(body)
        return json.dumps(body)

    def get_agents(self, selec=None):
        if selec:
            try:
                agent_list = []
                agents = self.agent_collection.find(selec)
                if agents:
                    for agent_mongo in agents:
                        agent_list.append(agent_mongo)
                return agent_list
            except Exception as e:
                return []
                pass
                #print(e)

    def delete_agent(self, selec):
        self.agent_collection.delete_one(selec)

    def update_agent(self, body):
        if "nodeID" in body.keys():
            id = body['nodeID'].strip("0")
            self.agent_collection.update({'_id': id},{"$set":body},True)
        else:
            ip = body["myIP"]
            self.agent_collection.update({'myIP': ip},{"$set":body},True)

    def get_service(self, input=None):
        if input:
            # obtener un servicio
            if type(input) is str:
                #print("entro con {}".format(input))
                service = self.service_catalog.find_one(input)
                #print("salgo con {}".format(service))
            else:
                selec = {"_id": input["service_id"]}
                service = self.service_catalog.find_one(selec);
            return service
        else:
            # obtener todos los servicios
            services = self.service_catalog.find();
            return list(services)

    def request_service(self, service):
        #print("REQUEST_SERVICE:", service)
        return self.agent.service_execution.request_service(service)

    def execute_service(self, service):
        return self.agent.runtime.execute_service(service)

    def response_service(self, service_result):
        return self.agent.service_execution.attend_response(service_result)

    def register_to_leader(self):
        if 'nodeID' not in self.agent.node_info:
            try:
                registered = requests.post(self.leader_url + "/register_agent", json=self.agent.node_info)
                status_code = registered.status_code
                self.agent.node_info["nodeID"] = registered.text.zfill(10)
            except:
                status_code = -1
                if self.agent.node_info["role"] != "agent":
                    self.register_agent(self.agent.node_info)
                    status_code = 200
            if status_code == 200:
                file = open("/etc/agent/agent.conf", "w")
                json.dump({"nodeID": self.agent.node_info["nodeID"]}, file)
                file.close()
                #print("Se ha registrado el agent correctamente con id {}".format(self.agent.node_info["nodeID"]))
            else:
                pass
                #print("No se ha podido registrar el agent")

    def delegate_service(self, service, agent_ip):
        try:
            response = requests.post("http://"+agent_ip+":8000/execute_service", json=service)
            status_code = response.status_code
            return json.loads(response.text)
        except Exception as e:
            #print(e)
            status_code = -1
        if status_code != 200:
            pass
            #print("No se ha podido delegar el servicio {} al agent".format(service["service_id"]))

    def request_service_to_agent(self, service, agent_ip):
        try:
            response = requests.post("http://"+agent_ip+":8000/request_service", json=service)
            status_code = response.status_code
            return json.loads(response.text)
        except Exception as e:
            #print(e)
            status_code = -1
        if status_code != 200:
            pass
            #print("No se ha podido pedir el servicio {} al leader".format(service["service_id"]))

    def request_service_to_leader(self, service):

        try:
            response = requests.post(self.leader_url+"/request_service", json=service)
            status_code = response.status_code
            return json.loads(response.text)
        except Exception as e:
            #print(e)
            status_code = -1
        if status_code != 200:
            pass
            #print("No se ha podido pedir el servicio {} al leader".format(service["service_id"]))

    def request_service_to_me(self, service):
        try:
            response = requests.post("http://"+self.agent.node_info["myIP"]+":8000/request_service", json=service)
            status_code = response.status_code
            return json.loads(response.text)
        except Exception as e:
            #print(e)
            status_code = -1
            return
        if status_code != 200:
            pass
            #print("No me he podido pedir el servicio")


    def register_cloud_agent(self):
        body = self.agent.node_info
        try:
            body['_id'] = "0"
            body["nodeID"] = "0".zfill(10)
            self.agent_collection.insert_one(body)
            config = open("/etc/agent/config/device.config", "r")
            content = json.load(config)
            content["nodeID"] = body["nodeID"]
            config.close()
            config = open("/etc/agent/config/device.config", "w")
            json.dump(content, config)
            config.close()
        except pymongo.errors.DuplicateKeyError as e:
            pass
        except Exception as e:
            pass
            #print(e)

    def return_data(self, data):
        result = ""
        if isinstance(data, dict):
            result = json.dumps(data)
        elif isinstance(data, int):
            result = str(data)
        elif isinstance(data, list):
            result = str(data)
        elif data is not None:
            result = data
        return result.encode()

    def check_alive(self, agent_ip):
        try:
            requests.get("http://"+agent_ip+":8000/alive")
            self.agent.topology_manager.change_agent_status(agent_ip, 1)
        except:
            self.agent.topology_manager.change_agent_status(agent_ip, 0)
