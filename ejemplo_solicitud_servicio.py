import requests
import sys


agent_ip = sys.argv[1]
end_position = sys.argv[2]

service = {
  "service_id": "FOLLOW_ROUTE",
  "agent_ip": agent_ip,
  "params": {
    "Final": end_position
  }
}

result = requests.post("http://{}:8000/request_service".format(agent_ip), json=service)

print("Resultado de la ejecucion del servicio:\n{}".format(result.json()))
