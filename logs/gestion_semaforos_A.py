import time
import sys
import json
import socket
import sqlite3
import errno
import serial
from threading import Thread
from util import get_params
from frontend_connection import FrontendConnection


TRAFFIC_LIGHT_REQUEST = "traffic_light_request"
CARD_ID_REQUEST = "card_id_request"
NESTED_LEADERS_REQUEST = "nested_leaders_request"
EMERGENCY_DICT_REQUEST = "emergency_dict_request"
REQUEST_TRAFFIC_LIGHT_STATUS = "requestTrafficLightStatus"
SET_TRAFFIC_LIGHT_COLOR = "setTrafficLightColor"
RESPONSE_TRAFFIC_LIGHT_COLOR = "responseTrafficLightColor"

traffic_light_color = {
    "1000" : "green",
    "0100" : "yellow",
    "0010" : "red"
}
color_traffic_light = {
    "green" : "1000",
    "yellow" : "0100",
    "red" : "0010"
}
# Propiedades y caracteristicas de los agentes que representa este script
tw1 = {
    "id" : "TW1",
    "type" : "trafficlight",
    "positioning" : "rfid",
    "x" : 139,
    "y" : 480,
    "direction" : "left",
    "orientation" : "v",
    "status" : "green",
    "description" : "Semaforo",
    "attributtes" : {
        "role" : "agent",
        "leader" : "TW2",
        "resources" : {
            "CPU" : "1,5GHz",
            "Chipset" : "DDR4",
            "DISK" : 5
        },
        "iots" : {}
    }
}

tw2 = {
    "id" : "TW2",
    "type" : "trafficlight",
    "positioning" : "rfid",
    "x" : 261,
    "y" : 447,
    "long" : 60/2,
    "direction" : "left",
    "orientation" : "h",
    "status" : "red",
    "description" : "Semaforo",
    "attributtes" : {
        "role" : "leader",
        "leader" : "",
        "resources" : {
            "CPU" : "1,5GHz",
            "Chipset" : "DDR4",
            "DISK" : 5
        },
        "iots" : {}
    }
}

ts1 = {
    "id" : "TS1",
    "type" : "trafficlight",
    "positioning" : "rfid",
    "x" : 591,
    "y" : 817,
    "direction" : "right",
    "orientation" : "h",
    "status" : "red",
    "description" : "Semaforo",
    "attributtes" : {
        "role" : "agent",
        "leader" : "TW2",
        "resources" : {
            "CPU" : "1,5GHz",
            "Chipset" : "DDR4",
            "DISK" : 500
        },
        "iots" : {}
    }
}

ts2 = {
    "id" : "TS2",
    "type" : "trafficlight",
    "positioning" : "rfid",
    "x" : 741,
    "y" : 700,
    "direction" : "left",
    "orientation" : "h",
    "status" : "red",
    "description" : "Semaforo",
    "attributtes" : {
        "role" : "agent",
        "leader" : "TW2",
        "resources" : {
            "CPU" : "1,5GHz",
            "Chipset" : "DDR4",
            "DISK" : 500
        },
        "iots" : {}
    }
}

def read_arduino_traffic_light_status(arduino, _):
    while True:
        try:
            lectura = arduino.readline().decode().rstrip()
            traffic_light, status= lectura.split('-')
            traffic_light_status[traffic_light] = traffic_light_color[status]
            if frontend:
                frontend.sendStatus(traffic_light, status)
        except:
            pass

def read_traffic_light_status():
    for arduino in arduinos:
        thread = Thread(target=read_arduino_traffic_light_status, args=(arduino, None))
        thread.start()

def bind_connection():
        my_socket.bind((ip, port))
        my_socket.listen(50)

def accept_connection():
        while True:
            agent_connection, addr = my_socket.accept()
            print("Se ha conectado el agent con addr ", addr)
            agent_connection.setblocking(0)
            agents.append(agent_connection)


