#!/usr/bin/env bash

apt-get update

apt-get install -y python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev python3-lxml rabbitmq-server
apt-get install -y ipython3 # For convenience during development
/usr/bin/pip3 install -r /vagrant/requirements.txt

# Initialize our db and upgrade it to the latest schema
python3 /vagrant/run.py db init
cd /vagrant && python3 run.py db upgrade

# Set up RabbitMQ (used to queue up emails)
rabbitmqctl add_user devuser test123 #username password
rabbitmqctl add_vhost devvhost
# Set permissions for our RabbitMQ user.  (Configuration, Read, Write)
# See https://www.rabbitmq.com/man/rabbitmqctl.1.man.html#set_permissions
rabbitmqctl set_permissions -p devvhost devuser ".*" ".*" ".*"