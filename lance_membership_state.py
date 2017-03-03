# -*- coding: utf-8 -*-
import xmlrpclib
import os
import csv
import sys

execfile('params.txt')

url = 'http://%s/xmlrpc' % connect['url']
sock_obj = xmlrpclib.ServerProxy(url+'/object')
sock_connect = xmlrpclib.ServerProxy(url+'/common')

admin_login = connect['admin_login']
admin_passwd = connect['admin_passwd']
dbname = connect['dbname']

uid = sock_connect.login(dbname, admin_login, admin_passwd)
print "UID : " + str(uid)

print sock_obj.execute(dbname,uid,admin_passwd, 'res.partner', 'check_membership_state_job')

