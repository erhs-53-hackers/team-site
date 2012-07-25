#!/usr/bin/env python
import sys
sys.path.append("./lib/")
sys.path.append("./lib/db/")

import webapp2
import urllib
from cookie import *
from password import *
from handlerbase import Handler
from google.appengine.api import images
from google.appengine.ext import db
from database import *
import json
import logging
import datetime





class MainHandler(Handler):
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username        
        
        self.render("index.html", user = user)
class BlogHandler(Handler):
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username
        
        #user = User(username="admin", password=make_pw_hash('admin', 'admin1234'), isadmin=True)
        #user.put()
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")      
        self.render("blog.html", user = user, posts = posts)
        
class LoginHandler(Handler):
     def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username
        
        self.render('login.html', user = user, remember = "false")

     def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        remember = self.request.get('remember')       
        

        user = db.GqlQuery('SELECT * FROM User WHERE username=:1 LIMIT 1', username)        

        if user.count() > 0 :
            if valid_pw(username, password, user[0].password):
                user_id = make_secure_val(str(user[0].key().id()))
                header ="user_id=%s" % user_id
                if remember == "true": header += "; expires=Wednesday, 01-Aug-2040 08:00:00 GMT"
                self.response.headers.add_header('Set-Cookie', header)
                self.redirect('/')
            else:
                self.render('login.html',username=username, error = "invalid password", remember=remember)
        else:
            self.render('login.html',username=username, error = "invalid login")

class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/login")
            
class MembersHandler(Handler):
     def get(self):        
        self.login()
        user = None
        if self.user: user = self.user.username
               
                      
        self.render("members.html", user = user)
        

     def post(self):
        cookie = self.request.cookies.get("user_id")
        user = authenticate_cookie(cookie)
        if user: user = get_user(user)
        if user and user.isadmin:
            username = self.request.get('username')
            password = self.request.get('password')
            verify = self.request.get('verify')
            email = self.request.get('email')
            #image = self.request.get('image')
            #logging.error("image: %s" % image)         
            #image = images.resize(image, 32, 32)
            #image = db.Blob(image)
            
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
                
                self.render("members.html", user = user,
                            email = m_email,
                            username = m_user,
                            password =  m_pass,
                            verify = m_verify,
                            mail = email)

class NewpostHandler(Handler):
    def render_form(self, subject="", content="", error="",user=None):
        self.render("newpost.html", subject=subject, content=content, error=error, user=user)
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username
        if user:
            self.render_form(user = user)
        else:
            self.redirect("/login")
        

    def post(self):
        self.login()               
        if self.user:            
            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                post = Post(subject=subject, content=content, username = self.user.username, user = self.user.key().id())            
                post.put()
                self.redirect("/blog")
            else:
                self.render_form(subject, content, "Please provide a title and content", user=self.user.username)

class DeletepostHandler(Handler):    
    def post(self):
        self.login()
        user = None
        if self.user: user = self.user.username            
        if user:
            post = self.request.get("post")
            post = Post.get_by_id(int(post))
            if post:
                post.delete()
        self.redirect("/blog")
        
class EditPostHandler(Handler):
    def get(self, resource):
        self.login()
        user = None
        if self.user: user = self.user.username
                
        post = Post.get_by_id(int(resource))
        post_user = None      
        if post: post_user = post.username
        
        if user == post_user:
            self.render("newpost.html", user = user, 
                                        subject=post.subject, 
                                        content=post.content)
        else:
            self.redirect('/login')
            
    def post(self, ID):
        self.login()
        user = None
        if self.user: user = self.user.username
        
        post = Post.get_by_id(int(ID))
        post_user = None      
        if post: post_user = post.username
        
        if user == post_user:            
            subject = self.request.get("subject")
            content = self.request.get("content")            

            if subject and content:                
                post.subject = subject
                post.content = content        
                post.put()
                self.redirect("/blog")              
            else:
                self.render_form(subject, content, "Please provide a title and content", user=user)
        
class CalendarHandler(Handler):
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username
            
            
        self.render("calendar.html", user = user)
        
class AboutHandler(Handler):
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username
            
        self.render("about.html", user = user)

class ContactHandler(Handler):
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username
        
        self.render("contact.html", user = user)

class SponsorsHandler(Handler):
    def get(self):
        self.login()
        user = None
        if self.user: user = self.user.username

        self.render("sponsors.html", user = user)

        
class ImageHandler(Handler):
    def get(self):
        user = User.get_by_id(int(self.request.get("id")))
        if user.userimage:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(user.userimage)
        else:
            self.error(404)
        

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/blog', BlogHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/newpost', NewpostHandler),
                               ('/members', MembersHandler),
                               ('/contact', ContactHandler),
                               ('/sponsors', SponsorsHandler),
                               ('/deletepost', DeletepostHandler),
                               ('/editpost/(\d+)', EditPostHandler),
                               ('/calendar', CalendarHandler),
                               ('/image', ImageHandler),
                               ('/about', AboutHandler)],
                              debug=True)
