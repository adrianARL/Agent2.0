from agent import Agent
import psutil
import subprocess

node_id = {
	#"ipDB" : "192.168.1.34",
	"ipDB" : "10.0.2.16",
	"portDB" : 8000,
	"device" : "Leader A",
	"role" : "leader",
	"myIP" : subprocess.getoutput("hostname -I | awk '{print $1}'"),
	"leaderIP" : '10.10.176.123',
	"port" : 5000,
	"IoT" : ["-", "semaforo"],
	"broadcastIP" : subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'"),
	"cpu" : psutil.cpu_percent(),
	"ram" : psutil.virtual_memory()[2],
	"status" : 1,
	"zone": "A"
}


leader = Agent(node_id)
