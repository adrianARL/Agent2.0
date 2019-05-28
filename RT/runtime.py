import os
import subprocess
from threading import Thread
from ftplib import FTP


class RunTime:

    FTP_SERVER = '10.1.136.179'
    # FTP_SERVER = '192.168.1.37'

    def __init__(self, agent):
        self.agent = agent

    def execute_service(self, service):
        print("Execute service")
        code = service["code"]
        params = service.get("params")
        try:
            output = ""
            if not self.has_service_code(code):
                print("Voy a descargar de FTP")
                self.get_remote_file(code)
                print("Ya he descargado")
            if service.get("is_infinite"):
                Thread(target=self.execute_code, args=(code, params)).start()
            else:
                output = self.execute_code(code, params)
            status = "success"
        except Exception as e:
            print(e)
            status = "error"
        finally:
            result = {
                "type": "service_result",
                "id": service["id"],
                "status": status,
                "output": output
            }
        print(result)
        return result

    def execute_code(self, code, params):
        if params:
            output = subprocess.getoutput("python ./codes/" + code + " " + " ".join(params))
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
