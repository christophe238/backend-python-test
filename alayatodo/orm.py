from alayatodo import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    done = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('todos', lazy='dynamic'))

    def __init__(self, description, user):
        self.description = description
        self.user = user
