# -*- coding: utf-8 -*-
import xmlrpclib
import os
import csv

url = 'http://%s/xmlrpc' % connect['url']
sock_obj = xmlrpclib.ServerProxy(url+'/object')
sock_connect = xmlrpclib.ServerProxy(url+'/common')

admin_login = connect['admin_login']
admin_passwd = connect['admin_passwd']
dbname = connect['dbname']

uid = sock_connect.login(dbname, admin_login, admin_passwd)
print "UID : " + str(uid)

modules = sock_obj.execute(dbname,uid,admin_passwd, 'ir.module.module', 'search_read', [('state','=','installed')], ['name'])
installed_ids = [x['id'] for x in modules]
print len(installed_ids)
modules_by_name = [(x['id'],x['name']) for x in modules]
print 'before'
print modules_by_name
modules_by_name = sorted(modules_by_name,key=lambda x: x[1])
print 'after'
print modules_by_name
dModules = {}
for module in modules:
    dModules[module['id']] = {'name':module['name'],'id':module['id'],'column':1}
depends = sock_obj.execute(dbname,uid,admin_passwd, 'ir.module.module.dependency', 'search_read', [('module_id','in',installed_ids)], ['module_id','depend_id'] )
print len(depends)
corrections = 9999
nested = 1
while corrections > 0:
    corrections = 0
    nested += 1
    for dep in depends:
        if dep['module_id'] and dep['depend_id']:
            if dModules.has_key(dep['module_id'][0]) and dModules.has_key(dep['depend_id'][0]):
                if dModules[dep['module_id'][0]]['column'] <= dModules[dep['depend_id'][0]]['column']:
                    corrections += 1
                    dModules[dep['module_id'][0]]['column'] = dModules[dep['depend_id'][0]]['column'] + 1
        else:
            print 'strange %s depends of %s' + (str(dep['module_id']),str(dep['depend_id']))
#print dModules
maxcol = 0
for module in dModules.values():
    if module['column'] > maxcol:
        maxcol = module['column']
print maxcol
f_out = csv.writer(open('modules_in_columns.csv','w'),delimiter=";")
index = 1
titles = []
while index <= maxcol:
    titles.append(str(index))
    index += 1
f_out.writerow(titles)
for (key,module_name) in modules_by_name:
    module = dModules[key]
    columns = ['']*maxcol
    columns[module['column']-1] = '#'+dModules[module['id']]['name']+'#'  ## the name og the current module is writtent between # to help to find it out
    for dep in depends:
        if dep['module_id'][0] == module['id']:
            parent_name = dModules.has_key(dep['depend_id'][0]) and dModules[dep['depend_id'][0]]['name'] or 'module name unknown '+str(dep['depend_id'][0])
            parent_column = dModules.has_key(dep['depend_id'][0]) and dModules[dep['depend_id'][0]]['column']-1 or 1
            #print 'parent name'
            #print parent_name
            #print 'parent_column'
            #print parent_column
            if columns[parent_column]:
                if columns[parent_column][0] == '-':
                    columns[parent_column] += '\n- ' + parent_name
                else:
                    columns[parent_column] = '- ' + columns[parent_column] + '\n- ' + parent_name
            else:
                columns[parent_column] = parent_name
            print columns
    #print module['name']
    #print module['column']
    #print columns
    #inputs = raw_input('press')
    f_out.writerow(columns)


