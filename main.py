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
                self.redirect('/')
            else:
                self.render('login.html',username=username, error = "invalid password")
        else:
            self.render('login.html',username=username, error = "invalid login")
            
class AdminHandler(Handler):
     def get(self):
        self.render("admin.html")

     def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        v_user = match(USER, username)
        v_pass = match(PASS, password)
        v_verify = None
        if password == verify:
            v_verify = 1       

        v_email = 1
        if email: v_email = match(EMAIL, email)

        v_existing_user = db.GqlQuery('SELECT * FROM User WHERE username=:1', username)
        v_existing_user = v_existing_user.count()

        if v_user and v_pass and v_verify and v_email and v_existing_user < 1:
            password = make_pw_hash(username, password)
            newuser = User(username=username, password=password, email = email, isadmin=False)
            newuser.put()
            user_id = make_secure_val(str(newuser.key().id()))
            self.response.headers.add_header('Set-Cookie', 'user_id=%s' % user_id)
            self.redirect('/')
        else:
            m_user = ''
            m_pass = ''
            m_verify = ''
            m_email = ''
            if not v_user: m_user = 'not a valid username.'            
            if not v_pass: m_pass = 'not a valid password.'
            if not v_verify: m_verify = 'passwords do not match.'
            if not v_email: m_email = 'not a valid email.'
            if v_existing_user > 0: m_user = 'That user already exists.'
            
            self.render("admin.html", name = username,
                        email = m_email,
                        username = m_user,
                        password =  m_pass,
                        verify = m_verify,
                        mail = email)


    
        
        

        

app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/login', LoginHandler),
                                ('/admin', AdminHandler)],
                              debug=True)
