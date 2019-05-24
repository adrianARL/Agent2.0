import time
import uuid
from threading import Thread
# from frontend_connection import FrontendConnection


class ServiceExecution:

    def __init__(self, agent):
        self.agent = agent
        self.th_wait_services = Thread(target=self.wait_services)
        self.th_attend_services = []
        self.service_ids = {}
        Thread(target=self.wait_services).start()

    def generate_id(self):
        random_id = uuid.uuid4()
        if random_id in self.service_ids.keys():
            return self.generate_id()
        return random_id

    def wait_services(self):
        while True:
            if len(self.agent.services) > 0:
                service = self.agent.services.pop(0)
                if self.can_execute_service(service, self.agent.node_info):
                    print("Puedo ejecutar {}".format(service.items()))
                    result = self.agent.runtime.execute_service(service)
                    if "id" in service.keys():
                        if self.agent.node_info["role"] != "agent":
                            id = service["id"]
                            self.agent.send_dict_to(result, self.service_ids[id])
                        else:
                            self.agent.send_dict(result)
                elif(self.agent.node_info['role'] != "agent"):
                    print("Delego el servicio a un agent {}".format(service.items()))
                    random_id = self.generate_id()
                    service["id"] = random_id
                    self.service_ids[random_id] = service['agent_id']
                    th_attend_service = Thread(target=self.attend_service, args=(service, ))
                    th_attend_service.start()
                    self.th_attend_services.append(th_attend_service)
                else:
                    print("Delego el servicio al leader {}".format(service.items()))
                    service["type"] = "service"
                    self.agent.send_dict(service)

    def attend_service(self, service):
        if "service_id" in service.keys():
            reg_service = self.agent.topology_manager.get_service(service["service_id"])
            agents = self.agent.topology_manager.get_my_agents(self.agent.node_info["zone"])
            if(agents):
                for agent in agents:
                    print("Agent : ", agent.get("IoT"))
                    print("Service : ", reg_service.get("IoT"))
                    if(self.can_execute_service(reg_service, agent)):
                        reg_service["id"] = service["id"]
                        reg_service["type"] = service["type"]
                        self.agent.send_dict_to(reg_service, agent["nodeID"])
                        break



    def can_execute_service(self, service, node_info):
        try:
            return set(service["IoT"]).issubset(set(node_info["IoT"]))
        except:
            return False
