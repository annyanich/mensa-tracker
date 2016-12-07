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

# Set up RabbitMQ (used to queue up emails)
rabbitmqctl add_user devuser test123 #username password
rabbitmqctl add_vhost devvhost
# Set permissions for our RabbitMQ user.  (Configuration, Read, Write)
# See https://www.rabbitmq.com/man/rabbitmqctl.1.man.html#set_permissions
rabbitmqctl set_permissions -p devvhost devuser ".*" ".*" ".*"
