"""
Authored by Andrew J. White - andrew.white@emc.com
Simple script to remove ScaleIO SDS with user input
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
# pulls protection domains, and member SDS servers
instances = '/api/instances'
inst_all = requests.get(base_url + instances, auth=(username, token), verify=False).json()
pd_count = inst_all['protectionDomainList']
#create an sds dictionary and adds each sds id, name
sds_dict = {}
for pd_iter in range(0, len(pd_count)):
    pd_name = pd_count[pd_iter]['name']
    sds_href = pd_count[pd_iter]['links'][3]['href']
    sds_count = requests.get(base_url + sds_href, auth=(username, token), verify=False).json()
    print "Protection Domain: %s" % (pd_name)
    for sds_iter in range(0, len(sds_count)):
        sds_name = sds_count[sds_iter]['name']
        sds_id = sds_count[sds_iter]['id']
        print "SDS Name: " + str(sds_name)
        sds_dict[sds_id] = sds_name
#asks user whcih SDS to remove, validates entry against the current list
while True:
    print ""
    sds_input = raw_input("Which SDS to Remove: ")
    if sds_input not in sds_dict.values():
        print ""
        print "Not a valid SDS - Try Again"
        print ""
    else:
        break
for id, name in sds_dict.iteritems():
    if name == sds_input:
        sds_id_post = id
#rest call to remove specified sds
post_payload = {}
headers = {'Content-Type': 'application/json'}
post_url = '/api/instances/Sds::'
stats = requests.post(base_url + post_url + sds_id_post + '/action/removeSds', json=post_payload, auth=(username, token), headers=headers, verify=False)
