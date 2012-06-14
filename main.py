#!/usr/bin/env python

import webapp2
import urllib
from cookie import *
from password import *
from handlerbase import Handler
from google.appengine.ext import db
from google.appengine.api import memcache
from database import *
import json
import logging
import datetime

class BlogHandler(Handler):
    def get(self):  
        #user = User(username="admin", password=make_pw_hash('admin', 'admin1234'), isadmin=True)
        #user.put()      
        self.render("blog.html")
        
class LoginHandler(Handler):
     def get(self):
        self.render('login.html')

     def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = db.GqlQuery('SELECT * FROM User WHERE username=:1 LIMIT 1', username)
        

        if user.count() > 0 :
            if valid_pw(username, password, user[0].password):
                user_id = make_secure_val(str(user[0].key().id()))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s' % user_id)
                self.redirect('/welcome')
            else:
                self.render('login.html',username=username, error = "invalid password.")
        else:
            self.render('login.html',username=username, error = "invalid login.")

    
        
        

        

app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/login', LoginHandler)],
                              debug=True)
