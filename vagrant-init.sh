#!/usr/bin/env bash

apt-get update

apt-get install -y python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev python3-lxml
apt-get install -y ipython3 # For convenience during development
apt-get install -y libpq-dev # Needed by SQLAlchemy to connect to PostgreSQL

/usr/bin/pip3 install -r /vagrant/requirements.txt

# Run the Heroku installation script
sh /vagrant/heroku-install-ubuntu.sh

# Initialize our db and upgrade it to the latest schema
cd /vagrant && heroku local init
cd /vagrant && heroku local upgrade
