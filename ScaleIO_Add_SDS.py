"""
Authored by Andrew J. White - andrew.white@emc.com
Simple script to add ScaleIO SDS servers with user input
Use code at own risk - no warranties. - does not use certifcates
Instuctions -  set the connection variable values for username, password, and ip of the ScaleIO gateway
Requirements - tested on ScaleIO 1.32
"""

import token
import requests

# disable certificate warnings
requests.packages.urllib3.disable_warnings()
username = ‘user’
password = ‘password’
base_url = 'https://xxx.xxx.xxx.xxx:443'
token = None

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
#pulls the protection domain ID, name and puts it in a dictionary
log_check()
instances = '/api/instances'
inst_all = requests.get(base_url + instances, auth=(username, token), verify=False).json()
pd_count = inst_all['protectionDomainList']
pd_dict = {}
for x in range(0, len(pd_count)):
    pd_id = inst_all["protectionDomainList"][x]["id"]
    pd_name = inst_all["protectionDomainList"][x]["name"]
    pd_dict[pd_name] = pd_id
print "Protection Domain List:"
for name, id in pd_dict.items():
    print name
#asks user to select a protection domain to add sds , validates if the pd exists
while True:
    print ""
    pd_input = raw_input("Which Protection Domain to add SDS?: ")
    if pd_input not in pd_dict.keys():
        print ""
        print "Not a valid PD - Try Again"
        print ""
    else:
        break
#pools the sds ips, names and loads them into a dictionary
sds_dict = {}
instances = '/api/types/Sds/instances'
inst_sds = requests.get(base_url + instances, auth=(username, token), verify=False).json()
for x in range(0, len(inst_sds)):
    sds_name = inst_sds[x]['name']
    for y in range(0, len(inst_sds[x]["ipList"])):
        sds_ip = inst_sds[x]["ipList"][y]['ip']
        sds_dict[sds_ip] = sds_name
#asks user for name,ip of new sds, compares against list of existing
while True:
    sds_name = raw_input("New SDS Name: ")
    if sds_name in sds_dict.values():
        print ""
        print "Name Already in Use, Try again"
        print ""
    else:
        break


while True:
    ip_addr = raw_input("Add IP Address for SDS: ")
    if ip_addr in sds_dict.keys():
        print ""
        print "IP Already in Use, Try again"
        print ""

    else:
        break
#user configures first IP for the SDS, assigns a role (default is all)
role = 'all'
print "IP Address Role Options:"
print "1. All"
print "2. SDS-SDS Only"
print "3. SDS-SDC Only"
set_role = raw_input("Which Test Option (use number): ")
if set_role == "1":
    role = "all"
elif set_role == "2":
    role = "sdsOnly"
elif set_role == "3":
    role = "sdcOnly"
else:
    print "Not a valid option, using default"
#Rest call to add the sds to the protection domain
post_payload = {"protectionDomainId": pd_dict[pd_input],"name":sds_name, "sdsIpList":[{"SdsIp":{"ip":ip_addr, "role": role}}]}
post_url = '/api/types/Sds/instances'
headers = {'Content-Type': 'application/json'}
stats = requests.post(base_url + post_url, auth=(username, token), json=post_payload, headers=headers, verify=False).json()
sds_id = stats['id']
print "New SDS ID: %s" % (sds_id)

#function to add additional IP's to the newly created SDS
def sds_add_ip():
    ip_iter = 0
    while True:
        ip_addr = raw_input("Add IP Address for SDS: ")
        if ip_addr in sds_dict.keys():
            print ""
            print "IP Already in Use, Try again"
            print ""
        else:
            break

    role = 'all'
    print "IP Role Options:"
    print "1. All"
    print "2. SDS-SDS Only"
    print "3. SDS-SDC Only"
    set_role = raw_input("Which Role for the IP (use number): ")
    if set_role == "1":
        role = "all"
    elif set_role == "2":
        role = "sdsOnly"
    elif set_role == "3":
        role = "sdcOnly"
    else:
        print "Not a valid option, using default"
    post_payload = {"ip":ip_addr, "role": role}
    post_url = '/api/instances/Sds::'+ sds_id+'/action/addSdsIp'
    headers = {'Content-Type': 'application/json'}
    stats = requests.post(base_url + post_url, auth=(username, token), json=post_payload, headers=headers, verify=False).json()
add_another_ip = raw_input("Add Another IP to "+sds_name+" (y or n)? ")

#asks user if they want to add additional IP's to the SDS
if add_another_ip == 'y':
    sds_add_ip()

#creates a dictionary of storage pool id, name
sp_dict = {}
sp_rel = "/api/instances/ProtectionDomain::" + pd_dict[pd_input] + "/relationships/StoragePool"
inst_sp = requests.get(base_url + sp_rel, auth=(username, token), verify=False).json()
for w in range(0, len(inst_sp)):
    sp_dict[inst_sp[w]['name']] = inst_sp[w]['id']

#asks if user wants to add devices to storage pool
dev_yn = raw_input("Add Devices from "+sds_name+ "(y or n?) ")
#prompt to add devices and asks if advanced options are required
if dev_yn == 'y':
    device_count = raw_input('How many devices to add?: ')
    device_count = int(device_count)
    for z in range(0, device_count):
        device_path = raw_input("Device #"+ str(z) + " Path: ")
        device_name = raw_input("Device #"+ str(z) + " Name: ")
        print "Available Pools in Protection Domain: %s" % (pd_input)
        for name, id in sp_dict.items():
            print name
        while True:
            device_pool = raw_input("Device #"+ str(z) + " Pool: " )
            if device_pool not in sp_dict.keys():
                print ""
                print "Not a valid pool, try again"
                print ""
            else:
                break
        mode = "testAndActivate"
        testtime = "10"
        dev_adv = raw_input("Set Advanced Parameters (y or n)? ")
        if dev_adv == 'y':
            print "Test Mode Options:"
            print "1. Test Only"
            print "2. No Test"
            print "3. Test and Activiate"
            set_test_mode = raw_input("Which Test Option (use number): ")
            if set_test_mode == "1":
                mode = "testOnly"
                set_test_time = raw_input("Test Time: ")
                testtime = set_test_time
            elif set_test_mode == "2":
                mode = "noTest"
            elif set_test_mode == "3":
                mode = "testAndActivate"
                set_test_time = raw_input("Test Time: ")
                testtime = set_test_time
            else:
                print "Not a valid option, using default"

        #rest call to create each device with parameters
        device_payload = {"deviceCurrentPathname":device_path, "storagePoolId": sp_dict[device_pool], "deviceName":device_name, "sdsId":sds_id,"deviceTestMode":mode, "testTimeSecs":testtime }
        post_dev_url = "/api/types/Device/instances"
        post_devices = requests.post(base_url + post_dev_url, auth=(username, token), json=device_payload, verify=False).json()
