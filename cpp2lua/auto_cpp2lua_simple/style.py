#!/bin/python3
# from style_tool_kits import *
import sys, os

style_name=sys.argv[1]

def cur_file_dir():
     path = sys.path[0]
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)

cmd = '{0}\\system'.format(cur_file_dir())
exec('sys.path.append(cmd)')

exec('from styles.'+style_name+' import *')

#parse_struct_list= parse_struct_list

if __name__ == '__main__':
	parse_const_include('inc_all.h')

#,const_var_string
	struct_string = parse_struct_list(struct_info_list)
	#request_info_string = parse_request_info_list_for_mc(struct_info_list)
	#print(struct_string)

	#struct_string=parse_struct_list_to_clear_type(struct_info_list)

	#marcro_string = parcel_const_var_list('request_id_list')
	#print(marcro_string)

	#print(const_var_string)

	f = open('inf.lua','w',encoding='gbk')
	#f.write(marcro_string)
	#f.write(const_var_string)
	f.write(struct_string)
	#f.write(request_info_string)
	f.close()
