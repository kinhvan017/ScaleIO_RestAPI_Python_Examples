"""
Authored by Andrew J. White - andrew.white@emc.com
Simple script to pull and print some ScaleIO Stats from a cluster.
Use code at own risk - no warranties. - does not use certifcates
Instuctions -  set the connection variable values for username, password, and ip of the ScaleIO gateway
Requirements - tested on ScaleIO 1.32
"""
import token
import requests
import pprint
# disable certificate warnings
requests.packages.urllib3.disable_warnings()
#Connection variables
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

#pulls the selected stats from the list
stat_prop = {"selectedStatisticsList":[{"type":"System", "allIds":"", "properties":["primaryReadBwc", "primaryWriteBwc", "numOfVolumes", "maxCapacityInKb","fwdRebuildReadBwc", "fwdRebuildWriteBwc", "bckRebuildReadBwc", "bckRebuildWriteBwc", "rebalanceReadBwc", "rebalanceWriteBwc", "numOfSdc" ]}]}
stats_url = '/api/instances/querySelectedStatistics'
stats = requests.post(base_url + stats_url, auth=(username, token), json=stat_prop, verify=False).json()

#sets variables for statistic computation
read_bw_num = int(stats["System"]["primaryReadBwc"]["numOccured"])
read_bw_sec = int(stats["System"]["primaryReadBwc"]["numSeconds"])
weight = int(stats["System"]["primaryReadBwc"]["totalWeightInKb"])

write_bw_num = int(stats["System"]["primaryWriteBwc"]["numOccured"])
write_bw_sec = int(stats["System"]["primaryWriteBwc"]["numSeconds"])
weight_write = int(stats["System"]["primaryWriteBwc"]["totalWeightInKb"])

fw_rbr_num = int(stats["System"]["fwdRebuildReadBwc"]["numOccured"])
fw_rbr_sec = int(stats["System"]["fwdRebuildReadBwc"]["numSeconds"])
fw_rbr_weight = int(stats["System"]["fwdRebuildReadBwc"]["totalWeightInKb"])

fw_rbw_num = int(stats["System"]["fwdRebuildWriteBwc"]["numOccured"])
fw_rbw_sec = int(stats["System"]["fwdRebuildWriteBwc"]["numSeconds"])
fw_rbw_weight = int(stats["System"]["fwdRebuildWriteBwc"]["totalWeightInKb"])

bw_rbr_num = int(stats["System"]["bckRebuildReadBwc"]["numOccured"])
bw_rbr_sec = int(stats["System"]["bckRebuildReadBwc"]["numSeconds"])
bw_rbr_weight = int(stats["System"]["bckRebuildReadBwc"]["totalWeightInKb"])

bw_rbw_num = int(stats["System"]["bckRebuildWriteBwc"]["numOccured"])
bw_rbw_sec = int(stats["System"]["bckRebuildWriteBwc"]["numSeconds"])
bw_rbw_weight = int(stats["System"]["bckRebuildWriteBwc"]["totalWeightInKb"])

reb_rbr_num = int(stats["System"]["rebalanceReadBwc"]["numOccured"])
reb_rbr_sec = int(stats["System"]["rebalanceReadBwc"]["numSeconds"])
reb_rbr_weight = int(stats["System"]["rebalanceReadBwc"]["totalWeightInKb"])

reb_rbw_num = int(stats["System"]["rebalanceWriteBwc"]["numOccured"])
reb_rbw_sec = int(stats["System"]["rebalanceWriteBwc"]["numSeconds"])
reb_rbw_weight = int(stats["System"]["rebalanceWriteBwc"]["totalWeightInKb"])

vol_num = stats["System"]["numOfVolumes"]
total_size = float(stats["System"]["maxCapacityInKb"]) / 1024 / 1024 / 1024

#functions to calcluate bandwidth and IOPs
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

print "Total IOPS: %s" % ((iops_calc(read_bw_num,read_bw_sec))+(iops_calc(write_bw_num,write_bw_sec)))
print "Total Bandwidth MB/s: %s" % ((bw_calc(weight, read_bw_sec ))+(bw_calc(weight_write, write_bw_sec )))
print ""
print "Read IOPS: %s" % (iops_calc(read_bw_num,read_bw_sec))
print "Write IOPS: %s" % (iops_calc(write_bw_num,write_bw_sec))
print "Read Bandwidth MB/s: %s" % (bw_calc(weight, read_bw_sec))
print "Write Bandwidth MB/s: %s" % (bw_calc(weight_write, write_bw_sec))
print ""
print "Forward Rebuild Read BW MB/s: %s" % (bw_calc(fw_rbr_weight, fw_rbr_sec))
print "Forward Rebuild Write BW MB/s: %s" % (bw_calc(fw_rbw_weight, fw_rbw_sec))
print "Backward Rebuild Read BW MB/s: %s" % (bw_calc(bw_rbr_weight, bw_rbr_sec))
print "Backward Rebuild Write BW MB/s: %s" % (bw_calc(bw_rbw_weight, bw_rbw_sec))
print "Rebalance Read BW MB/s: %s" % (bw_calc(reb_rbr_weight, reb_rbr_sec))
print "Rebalance Write BW MB/s: %s" % (bw_calc(reb_rbw_weight, reb_rbw_sec))
print ""
print "Number of Volumes: %s" % (vol_num)
print "Total Size in TB: %s" % (total_size)