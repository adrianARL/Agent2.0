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

def register_to_leader():
	global leader_ip, node_info
	if not os.path.exists("./config/device.config"):
		leader_ip = input("Leader IP: ")
		content = {}
		content["leader_ip"] = leader_ip
		node_info = {
	        "ipDB" : "10.0.2.16",
	        "portDB" : 8080,
	        "device" : "Agent",
	        "role" : "agent",
	        "myIP" : my_ip,
	        "leaderIP" : leader_ip,
	        "port" : 5000,
	        "broadcastIP" : subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'").split('\n')[0],
	        "cpu" : psutil.cpu_percent(),
	        "ram" : psutil.virtual_memory()[2],
	        "status" : 1
		}
		attributes = ["device", "role", "IoT"]
		for attribute in attributes:
			if attribute == "IoT":
				iots = []
				print("IoT's:")
				iot = input("\tNuevo IoT: ")
				while iot != "-":
					iots.append(iot)
					iot = input("\tNuevo IoT: ")
				node_info["IoT"] = iots
			else:
				value = input("{}: ".format(attribute))
				node_info[attribute] = value
		try:	
			node_id = requests.post("http://{}:8000/register_agent".format(leader_ip), json=node_info)
			node_info["nodeID"] = node_id.text.zfill(10)
			content["node_info"] = node_info
			config = open("./config/device.config", "w")
			json.dump(content, config)
			config.close()
		except:
			print("ERROR: No se ha podido conectar con el leader {}. Intentalo mas tarde.".format(leader_ip))
	else:
		config = open("./config/device.config", "r")
		content = json.load(config)
		leader_ip = content["leader_ip"]
		node_info = content["node_info"]
	# subprocess.call("python3 start_agent.py &", shell=True)

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
	services = requests.get("http://{}:8000/service".format(leader_ip)).text
	services = convert_to_list(services)
	services = filter_services(services)
	print(services)
	return services	

def request_service(service):
	requests.post("http://{}:8000/request_service".format(my_ip), json=service)

def main():
	register_to_leader()
	get_services()
	# os.system("clear")
	# services = {"Servicio 1": {"params": ["parametro1", "parametro2"]}, "Servicio 2": "", "Servicio 3":"", "Servicio 4":"", "Exit":""}
	# services_list = [service for service in services.keys()]
	# while True:
	# 	title = "Elige un servicio a solicitar:"
	# 	service, index = pick(services_list, title, indicator="=>")
	# 	print("Has seleccionado: {}".format(service))
	# 	request = {}
	# 	if service != "Exit":
	# 		request["service_id"] = service
	# 		request["params"] = {}
	# 		params = services[service]["params"]
	# 		for param in params:
	# 			value = input("{}: ".format(param))
	# 			request["params"][param] = value
	# 		input("Pulsa ENTER para solicitar el servicio {}".format(service))
	# 		request_service(request)
	# 	else:
	# 		os.system("clear")
	# 		print("Has salido del programa")
	# 		break


if __name__ == '__main__':
	main()