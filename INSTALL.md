# Installation 

This is a guide to run this app locally or deploy it to Heroku.
If you into any trouble while following these steps, please let 
me know, and I'll be glad to help you figure it out.

###Dependencies  
Here's a list of the dependencies for this app.  They will all get installed in the 
course of you following these instructions, assuming you deploy to Heroku or use
my Vagrantfile.
- Python 3, pip
  - Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login
  - rauth
  - yagmail 
  - Scrapy
  - Beautiful Soup 4
  - Celery
- Postgres
- RabbitMQ, Celery
- Gmail account
- Facebook developer account

### Vagrant setup (if running locally)

I develop this app inside of a VM that I set up with Vagrant.
I've included my Vagrantfile and a bootstrap script inside of this 
repository. 

To set this up for yourself, install Vagrant and Virtualbox on your computer 
(NB: Vagrant prefers a specific version of Virtualbox, which it will prompt you 
to install), then run `vagrant up` in the directory where Vagrantfile is. 

Vagrant will then download the VM image, boot it up, and run the script 
`bootstrap.sh`, which sets up all the packages necessary for Mensa Tracker
to work.

In case you haven't used Vagrant before, here are some useful commands:
- `vagrant up` If the VM isn't there, initialize it.  Otherwise, boot it up.
- `vagrant ssh` Open a shell inside of the VM.
- `vagrant halt` Shut the VM down gracefully.
- `vagrant destroy` Throw the VM out.  Lets you start from scratch in case you 
messed the VM up, or if you made some changes to bootstrap.sh, requirements.txt 
and would like to verify that they work as expected.

### Create a Heroku app and configure addons
You can skip this section if you just want to run the app locally.

Register at heroku.com, log in, and define a new app there.  Give it a name,
e.g. 'my-mensa-tracker'.  

Then, in the root directory of our project (i.e. /vagrant if you are in the VM), run 
`heroku git:remote --app my-mensa-tracker`.  (It may ask you to log in to
your Heroku account.)  This will associate your local
git repository with the app you have created in Heroku. Specifically, it adds a 
git remote called `heroku` to your repo.  The `heroku` command will use this
special git remote to infer what app you are working with, saving you trouble of 
adding `--app my-mensa-tracker` to the end of all of your commands.

Now that that's done, we're going to add the addons for RabbitMQ, PostgreSQL, 
the Heroku Scheduler, and Papertrail (which logs the output of any commands we 
run). These are all free. Add them to your app with the following commands 
(from inside of /vagrant): 

```
heroku addons:create rabbitmq-bigwig:pipkin
heroku addons:create heroku-postgresql:hobby-dev 
heroku addons:create scheduler:standard 
heroku addons:create papertrail:choklad 
```

The addons don't require any further configuration, except for the scheduler, 
which we will get to shortly. 

### Set up a Gmail account to send email alerts

Create a new Gmail account and open 
https://www.google.com/settings/security/lesssecureapps.  There, activate access
for less secure apps so that yagmail can log into your account.

### Create a Facebook app 

Go to 
https://developers.facebook.com 
and create an app there.
  
If you're deploying to Heroku, set the Facebook app's URL to whatever the URL 
is of your Heroku app, i.e. `http://(your app name).herokuapp.com`. 

For local development, you should point the URL to to the local URL of
your vagrant VM, e.g. 
`http://192.168.56.2:5000`.  
You should define separate Facebook apps for local development, staging, and 
deployment.

### Configure environment variables (in Heroku) 
Open the settings for your app in Heroku's web interface.  
Click the button "Reveal Config Vars."  
Define the following environment variables: 

  - FACEBOOK_APP_ID (from Facebook) 
  - FACEBOOK_APP_SECRET (from Facebook) 
  - GMAIL_USERNAME 
  - GMAIL_PASSWORD 
  - SECRET_KEY  
  (Generate it yourself. http://flask.pocoo.org/docs/0.11/quickstart/ suggests using 
the Python function os.urandom() inside of an interactive Python shell: 

    ```
    $ python3 -i 
    >>> import os 
    >>> os.urandom(24) 
    '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
    ```
    Copy and paste that big random blob into Heroku's settings, and you're golden. 

### Configure environment variables (for local development)
If you use PyCharm, there are already run configurations for Flask,
Scrapy, and `queue_daily_emails.py` included in this repo under 
`.idea/runConfigurations`, and they already have all the environment variables
  they need, except for Flask.  For Flask, you have to add your own 
  `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, and `SECRET_KEY`.

If you want to use `heroku local` to run your app, open up ".env" in a text 
editor and configure the same environment variables inside of there as described
above. `heroku local` will use those environment variables as if they were 
configured inside of Heroku's web interface. 

### Initialize the database 

For local development purposes, you may use the "Upgrade DB" run configuration from inside of PyCharm. 
You may also run one of the following shell commands:
```
heroku local:start upgrade
# does the same thing as
python3 flask_manage.py db upgrade
# but 'heroku local' loads its environment variables from the file '.env'
```

To initialize the database in Heroku, you can run this command:

```
heroku start upgrade 
```

### Start the web server
To run it locally from PyCharm, you can use the "Flask web server" run 
configuration.  Be sure to add your own Facebook API key and SECRET_KEY to the 
environment variables if you haven't already.

Otherwise, if you're deploying to Heroku or don't have PyCharm, you can run one 
of the following commands:
```
# If deploying to Heroku:
heroku start web

# If running locally:
heroku local:start web 
```


### Define scheduled tasks  

These commands should be run once a day, from the project's root
directory, in the following order: 
```
# Download the current menu data
python3 menuscraper/main.py 

# Queue up today's email alerts
python3 send_daily_emails.py 

# Send the queued up email alerts 
# We use timeout so that the worker doesn't hang around forever and use up 
# all your free dyno hours.
timeout 120s celery worker --app=email_alerter.celery_tasks.app
```

I normally run them all after midnight.  

In Heroku, you can enter them in the Scheduler addon's web interface.
There's a link to it in your Heroku app's dashboard.  It's pretty 
self-explanatory.

If you want to deploy this app outside of Heroku, you could use cron instead.

### Finished!
After following the above steps, you should now have a working installation
of Ann's Mensa Tracker.

### (Optional) Set up a staging app on Heroku
If you are deploying an app for other people to use as you develop it, I would 
recommend creating a staging app as well.  Heroku makes this easy using the 
`heroku fork` command:  
`heroku fork --from my-mensa-tracker --to my-mensa-tracker-staging`
This will copy the config vars and addons that you configured above, and it will
make a copy of your `heroku-postgresql` database, which is nice if you want to 
test out some potentially dangerous database operations.
 
After you do that, you can add the fork to an App Pipeline, which will  allow 
you to easily deploy code first to staging, and then to production after you 
verify that it works as expected. The exact details of how to do that are beyond
the scope of this document, but there is some helpful documentation on Heroku's
website:  https://devcenter.heroku.com/articles/pipelines
