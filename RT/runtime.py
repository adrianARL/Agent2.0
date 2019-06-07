import os
import subprocess
from threading import Thread
from ftplib import FTP


class RunTime:

    FTP_SERVER = '10.1.136.179'
    # FTP_SERVER = '192.168.1.37'

    def __init__(self, agent):
        self.agent = agent
        self.port = 5000

    def execute_service(self, service):
        code = service["code"]
        params = self.prepare_params(service)
        self.get_code(code)
        self.get_dependencies_codes(service.get("dependencies_codes"))
        if not service["is_infinite"]:
            output = self.execute_code(code, params)
            if self.check_error(output):
                result = self.get_result(service["id"], output, "error")
                if "origin_ip" in service.keys():
                    self.agent.API.send_result(result, service["origin_ip"])
                else:
                    self.agent.API.send_result(result, self.agent.node_info["myIP"])
            else:
                result = self.get_result(service["id"], output, "success")
                if "origin_ip" in service.keys():
                    self.agent.API.send_result(result, service["origin_ip"])
                else:
                    self.agent.API.send_result(result, self.agent.node_info["myIP"])
        else:
            port = self.port
            params = self.add_params(params)
            Thread(target=self.execute_code, args=(code, params)).start()
            output = "ip={} port={}".format(self.agent.node_info["myIP"], port)
            result = self.get_result(service["id"], output, "success")
            self.agent.API.send_result(result, service["origin_ip"])

    def add_params(self, params):
        params += "ip=" + self.agent.node_info["myIP"] + " port=" + self.port
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

    def get_code(self, code):
        if not self.has_service_code(code):
            print("Voy a descargar de FTP")
            self.get_remote_file(code)
            print("Ya he descargado")

    def get_dependencies_codes(self, codes):
        if codes:
            for code in codes.split(" "):
                self.get_code(code)

    def prepare_params(self, service):
        params = service.get("params")
        result = ""
        if params:
            for key, value in params.items():
                if value and value != "":
                    result += key + "=" + str(value) + " "
        return result

    def execute_code(self, code, params):
        if params:
            output = subprocess.getoutput("python ./codes/" + code + " " + params)
            # dentro del code.py que se ejecuta para obtener params: params = sys.argv[1].split(" ")
        else:
            output = subprocess.getoutput("python ./codes/" + code)
        return output

    def get_remote_file(self, code):
        file = open("./codes/" + code, 'wb')
        ftp = FTP(self.FTP_SERVER)
        ftp.login()
        ftp.cwd('files')
        ftp.retrbinary('RETR ' + code, file.write, 1024)
        file.close()

    def has_service_code(self, code):
        return os.path.isfile("./codes/" + code)
