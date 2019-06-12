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
        self.get_code(code, service["params"])
        self.get_dependencies_codes(service.get("dependencies_codes"))
        if not service["is_infinite"]:
            output = self.execute_code(service["python_version"], code, params)
            if self.check_error(output):
                result = self.get_result(service["id"], output, "error")
                if "ip" in service.keys():
                    self.agent.API.send_result(result, service["ip"])
                else:
                    self.agent.API.send_result(result, self.agent.node_info["myIP"])
            else:
                result = self.get_result(service["id"], output, "success")
                if "ip" in service.keys():
                    self.agent.API.send_result(result, service["ip"])
                else:
                    self.agent.API.send_result(result, self.agent.node_info["myIP"])
        elif service["_id"] not in self.infinite_services:
            port = self.port
            self.infinite_services[service["_id"]] = {
                "ip": self.agent.node_info["myIP"],
                "port": port
            }
            params = self.add_socket_params(params)
            Thread(target=self.execute_code, args=(service["python_version"], code, params)).start()
            output = json.dumps({
                "socket_ip": self.agent.node_info["myIP"],
                "socket_port": port
            })
            time.sleep(2)
            result = self.get_result(service["id"], output, "success")
            self.agent.API.send_result(result, service["ip"])
        else:
            ip = self.infinite_services[service["_id"]]["ip"]
            port = self.infinite_services[service["_id"]]["port"]
            output = json.dumps({
                "socket_ip": self.agent.node_info["myIP"],
                "socket_port": port
            })
            result = self.get_result(service["id"], output, "success")
            self.agent.API.send_result(result, service["ip"])

    def add_socket_params(self, params):
        params += "ip=" + self.agent.node_info["myIP"] + " port=" + str(self.port)
        self.port += 2
        return params

    def get_result(self, service_id, output, status):
        return {
            "type": "service_result",
            "id": service_id,
            "status": status,
            "output": output
        }

    def check_error(self, output):
        try:
            error = output.split(":")[0]
            return error == "ERROR"
        except:
            return False

    def get_code(self, code, params):
        if not self.has_service_code(code):
            self.get_remote_file(code, params)

    def get_dependencies_codes(self, codes):
        if codes:
            for code in codes.split(" "):
                self.get_code(code)

    def prepare_params(self, service):
        params = service.get("params")
        print("PARAMS:", params)
        result = ""
        if params:
            for key, value in params.items():
                if value and value != "":
                    result += key + "=" + str(value) + " "
        return result

    def execute_code(self, python_version, code, params):
        print("Voy a ejecutar:\n{}\n{}\n{}".format(python_version, code, params))
        if params:
            print("HAY PARAMS")
            output = subprocess.getoutput(python_version + " ./codes/" + code + " " + params)
            # dentro del code.py que se ejecuta para obtener params: params = sys.argv[1].split(" ")
        else:
            print("NO HAY PARAMS")
            output = subprocess.getoutput(python_version + " ./codes/" + code)
        return output

    def get_remote_file(self, code, params):
        file = open("./codes/" + code, 'wb')
        content = requests.get("http://{}:{}/download/{}".format(params["host_frontend"], params["port_frontend"], code)).content
        file.write(content)
        file.close()

    def has_service_code(self, code):
        return os.path.isfile("./codes/" + code)
