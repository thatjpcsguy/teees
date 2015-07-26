#/usr/bin/env python2.7
from werkzeug._internal import _log
import sqlalchemy
import traceback
import datetime
import MySQLdb
import socket
import struct
import sys
import ast
import os

db_user = 'root'
db_pass = os.environ['MYSQL_FLASK_GUEST_PW']
db_host = 'localhost'
db_db   = 'teees'
db_port = 3306

user_table = 'users'
log_table = 'log'

# Connect to DB 
engine = sqlalchemy.engine.create_engine('mysql://%s:%s@%s/%s' % (db_user, db_pass, db_host, db_db))
engine.echo = False

# Output connection string
_log('info', 'Connected to %s on %s:%s as %s' % (db_db, db_host, db_port, db_user))

metadata = sqlalchemy.MetaData(engine)
users = sqlalchemy.Table(user_table, metadata, autoload=True)
log = sqlalchemy.Table(log_table, metadata, autoload=True)

def login(username, pw):
    try:
        if verify_pw(username, pw) is True:
            update_sql = users.update().where(users.c.username==username).values(last_login=datetime.datetime.now())
            engine.execute(update_sql)
            return True
    except Exception as E:
        _log('critical', str(E))
    return False

def verify_pw(username, pw):
    try:
        select_sql = users.select().where(users.c.username==username)
        rs = engine.execute(select_sql)
        if rs.rowcount == 1:
            stored_pw = rs.fetchone()['password']
            if stored_pw == pw:
                return True
    except Exception as E:
        _log('critical', str(E))
    return False

def user_exists(username):
    try:
        select_sql = users.select(users.c.username).where(users.c.username==username)
        rs = engine.execute(select_sql)
        if rs.rowcount != 0:
            _log('info', 'User: %s exists' % username)
            return True
        else:
            return False
    except Exception as E:
        _log('critical', str(E))
    return False

def create_user(username, password, email):
    try:
        insert_sql = users.insert().values(username=username, password=password, email=email)
        engine.execute(insert_sql)
    except IntegrityError, err:
        if err.code==1062:
            print dir(err)

    except Exception as E:
        _log('critical', str(E))
    else:
        _log('info', 'User: %s created successfully!' % username)
        return True

def ipv4_to_int(addr):
    try:
        socket.inet_aton(addr)
    except socket.error as SE:
        _log('critical', '%s (%s)' % (str(SE), addr))
    else:   
        return struct.unpack("!I", socket.inet_aton(addr))[0]

def int_to_ipv4(addr):
    try:
        socket.inet_ntoa(addr)
    except struct.error as SE:
        _log('critical', '%s (%s)' % (str(SE), addr))
    else:
        return socket.inet_ntoa(struct.pack("!I", addr))

def clean(arg):
    """Prepends slashes to \x00, \n, \r, \, ', " and \x1a. literals using MySQLdb.escape_string"""
    return MySQLdb.escape_string(arg)

def security_log(username, ip, user_agent, action_type):
    if action_type not in ['account_create', 'auth_success', 'auth_failure', 'auth_logout', 'xss', 'csrf', 'sqli']:
        _log('warning', 'Invalid action type specified: %s' % action_type)
    else:
        if action_type == 'account_create':
            _log('info', "User %s does not exist, creating user" % username)
        elif action_type == 'auth_success':
            _log('info', 'User: %s successfully authenticated (%s)' % (username, ip))
        elif action_type == 'auth_logout':
            _log('info', 'User: %s has logged out (%s)' % (username, ip))
        elif action_type == 'auth_failure':             
            _log('warning', 'Authentication failed for user: %s (%s)' % (username, ip))
        elif action_type == 'xss':
            _log('critical', 'Attempted XSS detected! (%s)' % (ip))
        elif action_type == 'csrf':
            _log('critical', 'Attempted CSRF detected! (%s)' % (ip))
        elif action_type == 'sqli':
            _log('critical', 'Attempted SQLi detected! (%s)' % (ip))

        # Convert IP address into appropriate format
        ip_int = ipv4_to_int(ip)

        try:
            insert_sql = log.insert().values(action_type=action_type, username=username, ip=ip_int, user_agent=user_agent)
            engine.execute(insert_sql)
        except Exception as E:
            print "couldn't log!"
            _log('critical', str(E))
        else: 
            _log('info', 'Logged action: %s by: %s' % (action_type, username))



