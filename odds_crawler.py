#-*- coding: utf-8 -*-

# Created   15 July 2017 @author: Yen Kuo

# To-Do List
# ------------- -------------
#  Added         Description
# ------------- -------------
#  15 July 2017   Nothing
# ------------- -------------

import requests
import pandas as pd
import base64
import json
import sys
from db import get_conn, init_cur
from time import gmtime, strftime, sleep

# load league ids
df = pd.read_excel('leaguesID.xlsx', sheetname='Soccer')
leagueid = str(df['leagueid'].tolist())[1:-1]

def getOdds(api_user, api_pass, sportId, leagueid, since):
    
    # switch form of url depends on if since are entered
    if since != 0:
        url = 'https://api.pinnaclesports.com/v1/odds?sportId={}&since={}&oddsFormat=Decimal&leagueIds='.format(sportId,since) + leagueid
    else:
        url = 'https://api.pinnaclesports.com/v1/odds?sportId={}&oddsFormat=Decimal&leagueIds='.format(sportId) + leagueid
    
    # get json file and convert to dict 
    b64str = "Basic " + base64.b64encode('{}:{}'.format(api_user ,api_pass).encode('utf-8')).decode('ascii')

    headers = {'Content-length' : '0',
               'Content-type' : 'application/json',
               'Authorization' : b64str,
               'UserAgent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)'}

    req = requests.get(url, headers=headers)
    data = json.loads(req.text)

    # record server time
    ctime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    
    # create result list
    result = []
    last = data['last'] 
    
    # loop over event and apppend data to result list 
    for league in data['leagues']:
        leagueid = league['id']
        for event in league['events']:
            eventid = event['id']
            for line in event['periods']:
                
                # if there is no max spread data, fill null
                # escape obs without max spread value
                if line.get('maxSpread') != None:
                    try:
                        result.append(tuple([ctime,leagueid,eventid,line['lineId'],line['number'],line['maxMoneyline'],line['maxSpread'],\
                                       line['maxTeamTotal'],line['maxTotal']]+ list(line['moneyline'].values())\
                                      + list(line['spreads'][0].values()) + list(line['totals'][0].values())))
                    except:
                        result.append(tuple([ctime,leagueid,eventid,line['lineId'],line['number'],'NULL',line['maxSpread'],'NULL',line['maxTotal']]\
                        + ['NULL', 'NULL', 'NULL'] + list(line['spreads'][0].values()) + list(line['totals'][0].values())))

    return result, last, ctime

def main (db_user, db_pass, api_user, api_pass, time_interval):
    db_info = {'HOST':'yen-wang.clcafikcugph.ap-northeast-1.rds.amazonaws.com',
       'PORT':3306,
       'USER':db_user,
       'PASSWD':db_pass,
       'DB':'pinnacle_db',}
    conn = get_conn(db_info)
    cur = init_cur(conn)
    last = 0
    while type(last) == int:
        try:
            # fetch data
            result, last, ctime = getOdds(api_user, api_pass, 29, leagueid, last)
            values = ', '.join(map(str, result)).replace("'NULL'",'NULL')
            sql = "INSERT INTO odds VALUES {}".format(values)
            cur.execute(sql)
            conn.commit()

            # print log
            print(ctime,': successfully fetch {} obs'.format(len(result)))
            sleep(int(time_interval))
        except:
            # if nothing to fetch, print log and sleep
            ctime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print(ctime,': nothing to fetch at this moment')
            sleep(int(time_interval))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('please enter db_user, db_pass, api_user, api_pass and time_interval')
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]) 