from socketIO_client_nexus import SocketIO, LoggingNamespace
import time


class FrontendConnection:
	
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = SocketIO(host, port, wait_for_connection=False)
		#self.receiveStatus()
	
	def on_posicion_response(self, *args):
		# print('Posicion enviada al frontend:', args[0], args[1])
		pass


	def on_send_status_response(self, *args):
		# print('Estado enviado al frontend:', args[0], args[1])
		pass


	def on_reconocimiento_response(self, response):
	    if response == "ok":
	        # print('Reconocimiento ok')
	        pass
	    else:
	        # print("El servidor no te reconoce")
	        exit()

	def on_change_attributtes_response(self, *args):
		# print('Cambiados atributos:', args[0], args[1])
		pass


	def send(self, topic, data, callback):
	    self.socket.emit(topic, data, callback);


	def recognizeAgent(self, agent_info):
		self.send("agent/recognition", agent_info, self.on_reconocimiento_response)


	def repositionAgent(self, agent_id, posicion):
		self.send("agent/position", {
            	"position" : posicion,
                "agent_id" : agent_id
			},
			self.on_posicion_response
		)


	def sendStatus(self, agent_id, status):
		self.send("agent/status", {
            	"status" : status,
                "agent_id" : agent_id
			}, 
			self.on_send_status_response
		)


	def changeAttributtes(self, agent_id, attributtes):
		self.send("agent/attributes", {
				"agent_id" : agent_id,
				"attributes" : attributtes
			},
			self.on_change_attributtes_response
		)


	def wait(self, segs):
		self.socket.wait(segs)