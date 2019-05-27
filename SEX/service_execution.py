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
        Thread(target=self.process_results).start()

    def generate_id(self):
        random_id = uuid.uuid4()
        if random_id in self.service_ids.keys():
            return self.generate_id()
        return random_id

    def wait_services(self):
        while True:
            if len(self.agent.services) > 0:
                service = self.agent.services.pop(0)
                if self.agent.node_info["role"] != "agent":
                    reg_service = self.agent.topology_manager.get_service(service["service_id"])
                    self.fill_service(service, reg_service)
                if self.can_execute_service(service, self.agent.node_info):
                    print("Puedo ejecutar {}".format(service.items()))
                    result = self.agent.runtime.execute_service(service)
                    self.agent.services_results.append(result)
                elif(self.agent.node_info["role"] != "agent"):
                    # print("Delego el servicio a un agent {}".format(service.items()))
                    th_attend_service = Thread(target=self.attend_service, args=(service, ))
                    th_attend_service.start()
                    self.th_attend_services.append(th_attend_service)
                else:
                    # print("Delego el servicio al leader {}".format(service.items()))
                    service["type"] = "service"
                    if "id" in service:
                        service["origin_id"] = service["id"]
                    service["id"] = self.generate_id()
                    self.agent.send_dict(service)

    def attend_service(self, service):
        if "service_id" in service.keys():
            reg_service = self.agent.topology_manager.get_service(service["service_id"])
            agents = self.agent.topology_manager.get_my_agents(self.agent.node_info["zone"])
            attended = False
            if(agents):
                for agent in agents:
                    print("Agent : ", agent.get("IoT"))
                    print("Service : ", reg_service.get("IoT"))
                    if(self.can_execute_service(reg_service, agent)):
                        reg_service["id"] = service["id"]
                        reg_service["type"] = service["type"]
                        self.agent.send_dict_to(reg_service, agent["nodeID"])
                        attended = True
                        break
            if not attended:
                result = {
                    "type": "service_result",
                    "id": service["id"],
                    "status": "unattended",
                    "output": ""
                }
                self.agent.services_results.append(result)




    def can_execute_service(self, service, node_info):
        try:
            return set(service["IoT"]).issubset(set(node_info["IoT"]))
        except:
            return False

    def process_results(self):
        while True:
            if len(self.agent.services_results) > 0:
                service_result = self.agent.services_results.pop(0)
                if self.agent.node_info["role"] != "agent":
                    id = service_result["id"]
                    agent_id = self.service_ids[id]["agent_id"]
                    service_result["id"] = self.service_ids[id]["origin_id"]
                    print("Respondo: ", service_result)
                    self.agent.send_dict_to(service_result, agent_id)
                else:
                    self.agent.send_dict(service_result)


    def fill_service(self, service, reg_service):
        random_id = self.generate_id()
        service["origin_id"] = service["id"]
        service["id"] = random_id
        self.service_ids[random_id] = {
            "origin_id": service["origin_id"],
            "agent_id": service["agent_id"]
        }
        print("fill service:")
        print(self.service_ids)
        print()
        for key in reg_service.keys():
            if not key in service.keys():
                service[key] = reg_service[key]
