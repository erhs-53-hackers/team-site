import webapp2
import re
import random
import hashlib
import string

SECRET = "devel secret"

USER  = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS  = re.compile(r"^.{3,20}$")
EMAIL = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def match(re, s):
    return re.match(s)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (h, salt)

def valid_pw(name, pw, h):
    h2 = make_pw_hash(name, pw, h.split('|')[1])
    if h2 == h:
        return True
    return False
