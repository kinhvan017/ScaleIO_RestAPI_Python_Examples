"""
Authored by Andrew J. White - andrew.white@emc.com
Simple script to pull stats from a volume
Use code at own risk - no warranties. - does not use certifcates
Instuctions -  when executing the script there are 3 required arguments (ip, user, passwd) and the user must specify either a vol_name or vol_id or all


Requirements - tested on ScaleIO 1.32
"""

import token
import requests
import argparse
from prettytable import PrettyTable

#Define and Parse CLI arguments
parser = argparse.ArgumentParser(description='Example implementation of a Python REST client for ScaleIO.')
rflags = parser.add_argument_group('Required arguments')
rflags.add_argument('-ip',         required=True, help='IP of the GW Server 10.0.0.1')
rflags.add_argument('-user',        required=True, help='ScaleIO username. e.g. admin')
rflags.add_argument('-passwd',      required=True, help='ScaleIO password. e.g. password')
sflags = parser.add_argument_group('Additional optional arguments')
sflags.add_argument('-vol_name',     help='user inputed volume name', type=str, default='None')
sflags.add_argument('-vol_id',     help='user inputed volume id', type=str, default='None')
sflags.add_argument('-all',       action='store_true')

args = parser.parse_args()


# disable certificate warnings
requests.packages.urllib3.disable_warnings()
# sets variables from user input
username = args.user
password = args.passwd
base_url = 'https://' + args.ip + ':443'
volumeid = args.vol_id
volumename = args.vol_name
token = None

#sets fome variables for URLs to be used later
instances = '/api/instances'
stats_url = '/api/instances/querySelectedStatistics'
vol_url = '/api/instances/Volume::'

# Validates that volumeid or name has been specified
if volumeid == "None" and volumename == "None" and args.all == False:
    print "No Volume, Complete List - Exiting"
    quit()

#function to log into the cluster and return a token
def login_func():
    login_response = requests.Session()
    key = login_response.get(base_url + '/api/login', auth=(username, password), verify=False).json()
    if type(key) is dict:
        print "Error Logging In"
    else:
        return key
token = login_func()
print token

#function to check if token is valid -

def log_check():
    check_login = requests.get(base_url + '/api/instances', auth=(username, token), verify=False)
    if check_login.status_code == 200:
        pass
    else:
        login_func()
        pass
    return None

#function that takes raw Bwc stats and converts them into IO/s, bw/s
def iops_calc(occur, secs):
    if occur == 0:
        iops = 0
    else:
        iops = occur / secs
    return iops

def bw_calc(occur, secs):
    if occur == 0:
        bw = 0
    else:
        bw = (occur / secs) / 1024
    return bw

log_check()

#sets some variables for pulling the list of volumes - adds volumes to a created dictionary
inst_all = requests.get(base_url + instances, auth=(username, token), verify=False).json()
vol_count = inst_all['volumeList']
vol_dict = {}

for x in range(0, len(vol_count)):
    vol_name = vol_count[x]['name']
    vol_id = vol_count[x]['id']
    vol_dict[vol_name] = vol_id

if args.all == True:
    #Create the pretty table
    tab_out = PrettyTable(["Volume Name", "Volume ID", "Type", "Allocated (GB)", "Thin Used (GB)", "Snap Used (GB)", "Total Used (GB)", "Read IOPS", "Write IOPs", "Read BW (MB/s)", "Write BW (MB/s)"])
    tab_out.align["Volume Name"] = "l"
    tab_out.padding_width = 1
    for key, value in vol_dict.items():
        volumeid = value
        #Get volume name - sets vol_name as json output from call
        vol_name = requests.get(base_url + vol_url + volumeid, auth=(username, token), verify=False).json()
        #pulls the vtree id from using the id
        vol_request = requests.get(base_url + vol_url + volumeid, auth=(username, token), verify=False).json()
        vtree_id = vol_request['vtreeId']
        vtree_stats = requests.get(base_url + "/api/instances/VTree::" + vtree_id + "/relationships/Statistics", auth=(username, token), verify=False).json()
        base_cap = round(float(vtree_stats['baseNetCapacityInUseInKb']) / 1024 / 1024, 1)
        snap_cap = round(float(vtree_stats['snapNetCapacityInUseInKb']) / 1024 / 1024, 1)
        net_cap = round(float(vtree_stats['netCapacityInUseInKb']) / 1024 / 1024, 1)
        vol_type = vol_name["volumeType"]
        if vol_name["volumeType"] == "ThickProvisioned":
            vol_type = "Thick"
            base_cap = "N/A"
        elif vol_name["volumeType"] == "ThinProvisioned":
            vol_type = "Thin"
        #sets varible as the json output from vtree rest call.

        if vol_name["volumeType"] == "Snapshot":
            pass
        else:
            #sets variable vol_stats as the json output to the rest call - sets other variable to specific metrics
            vol_body = {"selectedStatisticsList": [{"type":"Volume", "ids":[volumeid] , "properties": ["userDataWriteBwc", "userDataReadBwc"]}]}
            vol_stats = requests.post(base_url + stats_url, auth=(username, token), json=vol_body, verify=False).json()
            write_bw_weight = vol_stats['Volume'][volumeid]['userDataWriteBwc']['totalWeightInKb']
            write_num_sec = vol_stats['Volume'][volumeid]['userDataWriteBwc']['numSeconds']
            write_iops = vol_stats['Volume'][volumeid]['userDataWriteBwc']['numOccured']
            read_bw_weight = vol_stats['Volume'][volumeid]['userDataReadBwc']['totalWeightInKb']
            read_num_sec = vol_stats['Volume'][volumeid]['userDataReadBwc']['numSeconds']
            read_iops = vol_stats['Volume'][volumeid]['userDataReadBwc']['numOccured']

        #adds each volume to prettytable
            tab_out.add_row([vol_name['name'],volumeid,vol_type ,float(vol_name['sizeInKb']) / 1024 /1024, base_cap,snap_cap ,net_cap, iops_calc(read_iops,read_num_sec), iops_calc(write_iops,read_num_sec),round(float(iops_calc(read_bw_weight,read_num_sec)) / 1024, 2),round(float(iops_calc(write_bw_weight,read_num_sec)) / 1024, 2)])
    #prints pretty table once all of the volumes have been added - sorted by volume name
    print tab_out.get_string(sortby="Volume Name")
