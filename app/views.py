from app import app
from app.models import MenuEntry

from flask import render_template


@app.route('/')
def mensa_history():
    menu_entries = MenuEntry.query.order_by(MenuEntry.date_valid)
    return render_template('mensahistory.html', menu_entries=menu_entries)
