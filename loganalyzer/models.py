from datetime import datetime
from sqlalchemy import desc
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from loganalyzer import db

tags = db.Table('support_bundle_tag',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('support_bundle_id', db.Integer, db.ForeignKey('support_bundle.id'))
                )

class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), nullable=False, unique=True)
    password_hash=db.Column(db.String(120), nullable=False)
    name=db.Column(db.String(30), nullable=False)
    surname=db.Column(db.String(30), nullable=False)
    email=db.Column(db.String(80), nullable=False)
    supportbundle = db.relationship('SupportBundle', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return '<User %r>' % self.username


class SupportBundle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_request = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    path = db.Column(db.Text, nullable=True)
    datetime = db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _tags = db.relationship('Tag', secondary=tags, lazy='joined', backref=db.backref('supportbundles', lazy='dynamic'))

    @staticmethod
    def newest(num):
        return SupportBundle.query.order_by(desc(SupportBundle.datetime)).limit(num)

    @property
    def tags(self):
        return ",".join([t.name for t in self._tags])

    @tags.setter
    def tags(self,string):
        if string:
            self._tags = [Tag.get_or_create(name) for name in string.split(',')]
        else:
            self._tags = []

    def __repr__(self):
        return "<filename: '{}', SR: '{}', coment: '{}'>".format(self.filename,self.service_request,self.comment)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False, unique=True, index=True)

    @staticmethod
    def get_or_create(name):
        try:
            return Tag.query.filter_by(name=name).one()
        except:
            return Tag(name=name)

    @staticmethod
    def all():
        return Tag.query.all()

    def __repr__(self):
        return self.name