else:
    #create a pretty table
    tab_out = PrettyTable(["Volume Name", "Volume ID", "Type", "Allocated (GB)", "Thin Used (GB)", "Snap Used (GB)", "Total Used (GB)", "Read IOPS", "Write IOPs", "Read BW (MB/s)", "Write BW (MB/s)"])
    tab_out.align["Volume Name"] = "l"
    tab_out.padding_width = 1
    #if user does not specify a vol id, uses the vol name to pull from dictionary and sets the volumeid variable
    if volumeid == "None":
        volumeid = vol_dict[volumename]

        vol_name = requests.get(base_url + vol_url + volumeid, auth=(username, token), verify=False).json()
        #pulls the vtree id from using the id
        vol_request = requests.get(base_url + vol_url + volumeid, auth=(username, token), verify=False).json()
        vtree_id = vol_request['vtreeId']
        vtree_stats = requests.get(base_url + "/api/instances/VTree::" + vtree_id + "/relationships/Statistics", auth=(username, token), verify=False).json()
        base_cap = round(float(vtree_stats['baseNetCapacityInUseInKb']) / 1024 / 1024, 1)
        snap_cap = round(float(vtree_stats['snapNetCapacityInUseInKb']) / 1024 / 1024, 1)
        net_cap = round(float(vtree_stats['netCapacityInUseInKb']) / 1024 / 1024, 1)
        vol_type = vol_name["volumeType"]
        if vol_name["volumeType"] == "ThickProvisioned":
            vol_type = "Thick"
            base_cap = "N/A"
        elif vol_name["volumeType"] == "ThinProvisioned":
            vol_type = "Thin"

        #sets varible as the json output from vtree rest call.
        vtree_stats = requests.get(base_url + "/api/instances/VTree::" + vtree_id + "/relationships/Statistics", auth=(username, token), verify=False).json()
        if vol_name["volumeType"] == "Snapshot":
            print "Script Only Reports on Thin or Thick Luns (no snaps)"
            pass
        else:
            #sets variable vol_stats as the json output to the rest call - sets other variable to specific metrics
            vol_body = {"selectedStatisticsList": [{"type":"Volume", "ids":[volumeid] , "properties": ["userDataWriteBwc", "userDataReadBwc"]}]}
            vol_stats = requests.post(base_url + stats_url, auth=(username, token), json=vol_body, verify=False).json()
            write_bw_weight = vol_stats['Volume'][volumeid]['userDataWriteBwc']['totalWeightInKb']
            write_num_sec = vol_stats['Volume'][volumeid]['userDataWriteBwc']['numSeconds']
            write_iops = vol_stats['Volume'][volumeid]['userDataWriteBwc']['numOccured']
            read_bw_weight = vol_stats['Volume'][volumeid]['userDataReadBwc']['totalWeightInKb']
            read_num_sec = vol_stats['Volume'][volumeid]['userDataReadBwc']['numSeconds']
            read_iops = vol_stats['Volume'][volumeid]['userDataReadBwc']['numOccured']

            #adds each volume to prettytable
            tab_out.add_row([vol_name['name'],volumeid,vol_type ,float(vol_name['sizeInKb']) / 1024 /1024, base_cap,snap_cap ,net_cap, iops_calc(read_iops,read_num_sec), iops_calc(write_iops,read_num_sec),round(float(iops_calc(read_bw_weight,read_num_sec)) / 1024, 2),round(float(iops_calc(write_bw_weight,read_num_sec)) / 1024, 2)])
            #prints pretty table once all of the volumes have been added - sorted by volume name
            print tab_out.get_string(sortby="Volume Name")
