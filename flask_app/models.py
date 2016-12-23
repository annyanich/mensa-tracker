from flask_app import db
from flask.ext.login import UserMixin
from sqlalchemy import UniqueConstraint

import unicodedata
import locale

class MenuEntry(db.Model):
    __tablename__ = 'menu_entries'
    id = db.Column(db.Integer, primary_key=True)
    time_scraped = db.Column(db.DateTime, nullable=False)
    date_valid = db.Column(db.Date, nullable=False)
    mensa = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    allergens = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    __table_args__ = (UniqueConstraint('date_valid', 'mensa', 'category',
                                       'description',
                                       name="unique_menu_entry_date_mensa_category_description"),
                      )

    def __repr__(self):
        return '<MenuEntry scraped: {0} valid: {1} Mensa: {2} Category: {3} ' \
               'Description: {4} Allergens: {5} ' \
               'Price: {6}'.format(self.time_scraped,
                                   self.date_valid,
                                   self.mensa,
                                   self.category,
                                   self.description,
                                   self.allergens,
                                   locale.currency(self.price/100))

    def to_pretty_text(self):
        return ("{date_valid}\n"
                "{mensa}: {category}\n"
                "{description}\n"
                "Allergens: {allergens}\n"
                "{price}\n").format(
            description=self.description.replace("\n", " "),
            mensa=self.mensa,
            category=self.category,
            date_valid=self.date_valid.strftime("%A, %d.%m.%Y"),
            allergens=self.allergens,
            price=locale.currency(self.price/100)
        )

    def does_search_match(self, search_terms):
        def normalize_caseless(text):
            return unicodedata.normalize("NFKD", text.casefold())

        return normalize_caseless(search_terms) in normalize_caseless(self.description)

MAX_EMAIL_LENGTH = 256
MAX_NICKNAME_LENGTH = 256
MAX_SOCIAL_ID_LENGTH = 64

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(MAX_SOCIAL_ID_LENGTH), nullable=False, unique=True)
    nickname = db.Column(db.String(MAX_NICKNAME_LENGTH), nullable=False)
    email = db.Column(db.String(MAX_EMAIL_LENGTH), nullable=True)
    searches = db.relationship("SavedSearch", backref="owner", lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.nickname


MAX_SEARCH_LENGTH = 64

class SavedSearch(db.Model):
    __tablename__ = 'searches'
    id = db.Column(db.Integer, primary_key=True)
    search_terms = db.Column(db.String(MAX_SEARCH_LENGTH), nullable=False)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<SavedSearch %r>' % self.search_terms
