import requests
import json
import time
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
            PARAMS = {'leaderID' : self.agent.node_info["nodeID"]}
            agents = self.agent.API.get_agents(PARAMS)
            for agent in agents:
                self.agent.agents_alive[agent["myIP"]] = agent["status"]
        except Exception as e:
            print(e)
            pass

    def check_alive_agents(self):
        while True:
            for agent_ip in list(self.agent.agents_alive.keys()):
                if agent_ip != self.agent.node_info["myIP"]:
                    self.agent.API.check_alive(agent_ip)
            time.sleep(2)

    def change_agent_status(self, agent_ip, status):
        if self.agent.agents_alive[agent_ip] != status:
            print("Se ha actualizado el estado {} al agent con ip {}".format(status, agent_ip))
            self.agent.API.update_agent({'myIP': agent_ip, 'status': status})
            self.agent.agents_alive[agent_ip] = status
