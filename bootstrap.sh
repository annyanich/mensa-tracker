#!/usr/bin/env bash

# add heroku repository to apt
echo "deb http://toolbelt.heroku.com/ubuntu ./" > /etc/apt/sources.list.d/heroku.list

# install heroku's release key for package verification
apt-key add /vagrant/heroku_release.key

apt-get update

apt-get install -y python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev python3-lxml
apt-get install -y git ipython3 # For convenience during development
apt-get install -y libpq-dev # Needed by SQLAlchemy to connect to PostgreSQL
apt-get install -y postgresql
apt-get install -y rabbitmq-server
apt-get install -y heroku-toolbelt

/usr/bin/pip3 install -r /vagrant/requirements.txt

sudo -u postgres createuser --superuser vagrant
sudo -u postgres createdb vagrant
sudo -u postgres psql -c "ALTER USER vagrant WITH PASSWORD 'password';"

# Enable the RabbitMQ web UI, which you can access at http://192.168.56.2:15672
# (Replace 192.168.56.2 with your VM's IP, if you changed it in Vagrantfile.)
# Username: guest
# Password: guest
# This lets you peek at the emails in the queue.
rabbitmq-plugins enable rabbitmq_management
/etc/init.d/rabbitmq-server restart

# Upgrade the app's db to the latest version
export DATABASE_URL='postgres://vagrant@localhost:5432/vagrant'
export PGPASSWORD='password'
cd /vagrant && python3 /vagrant/flask_manage.py db upgrade