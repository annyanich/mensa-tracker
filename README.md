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

Run configurations are defined in Procfile.  
Database models are defined in `flask_app/models.py`.  
Database migrations are handled using Flask-Migrate.  See `/migrations`.


### Installation, running, developing
See INSTALL.md.

### Authors, credits
Ann Yanich  

I'd like to thank Miguel Grinberg for writing The Flask 
Mega-Tutorial.  I based my Flask project on his examples. You can find part 1 of 
his tutorial at  
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world .

### Contact
Send bugs, feature requests, patches, etc. to ann.yanich@gmail.com.  
