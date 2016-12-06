# Mensa Tracker
Mensa Tracker is a website that automatically checks the menu of your
university's Mensa and sends you an email on days when dishes appear that match 
your search terms.

There are three main modules of this project:
- `menuscraper` 
Downloads menu data and saves it into a database.
- `flask_app` Presents downloaded menu data on a web site. Allows users to enter search 
terms and subscribe to email alerts for them.
- `email_alerter` Sends emails to users when their searches have matches.

Database models are defined in `flask_app/models.py`.  
Database migrations are handled using Flask-Migrate.  See `/migrations`.

Run configurations are defined in Procfile.

### Installation, developing
Read INSTALL.md.

### Authors
Ann Yanich  

Written with the help of Miguel Grinberg's Flask tutorial.

### Contact
Send bugs, feature requests, patches, etc. to ann.yanich@gmail.com.  
