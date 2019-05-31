from agent import Agent
import psutil
import subprocess

node_id = {
	#"ipDB" : "192.168.1.34",
	"ipDB" : "10.0.2.16",
	"portDB" : 8000,
	"device" : "Leader A",
	"role" : "leader",
	"myIP" : subprocess.getoutput("hostname -I"),
	"leaderIP" : '10.2.3.5',
	"port" : 5000,
	"IoT" : ["-", "-"],
	"broadcastIP" : subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'"),
	"cpu" : psutil.cpu_percent(),
	"ram" : psutil.virtual_memory()[2],
	"status" : 1,
	"zone": "A"
}

try:
	leader = Agent(node_id)
except KeyboardInterrupt:
	del leader
