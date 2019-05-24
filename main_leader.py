from leader import Leader
import psutil
import subprocess

node_id = {
	"ipDB" : "192.168.1.34",
	# "ipDB" : "10.0.2.16",
	"portDB" : 8000,
	"device" : "Leader A",
	"role" : "leader",
	"myIP" : subprocess.getoutput("hostname -I"),
	"leaderIP" : None,
	"port" : 5000,
	"IOT" : None,
	"broadcastIP" : subprocess.getoutput("ip a | grep inet | grep brd | awk '{print $4}'"),
	"cpu" : psutil.cpu_percent(),
	"ram" : psutil.virtual_memory()[2],
	"status" : 1,
	"zone": "A"
}

leader = Leader(node_id)
