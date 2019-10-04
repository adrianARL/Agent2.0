import json
import os.path
from agent.agent import Agent
from agent.leader import Leader


if os.path.exists("/etc/agent/device.conf"):
	config = open("/etc/agent/device.conf", "r")
	node_info = json.load(config)

	if node_info["role"] == "agent":
		agent = Agent(node_info)
	elif node_info["role"] == "leader" or node_info["role"] == "cloud_agent":
		leader = Leader(node_info)

	while True:
		pass
