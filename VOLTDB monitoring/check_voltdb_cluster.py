#!usr/bin/python3
#main program that runs, calling memory-check module and replication-check module and finally updatesthe issues.json
import requests
import json
import sys
import pprint

from voltdb_mem_stat import mem_stat_module
from voltdb_repl_stat import replication_check

def write_json(issues):
    with open('issue.json','w') as fp:
        sys.stderr.write('a')
        json.dump(issues,fp)

issue =False
issues={}
url_comp={}
url_comp1={}
current_hosts={}
url_comp['schema']='http:'
url_comp['host']='192.168.150.17'
url_comp['port']='6013'
url_comp['userid']='admin'
url_comp['password']='flypassWORD123'
url_comp['admin']='false'
schema=url_comp['schema']
url_comp1['Procedure']='@SystemInformation'
url_comp1['Parameters']='[DEPLOYMENT]'
url_comp1['admin']='false'
url_comp1['User']='admin'
url_comp1['Password']='flypassWORD123'


sys.stderr=open('a','w')
url=url_comp['schema']+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@SystemInformation&Parameters=[DEPLOYMENT]&admin="+url_comp['admin']+"&User="+url_comp['userid']+"&Password="+url_comp['password']
try :
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        url_comp['schema']='https'
        url=url_comp['schema']+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@SystemInformation&Parameters=[DEPLOYMENT]&admin="+url_comp['admin']+"&User="+url_comp['userid']+"&Password="+url_comp['password']
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            raise Exception
except:
    sys.stderr.write("Cannot communicate with VoltDB\nExiting....")
    issues['ERROR']='Cluster Check: Cannot communicate with VoltDB, VoltDB down or network error'
    write_json(issues)
    sys.exit(1) 

deployment_param=json.loads(r.content)
if deployment_param['status']!=1:
    sys.stderr.write("Error status indicated in VoltDB deployment info msg: ",deployment_param['statusstring'],"\nExiting...") 
    issues['ERROR']='Error status indicated in VoltDB deployment info msg: '+deployment_param['statusstring'] 
    write_json(issues)
    sys.exit(1) 
    
expexcted_host_num=int(deployment_param['results'][0]['data'][1][1])
# print "Hello"
# print expexcted_host_num
url=url_comp['schema']+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@SystemInformation&Parameters=[\"OVERVIEW\"]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
r = requests.get(url)

overview_param=json.loads(r.content)
if overview_param['status']!=1:
    sys.stderr.write("Error status indicated in VoltDB overview info msg: "+overview_param['statusstring']+"\nExiting...") 
    issues['ERROR']="Error status indicated in VoltDB overview info msg: "+overview_param['statusstring']
    write_json(issues)
    sys.exit(1) 

current_host_num=0
for element in overview_param['results'][0]['data']:
    if element[1]=='HOSTNAME':
        current_hosts[element[0]]=element[2]
        current_host_num+=1
hosts_down=expexcted_host_num-current_host_num
#print "Current hosts",current_hosts
if hosts_down:
    # print "Critical: ",hosts_down," host(s) are down"
    issue=True
    issues['Nodes down']=hosts_down
    sys.stderr.write(str(hosts_down))

# print current_hosts
comp='memory'
issues=mem_stat_module(url_comp,issues)
issues=replication_check(url_comp,issues,current_hosts,overview_param)
# pprint.pprint(issues) 
write_json(issues)







  




