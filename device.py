import requests
import os.path
import os
import subprocess
import json
import psutil
import ast
from pick import pick


leader_ip = None
my_ip = subprocess.getoutput("hostname -I | awk '{print $1}'")
node_info = {}
available_iots = ["mapa", "motor", "wheels", "rfid_sensor", "line_sensor", "ultrasonic_sensor", "semaforo", "farola", "siren"]
default_configs = {
        "ambulancia": ["motor", "wheels", "rfid_sensor", "line_sensor", "ultrasonic_sensor", "siren"],
        "camion_basura": ["motor", "wheels", "rfid_sensor", "line_sensor", "ultrasonic_sensor"],
        "gestor_semaforos": ["semaforo"],
        "gestor_farolas": ["farola"]
}

def prRed(skk): print("Estado: \033[91m{}\033[00m" .format(skk))

def prGreen(skk): print("Estado: \033[92m{}\033[00m" .format(skk)) 

def register_to_leader():
        global leader_ip, node_info, default_configs
        devices_list = ["{}:{}".format(device, default_configs[device]) for device in default_configs.keys()]
        if not os.path.exists("./config/device.conf"):
                leader_ip = input("Leader IP: ")
                node_info = {
                        "ipDB" : "10.0.2.16",
                        "portDB" : 27017,
                        "myIP" : my_ip,
                        "leaderIP" : leader_ip,
                        "port" : 5000,
                        "broadcastIP" : subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'").split('\n')[0],
                        "cpu" : psutil.cpu_percent(),
                        "ram" : psutil.virtual_memory()[2],
                        "status" : 1
                }
                attributes = ["device", "role", "IoT"]
                device, index = pick(devices_list, "Selecciona que tipo de dispositivo sera el agent", indicator="=>")
                device = device.split(":")[0]
                node_info["device"] = device
                node_info["IoT"] = default_configs[device]
                role, index = pick(["agent", "leader"], "Selecciona que rol tendra el agent en la topologia", indicator="=>")
                node_info["role"] = role
                try:
                        if node_info["role"] != "cloud_agent":
                                node_id = requests.post("http://{}:8000/register_agent".format(leader_ip), json=node_info)
                                node_info["nodeID"] = node_id.text.zfill(10)
                        config = open("./config/device.conf", "w")
                        json.dump(node_info, config)
                        config.close()
                except:
                        print("ERROR: No se ha podido conectar con el leader {}. Intentalo mas tarde.".format(leader_ip))
        else:
                config = open("./config/device.conf", "r")
                node_info = json.load(config)
                leader_ip = node_info.get("leader_ip")
                config.close()
        start_agent()

def start_agent():
        try:
                requests.get("http://{}:8000/alive".format(my_ip))
        except:
                subprocess.call("python3 start_agent.py &", shell=True)

def filter_services(services):
        global node_info
        iots = node_info["IoT"]
        result = []
        for service in services:
                if all(elem in iots for elem in service["IoT"]):
                        result.append(service)
        return result

def convert_to_list(services):
        count = 0
        services_list = []
        current_service = ""
        services = services[1:-1]
        for char in services:
                if char == "{":
                        count += 1
                elif char == "}":
                        count -= 1
                if count != 0 or char == "}":
                        current_service += char
                if count == 0 and len(current_service) > 0:
                        current_service = ast.literal_eval(current_service)
                        services_list.append(current_service)
                        current_service = ""
        return services_list

def get_services():
        global node_info
        if node_info["role"] == "agent":
                services = requests.get("http://{}:8000/service".format(leader_ip)).text
        else:
                try:
                        services = requests.get("http://{}:8000/service".format(my_ip)).text
                except:
                        get_services()
        services = convert_to_list(services)
        services = filter_services(services)
        return services

def request_service(service):
        result = requests.post("http://{}:8000/request_service".format(my_ip), json=service).text
        result = json.loads(result)
        return result

def find_service(services, service_id):
        for service in services:
                if service["_id"] == service_id:
                        return service

def show_default_configs():
        global default_configs
        print("\nConfiguraciones predeterminadas:")
        for config, iots in default_configs.items():
                print("\t- {}: {}".format(config, iots))
        option = input("\nQuieres seleccionar una configuracion predeterminada? s/n: ")
        if option == "s":
                config = input("\nQue configuracion quieres cargar?: ")
                return config, default_configs[config]
        return None, []
                
def show_available_iots():
        global available_iots
        print("IoT's disponibles:")
        for iot in available_iots:
                print("\t- {}".format(iot))
                
def show_result(result, service_id):
        os.system("clear")
        print("RESULTADO DEL SERVICIO {}:\n".format(service_id))
        if result["status"] == "success":
                prGreen("{}".format(result["status"]))
        else:
                prRed("{}".format(result["status"]))
        try:
                output = json.loads(result["output"])
                for key, value in output.items():
                        print("{}: {}".format(key, value))
        except:
                pass

def generate_service_list(services):
        services_list = []
        for service in services:
                services_list.append("{}:{}".format(service["_id_"], service["description"]))

        return services_list

def main():
        register_to_leader()
        services = get_services()
        services_list = generate_service_list(services)
        services_list.append("EXIT")
        os.system("clear")
        while True:
                title = "Elige un servicio a solicitar:"
                service_id, index = pick(services_list, title, indicator="=>")
                request = {}
                if service_id != "EXIT":
                        service_id = service_id.split(':')[1]
                        service = find_service(services, service_id)
                        request["service_id"] = service_id
                        request["params"] = {}
                        if service.get("params"):
                                os.system("clear")
                                print("Introduce los parametros del servicio: ")
                                params = service["params"]
                                request["params"] = params
                                for param in params:
                                        value = input("\t{}: ".format(param))
                                        request["params"][param] = value
                                input("\nPulsa ENTER para solicitar el servicio {}".format(service_id))
                        request["agent_ip"] = my_ip
                        result = request_service(request)
                        show_result(result, service_id)
                        input("\nPresiona ENTER para solicitar otro servicio")
                        os.system("clear")
                else:
                        os.system("clear")
                        print("Has salido del programa")
                        break


if __name__ == '__main__':
        main()
