"""
Authored by Andrew J. White - andrew.white@emc.com
Script to the pull device error status from the SDS Devices on a ScaleIO Cluster.
Use code at own risk - no warranties. - does not use certifcates
Instuctions -  set the connection variable values for username, password, and ip of the ScaleIO gateway
Requirements - tested on ScaleIO 1.32
"""
import token
import requests
import pprint

# disable certificate warnings
requests.packages.urllib3.disable_warnings()
username = 'username'
password = 'password'
base_url = 'https://xxx.xxx.xxx.xxx:443'

def login_func():
    login_response = requests.Session()
    key = login_response.get(base_url + '/api/login', auth=(username, password), verify=False).json()
    if type(key) is dict:
        print "Error Logging In"
    else:
        return key
token = login_func()

def log_check():
    check_login = requests.get(base_url + '/api/instances', auth=(username, token), verify=False)
    if check_login.status_code == 200:
        pass
    else:
        login_func()
        pass
    return None

stats_url = '/api/instances'
stats = requests.get(base_url + stats_url, auth=(username, token), verify=False).json()

for x in range(0, len(stats["deviceList"])):
    dev_state = stats["deviceList"][x]["errorState"]
    dev_name = stats["deviceList"][x]["name"]
    sds_id = stats["deviceList"][x]["sdsId"]
    sds_id_name = requests.get(base_url + "/api/instances/Sds::" + sds_id, auth=(username, token), verify=False).json()
    sds = sds_id_name["name"]
    print "SDS Name: %s, Device Name: %s, Device Error: %s" % (sds, dev_name, dev_state)
