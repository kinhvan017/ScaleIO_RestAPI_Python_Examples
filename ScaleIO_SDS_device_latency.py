"""
Authored by Andrew J. White - andrew.white@emc.com
Simple script to cycle through the ScaleIO SDS servers and print out the device latency for each device
Use code at own risk - no warranties. - does not use certifcates
Instuctions -  set the connection variable values for username, password, and ip of the ScaleIO gateway
Requirements - tested on ScaleIO 1.32
"""
import token
import requests


# disable certificate warnings
requests.packages.urllib3.disable_warnings()
#Connection Variables
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

def get_stats():
    # high level objects
    instances = '/api/instances'
    #check login
    log_check()
    #generate the list of and # of SDS's
    get_config = requests.get(base_url + instances, auth=(username, token), verify=False).json()
    sds_count = get_config['sdsList']
    #iterates through the SDSs
    for sds_iter in range(0, len(sds_count)):
        sds_list = sds_count[sds_iter]['links'][2]['href']
        sds_name = sds_count[sds_iter]['name']
        dev_count_per_sds = requests.get(base_url + sds_list, auth=(username, token), verify=False).json()
        print sds_name
        #iterates through the devices on each sds
        for dev_count_iter in range(0, len(dev_count_per_sds)):
            dev_stat_link = dev_count_per_sds[dev_count_iter]['links'][1]['href']
            device_name = dev_count_per_sds[dev_count_iter]['name']
            dev_stat = requests.get(base_url + dev_stat_link, auth=(username, token), verify=False).json()
            dev_wl_output = dev_stat['avgWriteLatencyInMicrosec']
            dev_rl_output = dev_stat['avgReadLatencyInMicrosec']
            print "Device Name: %s Read Latency: %s Write Latency: %s" % (device_name, dev_wl_output, dev_rl_output)

get_stats()

