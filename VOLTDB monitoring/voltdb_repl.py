from collections import defaultdict
from time import time
import sys
import requests
import json

critLimit = 16*1024*1024 # evaluated PER PARTITION
warnLimit = 4*1024*1024 # evaluated PER PARTITION
critTimeLimit = 120 # min in sec time since last DR agent ACK to alarm
critTimeBufferLimit = 200*1024


def replication_check(url_comp,issues,current_hosts,overview_param):
    no_repl_found=[]
    titles=[]
    # print 'mm'
    for element in overview_param['results'][0]['data']:
        if element[0] in current_hosts.keys() and element[1] == 'REPLICATIONROLE':   #check in overview param if node is in replication mode
            if element[2] !='REPLICA':
                
                no_repl_found.append(element[0])
        else:
            # print 'NO'
            issue=True
            issues['ERROR']="Replication Module:Failed to get replication role"
            
            break
            
    if no_repl_found:
        url=url_comp['schema']+"//"+url_comp['host']+":"+url_comp['port']+\
        "/api/1.0/?Procedure=@Statistics&Parameters=[DR,0]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            url_comp['schema']='https'
            url=url_comp['schema']+"//"+url_comp['host']+":"+url_comp['port']+\
            "/api/1.0/?Procedure=@Statistics&Parameters=[DR,0]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
            r = requests.get(url)
            if r.status_code != requests.codes.ok:
                issue=True
                issues['ERROR']="Replication Module:Cannot communicate with VoltDB"
                sys.stderr.write("Cannot communicate with VoltDB\nExiting....")
                return issues  #ERROR
        dr_param=json.loads(r.content)
        if dr_param['status']!=1:
            sys.stderr.write("ERROR Error status indicated in VoltDB dr stats msg: "+dr_param['statustring']+'\n')
            issues['ERROR']="Replication Module:status indicated in VoltDB dr stats msg: "+dr_param['statustring']
            return issues
        
        
        
        for title in dr_param['results'][0]['schema']:
            if title['name']:
                titles.append(title['name'])   #title of table 
        hostid_idx=titles.index('HOSTID')
        mode_idx=titles.index('MODE')
        rows_of_nodes=defaultdict(list)
        is_replicating=[]
        

        for element in dr_param['results'][0]['data']:
            element_to_dict={}
            for i in range(0,len(titles)):
                element_to_dict[titles[i]]=element[i]
                rows_of_nodes[element[hostid_idx]].append(element_to_dict)
            if element[hostid_idx] in no_repl_found and element[mode_idx] == 'NORMAL':
                is_replicating.append(element[hostid_idx])
        if not is_replicating:
            issue=True
            issues['ERROR']="Replication Module:Replication not started"
            return issues
            #"REPLICATION NOT STARTED ERROR"
        #REPLICATION OF PARTIOTION BEING CHECKED FOR NODES
        list_a=[],list_b=[],list_unreplicated_partition=[]
        for x in rows_of_nodes:
            for param_x in x:
                list_a.append(param_x['PARTITIONID'])
                if not param_x['ISSYNCED']:
                    issue=True
                    issues['ERROR']="Replication Module:VoltDB Replication CRITICAL - replication failure"
                    return issues
                    #NOT SYNCED PROPERLY "VoltDB Replication CRITICAL - replication failure\n" 
            list_b=list_a
            for y in rows_of_nodes:
                if y != x:
                    for param_y in y:
                        if param_y['PARTITIONID'] in list_a:
                            list_b.remove(param_y['PARTITIONID'])
            list_unreplicated_partition.append(list_b)
        if list_unreplicated_partition:
            issue=True
            issues['ERROR']="Replication Module:CRITICAL - Detected partition(s) not replicating"
            return issues        
            sys.exit(1)   #Partitions not correctly replicated  "VoltDB Replication CRITICAL - Detected partition(s) not replicating
        
        
        critPartCount=0
        totalBytes=0 
        totalBytesInMemory=0
        isSpilling=0
        strSpilling=""
        currdt = time() # get current dt/time in UTC epoch in secs
        tdiff=0
        maxtdiff=0


        for x in rows_of_nodes:
            nparts=0
            for param_x in x:
                tdiff = currdt - param_x['LASTACKTIMESTAMP']/1000000
                if (tdiff < -3):
                    issue=True
                    issues['ERROR']="Replication Module:Possible clock skew detected between monitor and host, cannot compute time offset"
                    return issues
                if ((tdiff > critTimeLimit and  param_x['TOTALBYTES'] > critTimeBufferLimit) or (param_x['TOTALBYTES'] > critLimit)):
                    critPartCount+=1
                    if (tdiff > maxtdiff):
                        maxtdiff = tdiff
                totalBytes +=  param_x['TOTALBYTES']
                totalBytesInMemory +=  param_x['TOTALBYTESINMEMORY']
                if ( param_x['TOTALBYTES'] -  param_x['TOTALBYTESINMEMORY']):
                    isSpilling+=1
                nparts+=1
            if (isSpilling):
                strSpilling = ", "+isSpilling+" node(s) Spilling to disk"
            if (critPartCount):
                issue=True
                issues['ERROR']="Replication Module:CRITICAL - over backlog limit by "+((totalBytes)/(critLimit*nparts)*100)+'%'+\
                totalBytes+" bytes queued"+strSpilling+" and Replication agent not heard from for "+maxtdiff+"secs.\n"
                #critical alarm


            # Always warn if any node is spilling.
            if (isSpilling): 
                sys.stderr.write("VoltDB Replication WARNING - Backlog spilling to disk, "+totalBytes+" bytes queued.\n")
                # this is a warning alarm
            
            sys.stderr.write("VoltDB Replication OK - bytes queued: "+totalBytes+strSpilling+"\n")
    # print issues
    return issues
    
    


    


                        
                



            
        

        #"Check @allrows and rows"
       # "first iterates over every node and compares with all other nodes in clster"
        


            
            


   