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


sudo pip install pick --upgrade
sudo pip install psutil --upgrade

sudo pip3 install pick --upgrade
sudo pip3 install psutil --upgrade
sudo pip3 install cherrypy --upgrade
sudo pip3 install hug==2.4.1
sudo pip3 install pymongo --upgrade
sudo pip3 install hug_middleware_cors --upgrade

sudo pip3 install git+https://github.com/adrianARL/Agent2.0.git
