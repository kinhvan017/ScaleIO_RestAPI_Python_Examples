"""
Authored by Andrew J. White - andrew.white@emc.com
Simple script to add ScaleIO pool without advanced settings
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
# Gets the protection name, id and loads it into a dictionary
log_check()
instances = '/api/instances'
inst_all = requests.get(base_url + instances, auth=(username, token), verify=False).json()
pd_count = inst_all['protectionDomainList']
pd_dict = {}
for x in range(0, len(pd_count)):
    pd_id = inst_all["protectionDomainList"][x]["id"]
    pd_name = inst_all["protectionDomainList"][x]["name"]
    pd_dict[pd_id] = pd_name
print "List of Protection Domains:"
for id, name in pd_dict.items():
    print name
#prompts user of what pd to add the pool, validates entry and sets a variable for the pd ID
while True:
    print ""
    pd_input = raw_input("Which Protection Domain to add Storage Pool?: ")
    if pd_input not in pd_dict.values():
        print ""
        print "Not a valid PD - Try Again"
        print ""
    else:
        break

for id, name in pd_dict.iteritems():
    if name == pd_input:
        pd_input_id = id

#create a list of pools, add pool names to list, asks users to name new pools and compares it against list
pool_list = []
sp_list = requests.get(base_url + "/api/instances/ProtectionDomain::"+pd_input_id +"/relationships/StoragePool", auth=(username, token), verify=False).json()
print 'Pools in Protection Domain: %s' % (pd_input)
for x in range(0,len(sp_list)):
    print sp_list[x]['name']
    pool_list.append(sp_list[x]['name'])

while True:
    print ""
    sp_input = raw_input("New Storage Pool Name: ")
    if sp_input in pool_list:
        print ""
        print "Pool exists, try again"
        print ""
    else:
        break
#rest call to add the pool
device_payload = {"protectionDomainId":pd_input_id, "name":sp_input}
post_sp_url = "/api/types/StoragePool/instances"
headers = {'Content-Type': 'application/json'}
post_devices = requests.post(base_url + post_sp_url, auth=(username, token), json=device_payload, headers=headers, verify=False).json()





