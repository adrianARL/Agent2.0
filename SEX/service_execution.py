import time
import uuid
from threading import Thread
# from frontend_connection import FrontendConnection


class ServiceExecution:

    def __init__(self, agent):
        self.agent = agent
        self.th_attend_services = []
        self.service_ids = {}
        Thread(target=self.process_results).start()

    def request_service(self, service):
        if self.agent.node_info["role"] == "agent":
            self.fill_service(service)
            self.agent.API.request_service_to_leader(service)
        else:
            reg_service = self.agent.API.get_service(service)
            self.fill_service(service, reg_service)
            if "dependencies" not in service.keys():
                if self.requester_can_execute(service):
                    self.agent.API.delegate_service(service, service["origin_ip"])
                elif self.can_execute_service(service, self.agent.node_info):
                    self.agent.API.delegate_service(service, self.agent.node_info["myIP"])
                else:
                    agent_ip = self.find_agent_to_execute(service)
                    if agent_ip:
                        self.agent.API.delegate_service(service, agent_ip)
                    else:
                        unattended_result = {
                            "type": "service_result",
                            "id": service["origin_id"],
                            "status": "unattended",
                            "output": ""
                        }
                        self.agent.API.send_result(agent_ip, unattended_result)

    def requester_can_execute(self, service):
        if "origin_ip" in service:
            agent_info = self.agent.API.get_agents({"myIP": service["origin_ip"]})
            if len(agent_info) > 0:
                agent_info = agent_info[0]
            return self.can_execute_service(service, agent_info)
        else:
            return False



    def find_agent_to_execute(self, service):
        agents = self.agent.API.get_agents({"leaderID" : self.agent.node_info["nodeID"]})
        print(agents)
        if(agents):
            for agent in agents:
                if(self.can_execute_service(service, agent)):
                    return  agent["myIP"]
        return None




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
        self.agent.generated_services_id.append(randrequesom_id)
        self.agent.services.append(reg_service)
        return random_id




    def can_execute_service(self, service, node_info):
        try:
            print()
            print(service)
            print(node_info)
            print()
            return set(service["IoT"]).issubset(set(node_info["IoT"]))
        except:
            return False

    def process_results(self):
        while True:
            if len(self.agent.services_results) > 0:
                service_result = self.agent.services_results.pop(0)
                origin = self.service_ids.get(service_result["id"])
                if origin:
                    if service_result["id"] in self.agent.generated_services_id:
                        self.agent.generated_services_id.remove(service_result["id"])
                    if origin["origin_id"] in self.agent.generated_services_id:
                        self.agent.generated_services_id.remove(origin["origin_id"])
                    service_result["id"] = origin["origin_id"]
                    if origin["agent_id"] != self.agent.node_info["nodeID"]:
                        if self.agent.node_info["role"] != "agent":
                            agent_id = origin["agent_id"]
                            requesprint("Devuelvo el resultado {} al agent {} ".format(service_result.get("output"), agent_id))
                            self.agent.send_dict_to(service_result, agent_id)
                        else:
                            print("Devuelvo el resultado {} al leader".format(service_result.get("output")))
                            self.agent.send_dict(service_result)
                    else:
                        print("Me quedo con el resultado {}".format(service_result.get("output")))
                        self.agent.my_services_results.append(service_result)



                # if service_result["id"] in self.agent.generated_services_id:
                #     self.agent.my_services_results.append(service_result)
                #     print(self.agent.generated_services_id)
                #     origin = self.service_ids.get(service_result["id"])
                #     if origin and origin["origin_id"] in self.agent.generated_services_id :
                #         self.agent.generated_services_id.remove(origin["origin_id"])
                #     self.agent.generated_services_id.remove(service_result["id"])
                #     print("He removido ", service_result["id"])
                #     print(self.agent.generated_services_id)
                # else:
                #     if self.agent.node_info["role"] != "agent":
                #         id = service_result["id"]
                #         agent_id = self.service_ids[id]["agent_id"]
                #         service_result["id"] = self.service_ids[id]["origin_id"]
                #         print("Respondo: ", service_result)
                #         self.agent.send_dict_to(service_result, agent_id)
                #     else:
                #         self.agent.send_dict(service_result)


    def fill_service(self, service, reg_service={}):
        random_id = str(self.agent.generate_service_id())
        if "id" in service.keys():
            service["origin_id"] = service["id"]
        service["id"] = random_id

        if "ip" in service.keys():
            service["origin_ip"] = service["ip"]
        service["ip"] = self.agent.node_info["myIP"]

        # self.service_ids[random_id] = {
        #     "origin_id": service["origin_id"],
        #     "agent_id": service["agent_id"]
        # }
        self.agent.generated_services_id.append(random_id)
        for key in reg_service.keys():
            if not key in service.keys():
                service[key] = reg_service[key]
