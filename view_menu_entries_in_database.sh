
#!/bin/sh
psql -c 'select date_valid,category,mensa,description,allergens,price from menu_entries order by date_valid;'

