import os
import commands
from ftplib import FTP


class RunTime:

    FTP_SERVER = '10.1.136.179'

    def __init__(self, agent):
        self.agent = agent

    def execute_service(self, service):
        code = service["code"]
        params = service.get("params")
        try:
            if not self.has_service_code(code):
                self.get_remote_file(code)
                output = commands.getoutput("python " + code)
                status = "success"
        except:
            status = "error"
            output = ""
        finally:
            result = {
                "id": service["id"],
                "status": status,
                "output": output
            }
        return result

    def get_remote_file(self, code):
        file = open("./RT/codes/" + code, 'wb')
        ftp = FTP(self.FTP_SERVER)
        ftp.login()
        ftp.cwd('files')
        ftp.retrbinary('RETR ' + code, file.write, 1024)
        file.close()

    def has_service_code(self, code):
        return os.path.isfile("./RT/codes/" + code)
