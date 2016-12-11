# Installation 

This is a guide to run this app locally or deploy it to Heroku.


###Dependencies  
Here's a list of the dependencies for this app.  They will all get installed in the 
course of you following these instructions, assuming you deploy to Heroku or use
my Vagrantfile.
- Python 3
- pip
- Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login
- rauth
- yagmail 
- Scrapy, Beautiful Soup
- Postgres
- RabbitMQ, Celery
- Gmail account
- Facebook developer account

### Vagrant setup (if running locally)

I develop this app inside of a VM that I set up with Vagrant.
I've included my Vagrantfile and a bootstrap script inside of this 
repository. 

To set this up for yourself, install Vagrant and Virtualbox on your computer (NB: Vagrant 
prefers a specific version of Virtualbox, which it will prompt you 
to install), then run `vagrant up` in the directory where Vagrantfile is. 

Vagrant will then download the VM image, boot it up, and run the script 
`bootstrap.sh`, which sets up all the packages 
necessary for Mensa Tracker to work.

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

Then, in the root directory of our project, run 
`heroku git:remote --app my-mensa-tracker`.  This will associate your local
git repository with the app you have created in Heroku. Specifically, it adds a 
git remote called `heroku` to your repo.  

The `heroku` command looks at this
git remote to figure out what app your commands should refer to.  E.g. if you run 
`heroku addons:create <addon name>`, normally you would have to add an 
additional `--app <heroku app name>` parameter so Heroku knows which app you're 
adding the addon to, but if you already ran `git:remote --app my-mensa-tracker`, then you don't have to include `--app my-mensa-tracker`
to any future commands you run.  

Finally, run `git push heroku release:master`.  This will deploy the latest
release of our project to your app in Heroku.  You can deploy different versions
by changing the branch name that you give to this command.  For example, if you 
were working on a feature in a local branch `cool-new-feature`, and you wanted to 
test it out on Heroku, you would run `git push heroku cool-new-feature:master`.

We want the addons for RabbitMQ, PostgreSQL, the Heroku Scheduler, 
and Papertrail (which logs the output of any commands we run). These are all free.
Add them to your app with the following commands: 

```
heroku addons:create rabbitmq-bigwig:pipkin
heroku addons:create heroku-postgresql:hobby-dev 
heroku addons:create scheduler:standard 
heroku addons:create papertrail:choklad 
```

The first time you run `heroku`, it will prompt you for your username and 
password. 

The addons don't require any further configuration, except for the scheduler, 
which we will get to shortly. 

If you are deploying the app for other people to use, I would recommend creating
a staging app as well.  Heroku makes this easy using the `heroku fork` command:  
`heroku fork --from my-mensa-tracker --to my-mensa-tracker-staging`
This copies your config vars and addons.
It will also make a copy of your database, assuming you use `heroku-postgresql`. 
 
 After you do that, you can create an App Pipeline to allow you to easily deploy
 code first to staging, and then to production after you verify that it works as 
 expected in staging.
### Set up a Gmail account to send email alerts

Create a new Gmail account and open 
https://www.google.com/settings/security/lesssecureapps.  There, activate access
for less secure apps so that yagmail can log into your account.

### Create a Facebook app 

Go to 
https://developers.facebook.com and create an app there.
  
 If you're deploying to Heroku, set the Facebook app's URL to whatever the URL is of your 
Heroku app, i.e. `http://(your app name).herokuapp.com`. 

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

### Configure environment variables (locally)
If you use PyCharm, there are already run configurations for Flask,
Scrapy, and `queue_daily_emails.py` included in this repo under 
`.idea/runConfigurations`, and they already have all the environment variables
  they need, except for Flask.  For Flask, you have to add your own 
  `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`, and a `SECRET_KEY`.

If you want to use `heroku local` to run your app, open up ".env" in a text editor and configure 
the same environment variables inside of there as described above. `heroku local` loads up those environment variables as if they were 
configured inside of Heroku's web interface. 

### Initialize the database 

Before the app will run, you need to issue the following
command from the project root (where Procfile is located):

```
# If deploying to Heroku:
heroku start upgrade 

#If running locally: 
local:start upgrade
```

### Start the web server

```
# If deploying to Heroku:
heroku start web

# If running locally:
heroku local:start web 
```


### Scheduled tasks  

These commands should be run once a day, from the project's root
directory, in the following order: 
```
# Download the current menu data
python3 menuscraper/main.py 

# Queue up today's email alerts
python3 send_daily_emails.py 

# Send today's email alerts 
# We use timeout so that the worker doesn't hang around forever and use up 
# all your free dyno hours.
timeout 120s celery worker --app=email_alerter.celery_tasks.app
```

I normally run them all after midnight.  

In Heroku, you can enter them in the Scheduler addon's web interface.
There's a link to it in your Heroku app's dashboard.  

If you want to deploy this app outside of Heroku, you could use cron instead.

# Tips for developers  
### IDE run configurations  

You're probably going to want to use Python's interactive debugger
if you're working on this project.  It might not be obvious how to
make that work with `heroku local` and the `.env` file.  Here's what I do.

Forget about .env.  Open your IDE's Run Configurations dialog (I use PyCharm) 
and set up the environment variables in there.  This basically accomplishes the
same thing as if you would define them in .env and run 'heroku local'.

### IPython.  Autoreload.
My Vagrant image includes IPython. It's a pretty popular REPL environment for Python.

It has a feature called autoreload, which, whenever you enter a command on 
the REPL, reloads from disk basically anything that is touched by your command. 
For example, if you type 

``` 
# Prefix commands with heroku local:run so that configuration variables 
# (postgres url, gmail user/pass, etc.) are loaded from .env.

$ heroku local:run ipython3 
>>> %load_ext autoreload 
>>> %autoreload 2 
>>> import email_alerter.email_alerter as el 
>>> el.test_email_generation()  # Prints the output of email_alerts_for_today()
```

While ipython is running and autoreload is turned on, you may edit 
email_alerter.py in a text editor, then go back to iPython
and run the same command again, and any changes you made in the file will be 
reflected in your iPython session. It's great.

