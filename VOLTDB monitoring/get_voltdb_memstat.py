import requests
import json
import sys
import pprint

# schema='http:'
# host='192.168.14.21'
# port='6013'
# userid='admin'
# password='bullet'
# admin='false'
# issues={}

delta='1'
titles=[]

mem_critical_p=90


def mem_stat_module(url_comp,issues,comp):
    schema=url_comp['schema']
    url=schema+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@Statistics&Parameters=["+comp+","+delta+"]&admin="+url_comp['admin']+"&User="+url_comp['userid']+"&Password="+url_comp['password']
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        schema='https'
        url=schema+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@Statistics&Parameters=["+comp+","+delta+"]&admin="+url_comp['admin']+"&User="+url_comp['userid']+"&Password="+url_comp['password']
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            print "Cannot communicate with VoltDB\nExiting...."
            sys.exit(1)
    stat_param=json.loads(r.content)
    if stat_param['statusstring']:
        print stat_param['statusstring']
        sys.exit(1)
    #pprint.pprint(stat_param)

    phymem=0
    rss=0
    
    for title in stat_param['results'][0]['schema']:
        if title['name']:
            titles.append(title['name'])
            
    if 'RSS' and 'PHYSICALMEMORY' in titles:
        for node in stat_param['results'][0]['data']:
            for i in range (0,len(titles)-1):
                #print titles[i],'\t',node[i]
                if titles[i]=='RSS':
                    rss+=node[i]
                elif titles[i]=='PHYSICALMEMORY':
                    phymem+=node[i]
            # print '\n'
    else:
        sys.stderr.write("RSS or PHYSICALMEMORY field not present") 
            
    memused_p=rss/phymem*100 #percent of mem used
    memused=rss/1024  #in MB
    if memused_p>mem_critical_p:
        issue=True
        issues['Memory usage critical']=memused_p
    # else:
    #     print 'Happy'
    return issues

   
    
    


