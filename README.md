# Ann's Mensa Tracker
Ann's Mensa Tracker is a website that automatically checks the menu of your
university's Mensa and sends you an email on days when dishes appear that match 
your search terms.

There are three main modules of this project:
- `menuscraper` Scrapes menu data from the Studentenwerk's website and saves it into a database once a day.
- `flask_app` Presents menu data on a web site.  Allows users to search for dishes matching key words and subscribe to email alerts for them.
- `email_alerter` Sends emails once a night to users whose searches have matches.

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
