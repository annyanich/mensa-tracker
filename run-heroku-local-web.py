#!/bin/python3
#
# This script is used in my PyCharm run configuration for the Flask web server.
# I wasn't sure how else to run the 'heroku' command inside of the Vagrant VM from PyCharm.

import os
os.system('heroku local web')