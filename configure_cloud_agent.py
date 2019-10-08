import json
import subprocess
import psutil

my_ip = subprocess.getoutput("hostname -I | awk '{print $1}'")
broadcast_ip = subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'").split('\n')[0]

node_info = {
    "ipDB": my_ip,
    "portDB": 27017,
    "myIP": my_ip,
    "leaderIP": "",
    "port": 5000,
    "broadcastIP": broadcast_ip,
    "cpu": psutil.cpu_percent(),
    "ram": psutil.virtual_memory()[2],
    "status": 1,
    "device": "cloud",
    "role": "cloud_agent",
    "IoT": [],
    "nodeID": "0000000000"
}

file = open("device.conf", "w")
json.dump(node_info, file)
file.close()