def receive_request():
    while True:
        for agent in agents:
            try:
                msg = agent.recv(4096).decode()
                if(msg != None and msg != ""):
                    print(msg)
                    info = ""
                    if msg == TRAFFIC_LIGHT_REQUEST:
                        info = json.dumps(traffic_light_dict, ensure_ascii=False)
                    elif msg == NESTED_LEADERS_REQUEST:
                        info = json.dumps(nested_leaders, ensure_ascii=False)
                    elif msg == EMERGENCY_DICT_REQUEST:
                        info = json.dumps(emergency_dict, ensure_ascii=False)
                    elif msg == CARD_ID_REQUEST:
                        info = json.dumps(card_id_dict, ensure_ascii=False)
                    elif msg.split("_")[0] == REQUEST_TRAFFIC_LIGHT_STATUS:
                        traffic_light = msg.split("_")[1]
                        info = RESPONSE_TRAFFIC_LIGHT_COLOR+"_"+traffic_light_status[traffic_light]
                    elif msg.split('_')[0] == SET_TRAFFIC_LIGHT_COLOR:
                        trafficlight_id = msg.split('_')[1]
                        color = msg.split('_')[2]
                        data = {
                            'agente_id': trafficlight_id,
                            'status': color_traffic_light[color]
                        }
                        on_receive_status(data)
                    if info != "":
                        print(info)
                        agent.send(info.encode())
            except IOError as e:
                if(e.errno == errno.EWOULDBLOCK):
                    pass


def load_traffic_lights():
    conn = sqlite3.connect('map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from traffic_lights").fetchall()
    trafficlights = {}
    for light in data:
        trafficlights[light[0]] = light[1]
    return trafficlights

def load_nested_leaders():
    conn = sqlite3.connect('map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from nested_leaders").fetchall()
    nested_leaders = {}
    for leader in data:
        nested_leaders[leader[0]] = (leader[1].split(',')[0], leader[1].split(',')[1])
    return nested_leaders

def load_emergency_dict():
    conn = sqlite3.connect('map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from emergency_rfids").fetchall()
    emergency_dict = {}
    for emergency in data:
        emergency_dict[emergency[0]] = emergency[1]
    return emergency_dict

def load_card_ids():
    conn = sqlite3.connect('map.db')
    cursor = conn.cursor()
    data = cursor.execute("select * from card_id").fetchall()
    card_ids = {}
    for card_id in data:
        card_ids[card_id[1]] = card_id[0]
    return card_ids

def on_receive_status(*args):
        data = args[0]
        print(args)
        print("Recibido cambio de estado para: "+data["agente_id"]+". Estado: "+data["status"])
        if data["agente_id"] == "TW1":
            code = '1'+data["status"]
            arduinos[0].write(code.encode())
        if data["agente_id"] == "TW2":
            code = '2'+data["status"]
            arduinos[0].write(code.encode())
        if data["agente_id"] == "TS1":
            code = '1'+data["status"]
            arduinos[1].write(code.encode())
        if data["agente_id"] == "TS2":
            code = '2'+data["status"]
            arduinos[1].write(code.encode())
        frontend.sendStatus(data["agente_id"], data["status"])

def receive_frontend_request():
    if frontend:
       frontend.socket.on("front/agent/status", on_receive_status)
    while True:
        frontend.wait(1)

if __name__ == "__main__":
    try:
        params = get_params(sys.argv)
        host_frontend = params.get("host_frontend")
        port_frontend = params.get("port_frontend")
        ip = params.get("ip")
        port = int(params.get("port"))
        # load from db
        traffic_light_dict = load_traffic_lights()
        card_id_dict = load_card_ids()
        nested_leaders = load_nested_leaders()
        emergency_dict = load_emergency_dict()

        agents = []
        arduinos = [serial.Serial('/dev/ttyACM0', 9600), serial.Serial('/dev/ttyACM1', 9600)]
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_connection()
        Thread(target=accept_connection).start()
        Thread(target=receive_request).start()
        frontend = FrontendConnection(host_frontend, port_frontend) # Conexion con Frontend
        if frontend:
            Thread(target=receive_frontend_request).start()
        traffic_light_status = {}
        semaforos = ["TW1", "TW2", "TS1", "TS2"]
        frontend.recognizeAgent(tw1)
        frontend.recognizeAgent(tw2)
        frontend.recognizeAgent(ts1)
        frontend.recognizeAgent(ts2)
        read_traffic_light_status()

    except Exception as e:
        print("ERROR:{}".format(e))
