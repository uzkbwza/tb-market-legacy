import configparser
import os
from getpass import getpass

from market import *

# Globals
# ----------------------------------------------------------------------
config_name = "config" 
config = configparser.ConfigParser()
# ----------------------------------------------------------------------


# Password functs
def hash_pass(passwd):
    hashed = hashlib.md5(passwd.encode()).hexdigest()
    return hashed
    
def check_pass(passwd):
    if hash_pass(passwd) == config['default']['password']:
        return True

def configure():
    print("Creating config")
    username = input(":: Username: ")
    password = getpass(prompt=":: Password: ")
    hashed = hash_pass(password)
    config["default"] = {
            "username":username,
            "password":hashed
            }
    with open(config_name,"w") as config_file:
        config.write(config_file)
    print("Config created")

def get_login():
    config.read(config_name)
    username = config["default"]["username"]
    password = config["default"]["password"]
    return (username,password)

if __name__ == "__main__":
    configure()
