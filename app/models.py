from app import db
from flask.ext.login import UserMixin
from sqlalchemy import UniqueConstraint


class MenuEntry(db.Model):
    __tablename__ = 'menu_entries'
    id = db.Column(db.Integer, primary_key=True)
    time_scraped = db.Column(db.DateTime, nullable=False)
    date_valid = db.Column(db.Date, nullable=False)
    mensa = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    __table_args__ = (UniqueConstraint('date_valid', 'mensa', 'category',
                                       'description',
                                       name="unique_menu_entry_date_mensa_category_description"),
                      )

    def __repr__(self):
        return '<MenuEntry scraped: {0} valid: {1} Mensa: {2} Category: {3} ' \
               'Description: {4}'.format(self.time_scraped, self.date_valid,
                                         self.mensa,
                                         self.category, self.description)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    searches = db.relationship("SavedSearch", backref="owner", lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.nickname


class SavedSearch(db.Model):
    __tablename__ = 'searches'
    id = db.Column(db.Integer, primary_key=True)
    search_terms = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<SavedSearch %r>' % self.search_terms
