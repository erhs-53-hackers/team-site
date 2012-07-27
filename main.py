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
        
        self.render("index.html", user = self.user)
class BlogHandler(Handler):
    def get(self):
        self.login()
        
        
        #user = User(username="admin", password=make_pw_hash('admin', 'admin1234'), isadmin=True)
        #user.put()
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")      
        self.render("blog.html", user = self.user, posts = posts)
        
class LoginHandler(Handler):
     def get(self):
        self.login()
                
        self.render('login.html', user = self.user, remember = "false")

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
        
        members = db.GqlQuery("SELECT * FROM User")
        members = list(members)    
        members = sorted(members, key=lambda member: member.username.lower())
       
        
        self.render("members.html", user = self.user, users=members, display="none")
        

     def post(self):
        self.login()        
        if self.user and self.user.isadmin:
            username = self.request.get('username')
            password = self.request.get('password')
            verify = self.request.get('verify')
            email = self.request.get('email')
            image = self.request.get('image')
            if image:
                image = images.resize(image, 300, 300)
                image = db.Blob(image)
                logging.error("YES!!! image")
            else:
                logging.error("NO!!!! image")
                        
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
                if image: newuser.userimage = image
                newuser.put()                
                self.redirect('/members')
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
                members = db.GqlQuery("SELECT * FROM User")
                self.render("members.html", user = self.user,
                            email = m_email,
                            username = m_user,
                            password =  m_pass,
                            verify = m_verify,
                            mail = email,
                            display = "block",
                            users=members)

class NewpostHandler(Handler):
    def render_form(self, subject="", content="", error="",user=None):
        self.render("newpost.html", subject=subject, content=content, error=error, user=user)
    def get(self):
        self.login()
        
        if self.user:
            self.render_form(user = self.user)
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
        if self.user:
            post = self.request.get("post")
            if post.isdigit():
                post = Post.get_by_id(int(post))
            else:
                post = None
            
            if post and (post.user == self.user.key().id() or self.user.isadmin):
                post.delete()
        
        self.redirect("/blog")
        
class EditPostHandler(Handler):
    def get(self, resource):
        self.login()        
        
        if self.user and resource.isdigit():
            post = Post.get_by_id(int(resource))      
            
            if post and (post.user == self.user.key().id() or self.user.isadmin):
                self.render("newpost.html", user = self.user.username, 
                                            subject=post.subject, 
                                            content=post.content)
        else:
            self.redirect('/login')
            
    def post(self, ID):
        self.login()
        
        if self.user and ID.isdigit():        
            post = Post.get_by_id(int(ID))           
            if post and (self.user.key().id() == post.user or self.user.isadmin):            
                subject = self.request.get("subject")
                content = self.request.get("content")            

                if subject and content:                
                    post.subject = subject
                    post.content = content        
                    post.put()
                    self.redirect("/blog")              
                else:
                    self.render_form(subject, content, "Please provide a title and content", user=user)
        else:
            self.redirect("/login")
        
class CalendarHandler(Handler):
    def get(self):
        self.login()           
            
        self.render("calendar.html", user = self.user)
        
class AboutHandler(Handler):
    def get(self):
        self.login()        
            
        self.render("about.html", user = self.user)

class ContactHandler(Handler):
    def get(self):
        self.login()
                
        self.render("contact.html", user = self.user)

class SponsorsHandler(Handler):
    def get(self):
        self.login()        

        self.render("sponsors.html", user = self.user)

class ProgrammingHandler(Handler):
    def get(self):
        self.login()        
        
        self.render("programming.html", user = self.user)

        
class ImageHandler(Handler):
    def get(self):
        user = db.get(self.request.get("id"))
        if user.userimage:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(user.userimage)
        else:
            self.error(404)
            
class ProfileHandler(Handler):
    def get(self, res):
        self.login()
        profile = db.GqlQuery("SELECT * FROM User WHERE username=:1 LIMIT 1", res)
        profile = list(profile)
        if len(profile) == 1:
            self.render("profile.html", user = self.user, profile = profile[0])
        else:
            self.error(404)
            
class EditProfileHandler(Handler):
    def get(self, res):
        self.login()
        profile = db.GqlQuery("SELECT * FROM User WHERE username=:1 LIMIT 1", res)
        profile = list(profile)
        if len(profile) == 1:
            profile = profile[0]
            if self.user.key().id() == profile.key().id():
                prog = ""
                mec  = ""
                out  = ""
                mang = ""
                
                if profile.team == "Programming":
                    prog = 'selected="selected"'
                elif profile.team == "Mechanical":
                    mec  = 'selected="selected"'
                elif profile.team == "Outreach":
                    out  = 'selected="selected"'
                elif profile.team == "Management":
                    mang = 'selected="selected"'
                    
                currentProjects = ""
                                
                for i in range(len(profile.currentProjects)):
                    if i == 0:
                        currentProjects += profile.currentProjects[i]
                    else:
                        currentProjects += ", " + profile.currentProjects[i]
                        
                pastProjects = ""
                                
                for i in range(len(profile.pastProjects)):
                    if i == 0:
                        pastProjects += profile.pastProjects[i]
                    else:
                        pastProjects += ", " + profile.pastProjects[i]
                    
                
                self.render("editprofile.html", user = self.user, profile = profile,
                            currentProjects=currentProjects ,pastProjects=pastProjects,
                            prog=prog, mec=mec, out=out, mang=mang)
            else:
                self.redirect("/login")
        else:
            self.error(404)
    def post(self, res):
        self.login()        
        profile = db.GqlQuery("SELECT * FROM User WHERE username=:1 LIMIT 1", res)
        profile = list(profile)
        if len(profile) == 1 and self.user and self.user.key().id() == profile[0].key().id():
            profile = profile[0]
            quote        = self.request.get("quote")
            team         = self.request.get("team")
            currentProjs = self.request.get("currentProjects")
            pastProjs    = self.request.get("pastProjects")
            email        = self.request.get("email")
            image        = self.request.get("image")
            
            if image:
                image = images.resize(image, 300, 300)
                image = db.Blob(image)
            
            currentProjs = currentProjs.split(',')
            for i in range(len(currentProjs)):
                currentProjs[i] = currentProjs[i].strip()
            
            pastProjs = pastProjs.split(',')
            for i in range(len(pastProjs)):
                pastProjs[i] = pastProjs[i].strip()
            
            profile.quote           = quote
            profile.team            = team
            profile.currentProjects = currentProjs
            profile.pastProjects    = pastProjs
            profile.email           = email            
            if image: profile.userimage = image
            
            profile.put()
            
            self.redirect("/profile/%s" % res)
        else:
            self.redirect("/login")
            
        
       
                
        
        
        
        

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
                               ('/about', AboutHandler),
                               ('/profile/(.+)', ProfileHandler),
                               ('/editprofile/(.+)', EditProfileHandler),
                               ('/programming', ProgrammingHandler)],
                               debug=True)
