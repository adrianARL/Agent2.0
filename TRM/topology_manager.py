import requests
import json
from threading import Thread


class TopologyManager:

    def __init__(self, agent, DB_ip, DB_port):
        self.agent = agent
        self.URL = "http://"+DB_ip+":"+str(DB_port)+"/"
        self.post_URL = self.URL + "post_topoDB"
        self.update_URL = self.URL + "update_topoDB"
        self.get_URL = self.URL + "get_topoDB"
        self.del_URL = self.URL + "del_topoDB"
        self.reset_URL = self.URL + "reset_topoDB"
        self.get_service_URL = self.URL + "get_serviceDB"
        if self.agent.node_info["role"] != "agent":
            Thread(target=self.check_alive_agents).start()

    def check_alive_agents(self):
        while True:
            for agent in self.agent.agents_alive.keys():
                if agent["nodeID"] != self.agent.node_info["nodeID"]:
                    self.agent.API.check_alive(agent["myIP"])

    def register(self, node_info):
        try:
            response = requests.post(self.post_URL, data=node_info)
            id = response.text[1:len(response.text)-1]
            return response.status_code, id
        except:
            return -1, None

    def update(self, node_info):
        try:
            response = requests.post(self.update_URL, data=node_info)
            return response.status_code
        except:
            return -1

    def get(self, nodeID):
        try:
            PARAMS = "selec={'nodeID':"+"'"+nodeID+"'}"
            response = requests.get(self.get_URL, PARAMS)
            if response.status_code == 200:
                return json.loads(json.loads(response.text)[0])[0]
            else:
                return None
        except:
            return -1

    def get_my_agents(self, zone):
        try:
            PARAMS = "selec={'status':'1','zone':"+"'"+zone+"'}"
            response = requests.get(self.get_URL, PARAMS)
            if response.status_code == 200:
                return json.loads(json.loads(response.text)[0])
            else:
                return None
        except:
            return -1

    def get_available_ambulances(self):
        try:
            PARAMS = str("selec={'device':'ambulance','status':'1'}")
            response = requests.get(self.get_URL, PARAMS)
            if response.status_code == 200:
                return json.loads(json.loads(response.text)[0])
            else:
                return None
        except:
            return -1

    def get_service(self, service_id):
        try:
            PARAMS = "selec={'_id':"+"'"+service_id+"'}"
            response = requests.get(self.get_service_URL, PARAMS)
            if response.status_code == 200:
                return json.loads(json.loads(response.text)[0])[0]
            else:
                return None
        except:
            return -1


    def delete(self, nodeID):
        try:
            PARAMS = "index={'nodeID':"+"'"+nodeID+"'}"
            response = requests.get(self.del_URL, PARAMS)
            return response.status_code
        except:
            return -1

    def reset(self):
        try:
            response = requests.get(self.reset_URL)
            return response.status_code
        except:
            return -1

    def change_agent_status(self, agent_ip, status):
        if self.agent.agents_alive[agent_ip] != status:
            self.agent.API.update_agent({'myIP': agent_ip, 'status': status})
