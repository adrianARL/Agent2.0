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


    def wait_services(self):
        while True:
            if len(self.agent.services) > 0:
                print("Ento en services")
                service = self.agent.services.pop(0)
                print(service)
                print()
                if self.agent.node_info["role"] != "agent" and not self.can_execute_service(service, self.agent.node_info):
                    reg_service = self.agent.topology_manager.get_service(service["service_id"])
                    self.fill_service(service, reg_service)
                if 'dependencies' in service.keys() and "dependencies_done" not in service.keys():
                    print("Tiene dependencias")
                    Thread(target=self.attend_service_dependencies, args=(service, )).start()
                else:
                    print("No tiene dependencias")
                    if self.can_execute_service(service, self.agent.node_info):
                        print("Puedo ejecutar {}".format(service.items()))
                        result = self.agent.runtime.execute_service(service)
                        self.agent.services_results.append(result)
                    elif(self.agent.node_info["role"] != "agent"):
                        print("Delego el servicio a un agent {}".format(service.items()))
                        th_attend_service = Thread(target=self.attend_service, args=(service, ))
                        th_attend_service.start()
                        self.th_attend_services.append(th_attend_service)
                    else:
                        self.agent.send_dict(service)




    def attend_service_dependencies(self, service):
        dependencies = []
        for dependency in service["dependencies"]:
            dependencies.append(self.add_service(dependency))
        for dependency in dependencies:
            while True:
                if dependency not in self.agent.generated_services_id:
                    break
        service["dependencies_done"] = True
        self.agent.services.append(service)



    def add_service(self, service_id):
        reg_service = self.agent.topology_manager.get_service(service_id)
        random_id = self.agent.generate_service_id()
        reg_service["type"] = "service"
        reg_service["id"] = random_id
        reg_service["service_id"] = reg_service["_id"]
        reg_service["agent_id"] = self.agent.node_info["nodeID"]
        self.agent.generated_services_id.append(random_id)
        self.agent.services.append(reg_service)
        return random_id


    def attend_service(self, service):
        agents = self.agent.topology_manager.get_my_agents(self.agent.node_info["zone"])
        attended = False
        if(agents):
            for agent in agents:
                if(self.can_execute_service(service, agent)):
                    self.agent.send_dict_to(service, agent["nodeID"])
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
        print()
        print(service.get("IoT"))
        print(node_info.get("IoT"))
        print()
        try:
            return set(service["IoT"]).issubset(set(node_info["IoT"]))
        except:
            return False

    def process_results(self):
        while True:
            if len(self.agent.services_results) > 0:
                service_result = self.agent.services_results.pop(0)
                if service_result["id"] in self.agent.generated_services_id:
                    self.agent.my_services_results.append(service_result)
                    # print(self.agent.generated_services_id)
                    origin = self.service_ids.get(service_result["id"])
                    if origin and origin["origin_id"] in self.agent.generated_services_id:
                        self.agent.generated_services_id.remove(origin["origin_id"])
                    self.agent.generated_services_id.remove(service_result["id"])
                    # print("He removido ", service_result["id"])
                    # print(self.agent.generated_services_id)
                else:
                    if self.agent.node_info["role"] != "agent":
                        id = service_result["id"]
                        agent_id = self.service_ids[id]["agent_id"]
                        service_result["id"] = self.service_ids[id]["origin_id"]
                        print("Respondo: ", service_result)
                        self.agent.send_dict_to(service_result, agent_id)
                    else:
                        self.agent.send_dict(service_result)


    def fill_service(self, service, reg_service):
        random_id = self.agent.generate_service_id()
        service["origin_id"] = service["id"]
        service["id"] = random_id
        self.service_ids[random_id] = {
            "origin_id": service["origin_id"],
            "agent_id": service["agent_id"]
        }
        self.agent.generated_services_id.append(random_id)
        for key in reg_service.keys():
            if not key in service.keys():
                service[key] = reg_service[key]
