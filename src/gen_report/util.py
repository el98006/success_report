'''
Created on Jul 14, 2016

@author: eli
'''

import cx_Oracle
import ConfigParser
import os
import logging
import datetime

map_div_to_type = {}

def str_to_date(input_str):
    mon_tr={'JAN':1,'FEB':2, 'MAR':3,'APR':4,'MAY':5,'JUN':6, 'JUL':7,'AUG':8, 'SEP':9,'OCT':10, 'NOV':11,'DEC':12}
    dd, mmm, yyyy = input_str.split('-')
    mm = int(mon_tr[mmm.upper()])
    return datetime.date(int(yyyy), mm, int(dd))
    

def load_config():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_file = os.path.join(os.path.split(src_dir)[0],'config.ini')
 
    cfg = ConfigParser.ConfigParser()
    cfg.read(cfg_file)
    UNAME = cfg.get('Database','uname')
    PASS = cfg.get('Database','passwd')
    sql = cfg.get('Database','SQL').replace('\n',' ').replace('\t',' ')
    for k, v in cfg.items('Division'):
        map_div_to_type[k] = v
    data_file_name = cfg.get('Storage', 'filename')
    return (UNAME, PASS, sql), data_file_name


def get_tx_count(db_config, start_date, end_date, div_num, success_only=True ):
    
    
    named_params = {}
    named_params['division'] =  div_num
    named_params['start_date'] = start_date
    named_params['end_date'] = end_date
    logging.debug('div: {division} from: {start_date} to: {end_date} '.format(division=div_num, start_date = start_date, end_date = end_date))
    try:
        named_params['tx_type'] = map_div_to_type[div_num]
    except KeyError:
        print 'wrong payment_division\n'
    
    uname, passwd, SQL = db_config
    

    db_con = cx_Oracle.connect(uname, passwd, 'CT')
    cur = db_con.cursor()
    if success_only :
        sql_to_run = SQL + ''' AND px.STATUS = 'SUCCESS' '''
    else:
        sql_to_run = SQL
    logging.debug('sql= {}'.format(sql_to_run))

  
    cur.execute(sql_to_run, named_params) 
    num =  cur.fetchone()[0]
    return num
    