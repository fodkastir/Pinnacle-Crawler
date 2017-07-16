#-*- coding: utf-8 -*-

# Created   15 July 2017 @author: Yen Kuo

# To-Do List
# ------------- -------------
#  Added         Description
# ------------- -------------
#  15 July 2017   Nothing
# ------------- -------------
import pymysql

def get_conn(db_info):
    conn = pymysql.connect(host=db_info['HOST'],
                           port=db_info['PORT'],
                           user=db_info['USER'],
                           passwd=db_info['PASSWD'],
                           db=db_info['DB'])
    conn.set_charset('utf8')
    return conn

def init_cur(conn):
    cur = conn.cursor()
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')
    return cur
