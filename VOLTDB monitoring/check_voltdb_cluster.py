#!usr/bin/python3

import requests
import json
import sys
import pprint

from get_voltdb_stat import mem_stat_module

issue =False
issues={}
url_comp={}
current_hosts={}
url_comp['schema']='http:'
url_comp['host']='192.168.14.21'
url_comp['port']='6013'
url_comp['userid']='admin'
url_comp['password']='bullet'
url_comp['admin']='false'
schema=url_comp['schema']

sys.stderr=open('a','w')
url=schema+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@SystemInformation&Parameters=[DEPLOYMENT]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
r = requests.get(url)
if r.status_code != requests.codes.ok:
    schema='https'
    url=schema+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@SystemInformation&Parameters=[DEPLOYMENT]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        sys.stderr.write("Cannot communicate with VoltDB\nExiting....")
        sys.exit(1)

deployment_param=json.loads(r.content)
if deployment_param['status']!=1:
    sys.stderr.write("Error status indicated in VoltDB deployment info msg: ",deployment_param['statusstring'],"\nExiting...") 
    sys.exit(1)
expexcted_host_num=int(deployment_param['results'][0]['data'][1][1])
# print "Hello"
# print expexcted_host_num
url=schema+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@SystemInformation&Parameters=[\"OVERVIEW\"]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
r = requests.get(url)

overview_param=json.loads(r.content)
if overview_param['status']!=1:
    sys.stderr.write("Error status indicated in VoltDB overview info msg: ",overview_param['statusstring'],"\nExiting...") 
    sys.exit(1)
current_host_num=0
for element in overview_param['results'][0]['data']:
    if element[1]=='HOSTNAME':
        current_hosts[element[0]]=element[2]
        current_host_num+=1
hosts_down=expexcted_host_num-current_host_num
print "Current hosts",current_host_num
if hosts_down:
    # print "Critical: ",hosts_down," host(s) are down"
    issue=True
    issues['Nodes down']=hosts_down


comp='memory'
mem_stat_module(url_comp,issues,comp)

with open('issue.json','w') as fp:
    json.dump(issues,fp)






  




