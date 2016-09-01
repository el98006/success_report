'''
Created on Jul 14, 2016

@author: eli
'''

import cx_Oracle
import ConfigParser
import os





def load_config():
    sql= []
    src_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_file = os.path.join(os.path.split(src_dir)[0],'config.ini')
 
    cfg = ConfigParser.ConfigParser()
    cfg.read(cfg_file)
    UNAME = cfg.get('Database','uname')
    PASS = cfg.get('Database','passwd')
    sql.append(cfg.get('Database','SQL').replace('\n',' ').replace('\t',' '))
    return UNAME, PASS, sql


def get_tx_count(db_config, start_date, end_date, div_num, success_only=True ):
    
    
    named_params = {}
    named_params['division'] =  div_num
    named_params['start_date'] = start_date
    named_params['end_date'] = end_date
    try:
        named_params['tx_type'] = map_div_to_type[div_num]
    except KeyError:
        print 'wrong payment_division\n'
    
    uname, passwd, SQL = db_config
    db_con = cx_Oracle.connect(uname, passwd, 'CT')
    cur = db_con.cursor()
    if success_only :
        sql_to_run = SQL[0] + ''' AND px.STATUS='SUCCESS' '''
 
    cur.execute(sql_to_run, named_params)
    num =  cur.fetchone()[0]
    return num
    