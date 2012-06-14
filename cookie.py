import webapp2
import hmac
from password import SECRET

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val
    
def authenticate_cookie(cookie):
    if cookie:
        c = check_secure_val(cookie)
        if c:
            return c