import requests
import time
from functools import wraps

# Globals
# ----------------------------------------------------------------------

TIMEOUT = 1.0
BASE_URL = "http://forum.toribash.com/"

# Timeout and request related functs. To ensure rate limit is obeyed
# and other general functions
def request(funct):
    """General request function. 
    Delays request to rate limit and logs (todo)"""
    @wraps(funct)
    def wrapper(*args,**kwargs):
        return timeout(funct,*args,**kwargs)
    return wrapper

def timeout(funct,*args,**kwargs):
    start = time.time()
    result = funct(*args,**kwargs)
    end = time.time()
    elapsed = end - start
    if elapsed <= 1:
        time.sleep(1-elapsed + 0.01) 
    # Args is sliced this way so _tori_market() doesnt raise IndexError
    # print("Request: " + funct.__name__ + str([*args[1:2]]))
    return result

def comma_separated_values(values):
    """For requests that require multiple values for one parameter"""
    string_values = [str(value) for value in values]
    string = ",".join(string_values)
    return string

# ----------------------------------------------------------------------

class API():
    """Class which contains all toribash market API functions"""
    def __init__(self,session):
        self.session = session
        self.headers = {"Accept":"application/json"}

    def login(self,username,md5pass):
        """Uses login info to get token"""
        print("Logging in " + username)
        try:
            self.session.post(
                BASE_URL + "login.php?do=login", {
                    "vb_login_username": username,
                    "vb_login_password": "",
                    "vb_login_md5password": md5pass,
                    "vb_login_md5password_utf": md5pass,
                    "cookieuser": 1,
                    "do": "login",
                    "s": "",
                    "securitytoken": "guest" }
                )
            url = BASE_URL + 'bank_ajax.php?bank_ajax=get_token'
            self.token = self.session.get(url).json()["token"] 
            print("Logged in\n")
            self.userid = self._tori_market()["user"]["userid"]
        except KeyError:
            print("Login failed, did you enter everything correctly?")

    def get_userinfo(self,*users):
        """Returns username, TC, qi, etc"""
        params = {}
        if users:
        # Get info of all users passed
            if len(users) > 50:
                raise ValueError("'get_userinfo' can load no more than 50 users at a time")
            users = self._names_to_id(*users)
            if len(users) > 1:
                users = comma_separated_values(users)
            print("Getting info for users: " + users)
            params = {"userid":users}
            request = self._bank_ajax("get_userinfo",params)
            print("Info retrieved")
            return request
        # Else lack of users parameter recursively gets own user info
        print("(Using own ID)")
        request = self.get_userinfo(self.userid)
        print("Retrieved user info")
        return request

    def get_inventory(self,user,offset=0,excludeids=None):
        """Returns inventory of user and without
        excluded IDs"""
        if not user:
            user = self.get_userinfo()["users"][0]["userid"]
        user = self._names_to_id(user)
        print("Getting inventory for user: " + str(user))
        params = {"userid":user,
                  "offset":offset,
                  "excludeids":excludeids}
        request = self._bank_ajax("get_inventory",params)
        print("Retrieved user inventory")
        return request

    def get_items(self,*inventids):
        """Returns info for specific item instance in an inventory"""
        print("Getting items")
        if inventids:
           inventids = comma_separated_values(inventids)
           params = {"inventid":inventids}
        else:
            raise RuntimeError("'inventids' are required for get_items()")
        request = self._bank_ajax("get_items",params)
        print("Retrieved items")
        return request

    def send_items(self,user,*inventids,message="",
            omit_items_with_errors=1,use_admin_override=0,via_shop_admin=0,confirm=True):
        print("Sending items to " + str(user))
        userid = self._names_to_id(user)
        if inventids:
           inventids = comma_separated_values(inventids)
           params = {"inventid":inventids} 
        params.update({"token":self.token,
                       "userid":userid,
                       "message":message,
                       "omit_items_with_errors":omit_items_with_errors,
                       "use_admin_override":use_admin_override,
                       "via_shop_admin":via_shop_admin})
        if confirm:
            confirm_string = ":: Send {} to userid {}? (y/n) ".format(inventids,userid)
            if input(confirm_string).lower() != "y":
                return
        request = self._bank_ajax("send_items",params)
        print(request)
        return request

    def send_tc(self,to_userid,amount,confirm=True,
            from_userid=None,message="",use_admin_override=0,
            via_shop_admin=0):
        print("Sending TC to {}".format(to_userid))
        if not from_userid:
            from_userid = self.userid
        from_userid,to_userid = self._names_to_id(from_userid,to_userid)
        params = {"amount":amount,
                  "from_userid":from_userid,
                  "to_userid":to_userid,
                  "message":message,
                  "use_admin_override":use_admin_override,
                  "via_shop_admin":via_shop_admin,
                  "token":self.token}
        if confirm:
            confirm_string = ":: Send {} TC to userid {}? (y/n) ".format(amount,to_userid)
            if input(confirm_string).lower() != "y":
                return
        request = self._bank_ajax("send_tc",params)
        print(request)
        return(request)

    @request
    def _bank_ajax(self,name,params):
        """Returns json of and posts with specified bank_ajax parameters"""
        url = BASE_URL + "bank_ajax.php?"
        params.update({"bank_ajax":name})
        request = self.session.post(url,data=params)
        request.raise_for_status()
        return request.json()

    @request
    def _tori_market(self):
        """Returns json of current market API"""
        url = BASE_URL + "tori_market.php?"
        params = {"format":"json"}
        return self.session.get(url,params=params).json()

    def _names_to_id(self,*users):
        usernames = [user for user in users if isinstance(user,str)]
        userids = [user for user in users if user not in usernames]
        usernames = comma_separated_values(usernames) 
        params = {"username":usernames}
        request = self._bank_ajax("get_userinfo",params)
        for username in request["users"]:
            userids.append(int(username["userid"]))
        if len(userids) == 1:
            return userids[0]
        return userids

