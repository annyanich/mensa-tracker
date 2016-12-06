#!/usr/bin/env bash

apt-get update

apt-get install -y python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev python3-lxml
apt-get install -y ipython3 # For convenience during development
apt-get install -y libpq-dev # Needed by SQLAlchemy to connect to PostgreSQL
apt-get install -y postgresql
apt-get install -y rabbitmq-server

/usr/bin/pip3 install -r /vagrant/requirements.txt

sh /vagrant/heroku-install-ubuntu.sh

sudo -u postgres createuser --superuser vagrant
sudo -u postgres createdb vagrant
sudo -u postgres psql -c "ALTER USER vagrant WITH PASSWORD 'password';"

# Initialize our db and upgrade it to the latest schema
cd /vagrant && heroku local init
cd /vagrant && heroku local upgrade

# Set up RabbitMQ (used to queue up emails)
rabbitmqctl add_user devuser test123 #username password
rabbitmqctl add_vhost devvhost
# Set permissions for our RabbitMQ user.  (Configuration, Read, Write)
# See https://www.rabbitmq.com/man/rabbitmqctl.1.man.html#set_permissions
rabbitmqctl set_permissions -p devvhost devuser ".*" ".*" ".*"