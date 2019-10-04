import os
import json
import subprocess
import time
import requests
from threading import Thread


class RunTime:

    def __init__(self, agent):
        self.agent = agent
        self.port = 5000
        self.infinite_services = {}

    def execute_service(self, service):
        code = service["code"]
        params = self.prepare_params(service)
        self.get_code(code, service)
        self.get_dependencies_codes(service.get("dependencies_codes"), service)
        result = {
            "type": "service_result",
            "status": "unattended",
        }
        if not service["is_infinite"]:
            output = self.execute_code(service["python_version"], code, params)
            if self.check_error(output):
                result = self.get_result(output, "error")
            else:
                result = self.get_result(output, "success")
        elif service["service_id"] not in self.infinite_services:
            port = self.port
            self.infinite_services[service["service_id"]] = {
                "ip": self.agent.node_info["myIP"],
                "port": port
            }
            params = self.add_socket_params(params)
            Thread(target=self.execute_code, args=(service["python_version"], code, params)).start()
            socket_ip = service["service_id"]+"_ip"
            socket_port = service["service_id"]+"_port"
            output = json.dumps({
                socket_ip: self.agent.node_info["myIP"],
                socket_port: port
            })
            result = self.get_result(output, "success")
        else:
            port = self.infinite_services[service["service_id"]]["port"]
            socket_ip = service["service_id"]+"_ip"
            socket_port = service["service_id"]+"_port"
            output = json.dumps({
                socket_ip: self.agent.node_info["myIP"],
                socket_port: port
            })
            result = self.get_result(output, "success")
        ##print("HAGO RESULT DE", result)
        return result

    def add_socket_params(self, params):
        params += "ip=" + self.agent.node_info["myIP"] + " port=" + str(self.port)
        self.port += 2
        return params

    def get_result(self, output, status):
        return {
            "type": "service_result",
            "status": status,
            "output": output
        }

    def check_error(self, output):
        try:
            error = output.split(":")[0]
            return error == "ERROR"
        except:
            return False

    def get_code(self, code, service):
        if not self.has_service_code(code):
            self.get_remote_file(code, service)

    def get_dependencies_codes(self, codes, service):
        if codes:
            for code in codes.split(" "):
                self.get_code(code, service)

    def prepare_params(self, service):
        params = service.get("params")
        ##print("PARAMS:", params)
        result = ""
        result += "download_host=" + service["download_host"] + " "
        result += "download_port=" + str(service["download_port"]) + " "
        result += "agent_id=" + self.agent.node_info["nodeID"] + " "
        if params:
            for key, value in params.items():
                if value:
                    if(type(value) is dict):
                        result += key + "='" + json.dumps(value) + "' "
                    elif(type(value) is list):
                        result += key + "="
                        for item in value:
                            result+=item+"@"
                        result += " "
                    elif value != "":
                        result += key + "=" + str(value) + " "
        return result

    def execute_code(self, python_version, code, params):
        print("Voy a ejecutar:\n{}\n{}\n{}".format(python_version, code, params))
        if params:
            ##print("HAY PARAMS")
            output = subprocess.getoutput(python_version + " ./codes/" + code + " " + params)
            # dentro del code.py que se ejecuta para obtener params: params = sys.argv[1].split(" ")
        else:
            ##print("NO HAY PARAMS")
            output = subprocess.getoutput(python_version + " ./codes/" + code)
        return output

    def get_remote_file(self, code, service):
        file = open("./codes/" + code, 'wb')
        content = requests.get("http://{}:{}/download/{}".format(service["download_host"], service["download_port"], code)).content
        file.write(content)
        file.close()

    def has_service_code(self, code):
        return os.path.isfile("./codes/" + code)
