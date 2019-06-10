import subprocess
import psutil
import time
from agent import Agent

node_id = {
	# "ipDB" : "10.0.2.16",
	"ipDB" : "192.168.1.45",
	"portDB" : 8000,
	"device" : "Agent",
	"role" : "agent",
	"myIP" : subprocess.getoutput("hostname -I | awk '{print $1}'"),
	"leaderIP" : '192.168.1.45',
	# "leaderIP" : '10.0.2.16',
	"port" : 5000,
	"IoT" : ["-", "motor", "rfid_sensor", "ultrasonic_sensor", "line_sensor", "virtual"], 
	"broadcastIP" : subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'"),
	"cpu" : psutil.cpu_percent(),
	"ram" : psutil.virtual_memory()[2],
	"status" : 1
}

agent = Agent(node_id)

while True:
	pass
