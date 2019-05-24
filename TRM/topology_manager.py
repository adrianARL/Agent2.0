import requests
import json

class TopologyManager:

    def __init__(self, DB_ip, DB_port):
        self.URL = "http://"+DB_ip+":"+str(DB_port)+"/"
        self.post_URL = self.URL + "post_topoDB"
        self.update_URL = self.URL + "update_topoDB"
        self.get_URL = self.URL + "get_topoDB"
        self.del_URL = self.URL + "del_topoDB"
        self.reset_URL = self.URL + "reset_topoDB"
        self.get_service_URL = self.URL + "get_serviceDB"

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
                return json.loads(json.loads(response.text)[0])
            else:
                return None
        except:
            return -1

    def get_my_agents(self, zone):
        try:
            PARAMS = "selec={'zone':"+"'"+zone+"'}"
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
                return json.loads(json.loads(response.text)[0])
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
