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
            self.get_my_agents()
            Thread(target=self.check_alive_agents).start()

    def get_my_agents(self):
        try:
            PARAMS = "selec={'leaderID':'"+self.agent.node_info["nodeID"]+"'}"
            agents = self.agent.API.get_agents(PARAMS)
            for agent in agents:
                self.agent.agents_alive[agent["myIP"]] = agent["status"]
        except:
            pass

    def check_alive_agents(self):
        while True:
            for agent in self.agent.agents_alive.keys():
                if agent["nodeID"] != self.agent.node_info["nodeID"]:
                    self.agent.API.check_alive(agent["myIP"])

    def change_agent_status(self, agent_ip, status):
        if self.agent.agents_alive[agent_ip] != status:
            self.agent.API.update_agent({'myIP': agent_ip, 'status': status})
