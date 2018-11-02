def repl_check(current_hosts,overview_param):
    no_repl_found=[]
    titles=[]
    for element in overview_param['results'][0]['data']:
        if element[0] in current_hosts.keys() and element[1] == 'REPLICATIONROLE':
            if element[2] !='REPLICA':
                no_repl_found.append(element[0])
        else:
            issue=True
            "Message - No replica in json issues"
    if not_replicated:
        url=url_comp[schema]+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@Statistics&Parameters=[DR,0]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            url_comp[schema]='https'
            url=url_comp[schema]+"//"+url_comp['host']+":"+url_comp['port']+"/api/1.0/?Procedure=@Statistics&Parameters=[DR,0]&admin=false&User="+url_comp['userid']+"&Password="+url_comp['password']
            r = requests.get(url)
            if r.status_code != requests.codes.ok:
                sys.stderr.write("Cannot communicate with VoltDB\nExiting....")
                sys.exit(1)
            dr_param=json.loads(r.content)
            if dr_param['status']!=1:
                print "ERROR Error status indicated in VoltDB dr stats msg: ",dr_param['statustring'],'\n'
                sys.exit(0)
            
            
            
            for title in dr_param['results'][0]['schema']:
                if title['name']:
                    titles.append(title['name'])
            hostid_idx=titles.index('HOSTID')
            mode_idx=titles.index('MODE')
            for element in dr_param['results'][0]['data']:
                if element[hostid_idx] in no_repl_found and element[mode_idx] == 'NORMAL':
                    is_replicating.append(element[hostid_idx])
            if not is_replicating:
                "REPLICATION NOT STARTED ERROR"
            


            
            


   