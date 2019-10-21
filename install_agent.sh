#!/bin/bash

sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install python -y
sudo apt-get install python-pip -y
sudo apt-get install python-setuptools -y
sudo apt-get install python3 -y
sudo apt-get install python3-pip -y
sudo apt-get install python3-setuptools -y
sudo apt-get install nodejs -y
sudo apt-get install npm -y
sudo apt-get install git -y
sudo apt-get install sqlite3 -y


sudo pip install pick
sudo pip install psutil
sudo pip install socketIO_client_nexus

sudo pip3 install pick
sudo pip3 install psutil
sudo pip3 install cherrypy
sudo pip3 install hug==2.4.1
sudo pip3 install pymongo
sudo pip3 install hug_middleware_cors
sudo pip3 install socketIO_client_nexus

sudo pip3 install git+https://github.com/adrianARL/Agent2.0.git

sudo mkdir /etc/agent
sudo mkdir /etc/agent/codes
sudo mkdir /etc/agent/config
sudo chmod -R 777 /etc/agent

wget https://raw.githubusercontent.com/adrianARL/Agent2.0/master/start_agent.py
mv start_agent.py /etc/agent/

wget https://raw.githubusercontent.com/adrianARL/Agent2.0/master/device.py

wget -O map.db https://github.com/adrianARL/Agent2.0/blob/master/map.db?raw=true
mv map.db /etc/agent/
