#!/usr/bin/python3
from flask_app import app, db

from flask_script import Manager, Server

from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Use a fake bad ssl certificate if running on developer's PC
# (do not deploy the website this way.)
manager.add_command("runserverdev", Server(ssl_context="adhoc"
                                           # ssl_crt="cert.pem",
                                           # ssl_key="key.pem"
                                           ))

if __name__ == '__main__':
    manager.run()
