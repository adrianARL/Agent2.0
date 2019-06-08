import time
import uuid
import json
from threading import Thread
# from frontend_connection import FrontendConnection


class ServiceExecution:

    def __init__(self, agent):
        self.agent = agent
        self.running_dependencies = {}
        self.dependency_of = {}
        self.pending_services = {}

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
                    self.delegate_service(service)
            else:
                self.running_dependencies[service["id"]] = []
                self.pending_services[service["id"]] = service
                for dependency in service["dependencies"]:
                    service_to_delegate = {'params': service['params']}
                    reg_dependency = self.agent.API.get_service({"service_id": dependency})
                    self.fill_service(service_to_delegate, reg_dependency)
                    self.running_dependencies[service["id"]].append(service_to_delegate["id"])
                    self.dependency_of[service_to_delegate["id"]] = service["id"]
                    if "dependencies" in service_to_delegate.keys():
                        self.agent.API.request_service(service_to_delegate, self.agent.node_info["myIP"])
                    else:
                        if self.can_execute_service(service, self.agent.node_info):
                            self.agent.API.delegate_service(service, self.agent.node_info["myIP"])
                        else:
                            self.delegate_service(service_to_delegate)

    def attend_response(self, service_response):
        if service_response["id"] in self.dependency_of.keys():
            pending_service_id = self.dependency_of[service_response["id"]]
            service_pending = self.pending_services[pending_service_id]
            if service_response["status"] == "success":
                params = json.loads(service_response["output"])
                self.merge_params(service_pending, params)
                del self.dependency_of[service_response["id"]]
                self.running_dependencies[pending_service_id].remove(service_response["id"])
                if not self.running_dependencies[pending_service_id]:
                    if self.requester_can_execute(service_pending):
                        self.agent.API.delegate_service(service_pending, service_pending["origin_ip"])
                    elif self.can_execute_service(service_pending, self.agent.node_info):
                        self.agent.API.delegate_service(service_pending, self.agent.node_info["myIP"])
                    else:
                        self.delegate_service(service_pending)
            elif service_response["status"] == "error":
                dependencies = self.running_dependencies[pending_service_id]
                for dependency in dependencies:
                    del self.dependency_of[dependency]
                del self.running_dependencies[pending_service_id]
                service_response["id"] = pending_service_id
                if "origin_ip" in service_pending.keys():
                    self.agent.API.send_result(service_response, service_pending["origin_ip"])
                else:
                    self.agent.API.send_result(service_response, self.agent.node_info["myIP"])
        else:
            print("MENSAJE FINAL = {}".format(service_response))



    def merge_params(self, service, params):
        if "params" not in service.keys():
            service["params"] = {}
        for param in params.keys():
            service["params"][param] = params[param]

    def delegate_service(self, service):
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
            self.agent.API.send_result(unattended_result, agent_ip)

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
            return set(service["IoT"]).issubset(set(node_info["IoT"]))
        except:
            return False



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
            if key not in service.keys() and key != "params":
                service[key] = reg_service[key]
