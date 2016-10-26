#!/usr/bin/env bash

apt-get update

apt-get install -y python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev python3-lxml
apt-get install -y ipython3 # For convenience during development
/usr/bin/pip3 install -r /vagrant/requirements.txt

# Initialize our db and upgrade it to the latest schema
python3 /vagrant/run.py db init
cd /vagrant && python3 run.py db upgrade
