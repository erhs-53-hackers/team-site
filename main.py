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

class MainHandler(Handler):
    def get(self):        
        self.render("blog.html")
class LoginHandler(Handler):
    def get(self):
        pass
        
        

        

app = webapp2.WSGIApplication([('/blog', MainHandler)],
                              debug=True)
