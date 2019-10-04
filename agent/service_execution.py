import time
import uuid
import json
from threading import Thread


class ServiceExecution:

    UNATTENDED_MESSAGE = {
        "type": "service_result",
        "status": "unattended",
    }

    def __init__(self, agent):
        self.agent = agent
        self.running_dependencies = {}
        self.dependency_of = {}
        self.pending_services = {}

    def request_service(self, service):
        if self.agent.node_info["role"] == "agent":
            self.fill_service(service)
            service["agent_ip"] = self.agent.node_info["myIP"]
            return self.agent.API.request_service_to_leader(service)
        elif self.agent.node_info["role"] == "cloud_agent":
            reg_service = self.agent.API.get_service(service)
            self.fill_service(service, reg_service)
            requester = self.get_service_requester(service)
            if requester and requester["role"] == "agent":
                leader = self.get_active_leader_from_agent(requester)
                if leader and (self.can_execute_service(service, leader) or self.can_execute_service(service, requester)):
                    return self.agent.API.request_service_to_agent(service, leader["myIP"])
                elif service.get("params") and not service.get("params").get("agent_id"):
                    agent_to_delegate = self.find_agent_to_delegate(service)
                    if agent_to_delegate:
                        if agent_to_delegate.get("leaderID") == self.agent.node_info["nodeID"]:
                            return self.agent.API.delegate_service(service, agent_to_delegate["myIP"])
                        elif agent_to_delegate.get("leaderID"):
                            return self.agent.API.request_service_to_agent(service, agent_to_delegate.get("leaderID"))
            elif requester:
                return self.agent.API.request_service_to_agent(service, requester["myIP"])
            return self.UNATTENDED_MESSAGE
        else:
            reg_service = self.agent.API.get_service(service)
            self.fill_service(service, reg_service)
            if "dependencies" in service.keys():
                for dependency in service.get("dependencies"):
                    service_to_request = {"service_id": dependency, "agent_ip": service["agent_ip"]}
                    service_to_request["params"] = service["params"] if "params" in service.keys() else None
                    result_dependency = self.agent.API.request_service_to_me(service_to_request)
                    self.get_params_from_result(service, result_dependency)
            if self.requester_can_execute(service):
                return self.agent.API.delegate_service(service, service["agent_ip"])
            elif self.can_execute_service(service, self.agent.node_info):
                return self.agent.API.delegate_service(service, self.agent.node_info["myIP"])
            else:
                agent_ip = self.find_agent_to_execute(service)
                if agent_ip:
                    return self.agent.API.delegate_service(service, agent_ip)
                else:
                    return self.agent.API.request_service_to_leader(service)


    def get_service_requester(self, service):
        if "agent_ip" in service:
            agent_info = self.agent.API.get_agents({"myIP": service["agent_ip"], "status": 1})
            if len(agent_info) > 0:
                agent_info = agent_info[0]
                return agent_info
        return False

    def get_active_leader_from_agent(self, requester):
        if "leaderIP" in requester:
            agent_info = self.agent.API.get_agents({"myIP": requester["leaderIP"], "status": 1})
            if len(agent_info) > 0:
                agent_info = agent_info[0]
                return agent_info
        return None

    def get_params_from_result(self, service, result):
        if "status" in result.keys() and result["status"] == "success" and "output" in result.keys():
            print("Resultado: ", result)
            print(type(result["output"]))
            try:
                result["output"] = json.loads(result["output"])
                if "params" not in service.keys():
                    service["params"] = result["output"]
                else:
                    for key, value in result["output"].items():
                        service["params"][key] = value
            except:
                print("Me ha petado con el output", result)

    def attend_response(self, service_response):
        if service_response["id"] in self.dependency_of.keys():
            pending_service_id = self.dependency_of[service_response["id"]]
            service_pending = self.pending_services[pending_service_id]
            if service_response["status"] == "success":
                params = json.loads(service_response["output"])
                self.merge_params(service_pending, params)
                del self.dependency_of[service_response["id"]]
                self.running_dependencies[pending_service_id].remove(service_response["id"])
                self.pending_services[pending_service_id]
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
                    pass
                    #print("MENSAJE FINAL = {}".format(service_response))
                del self.pending_services[service_response["id"]]
        elif service_response.get("id") and self.pending_services.get(service_response.get("id")):
            service_pending = self.pending_services[service_response["id"]]
            if "origin_ip" in service_pending.keys():
                self.agent.API.send_result(service_response, service_pending["origin_ip"])
            else:
                pass
                #print("MENSAJE FINAL = {}".format(service_response))
            del self.pending_services[service_response["id"]]
        else:
            pass
            #print("MENSAJE FINAL = {}".format(service_response))



    def merge_params(self, service, params):
        if "params" not in service.keys():
            service["params"] = {}
        for param in params.keys():
            service["params"][param] = params[param]


    def delegate_service(self, service):
        agent_ip = self.find_agent_to_execute(service)
        if agent_ip:
            self.agent.API.delegate_service(service, agent_ip)
        elif service["id"] in self.dependency_of.keys():
            pending_service_id = self.dependency_of[service["id"]]
            service_pending = self.pending_services[pending_service_id]
            dependencies = self.running_dependencies[pending_service_id]
            for dependency in dependencies:
                del self.dependency_of[dependency]
            del self.running_dependencies[pending_service_id]
            unattended_result = {
                "type": "service_result",
                "id": pending_service_id,
                "status": "unattended",
                "output": ""
            }
            if "origin_ip" in service_pending.keys():
                self.agent.API.send_result(unattended_result, service_pending["origin_ip"])
            else:
                self.agent.API.send_result(unattended_result, self.agent.node_info["myIP"])


    def requester_can_execute(self, service):
        if "agent_ip" in service:
            agent_info = self.agent.API.get_agents({"myIP": service["agent_ip"], "status": 1})
            if len(agent_info) > 0:
                agent_info = agent_info[0]
            return self.can_execute_service(service, agent_info)
        else:
            return False

    def find_agent_to_execute(self, service):
        agents = self.agent.API.get_agents({"leaderID" : self.agent.node_info["nodeID"], "status": 1})
        if(agents):
            for agent in agents:
                if(self.can_execute_service(service, agent)):
                    return  agent["myIP"]
        return None

    def find_agent_to_delegate(self, service):
        agents = self.agent.API.get_agents({"status": 1})
        if(agents):
            for agent in agents:
                if(self.can_execute_service(service, agent)):
                    return  agent
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
        for key in reg_service.keys():
            if key not in service.keys() and key != "params":
                service[key] = reg_service[key]
