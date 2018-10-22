#!/usr/bin/python
import time
import datetime
import requests
from getpass import getpass
import os
from pprint import pprint

import config
from market import *

session = requests.Session()

api = API(session)

def main():
    if not os.path.isfile(config.config_name):
        config.configure()
    username,password = config.get_login()
    api.login(username,password)

    # examples
    # -----------------------------------------------------------------
    api.get_userinfo(16251,"suomynona",150863) # supports usernames and userids
    api.get_items(50000,50001) # returns inventid 50000,50001
    api.get_inventory("hampa",offset=1) # returns 2nd page of hampa's inv
    api.send_tc("example",999999999) 
    api.send_items("example",50000,50001)
    # -----------------------------------------------------------------
if __name__ == "__main__":
    main()
