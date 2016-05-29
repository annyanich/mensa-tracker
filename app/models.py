from app import db
from flask.ext.login import UserMixin


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