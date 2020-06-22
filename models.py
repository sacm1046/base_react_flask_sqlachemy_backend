from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key = True)
    fullname = db.Column(db.String(255), nullable = True)
    email = db.Column(db.String(50), nullable = True)
    password = db.Column(db.String(50), nullable = True)

    def __repr__(self):
        return 'User %r' % self.email

    def serialize(self):
        return{
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email
        }

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    value = db.Column(db.Integer, nullable = False)
    number = db.Column(db.Integer, nullable= True, default=1)
    date = db.Column
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    user = db.relationship(User, backref = backref('children', cascade = 'all, delete'))

    def __repr__(self):
        return 'Score %r' % self.value

    def average(self):
        return self.value
    
    def names(self):
        return {
            'id': self.id,
            'name':self.name
        }

    def serialize(self):
        return{
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'number':self.number,
            'user': self.user.serialize()
        }