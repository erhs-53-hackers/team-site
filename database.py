from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email    = db.StringProperty()
    isadmin  = db.BooleanProperty(required = True)