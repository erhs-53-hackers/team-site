from google.appengine.ext import db
from google.appengine.api import memcache

def get_user(num):
    if num:
        user = memcache.get(str(num))
        if not user:
            user = User.get_by_id(int(num))
            if user:
                memcache.set(str(num), user)
        return user

class Post(db.Model):
    username = db.StringProperty(required = True)
    user     = db.IntegerProperty()
    subject  = db.StringProperty(required = True)
    content  = db.TextProperty(required = True)
    created  = db.DateTimeProperty(auto_now_add = True)
    
class User(db.Model):
    userimage = db.BlobProperty()
    username  = db.StringProperty(required = True)
    password  = db.StringProperty(required = True)
    email     = db.StringProperty()
    isadmin   = db.BooleanProperty(required = True)

    