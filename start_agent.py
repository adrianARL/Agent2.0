import json
import os.path
from agent import Agent


if os.path.exists("agent.config"):
	config = open("agent.config", "r")
	content = json.load(config)
	node_info = content["node_info"]
	
	agent = Agent(node_info)
	while True:
		pass