#!/usr/bin/env bash

apt-get update

apt-get install -y apache2
if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi

apt-get install -y python3-pip python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev python3-lxml
/usr/bin/pip3 install -r /vagrant/requirements.txt
python3 /vagrant/oauth_example_app.py db init
cd /vagrant && python3 oauth_example_app.py db upgrade
ln -s /vagrant/start_server.sh /home/vagrant/start_server.sh

