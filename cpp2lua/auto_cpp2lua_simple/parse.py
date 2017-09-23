'''
Created on 2015.04.07

@author: windy
'''

import re
from copy import deepcopy

o_proc_const_def = \
	{
		'marcro_name':'',
		'marcro_body':'',
	}

o_var_info = \
	{
		'varname': '',
		'typename': '',
		'length': 0,
	}

o_struct_info = \
	{
		'struct_name_list': {'org_name': '', 'use_name': ''},
		'var_info_list': list(),
	}

o_const_ifelse_state_stack = list()

#<<< init const def map
atom_def_list = ['int',
	'unsigned long',
	#'string',
	'long',
	'unsigned int',
	'float',
	'double',
	'char',
	'byte',
	'unsigned char',
	'short',
	'unsigned short',
	'long long',]

const_def_map = dict()

for ele in atom_def_list:
	const_def_map[ele] = ele

def my_assert(con,tip):
	assert con,tip
	pass
	
def proc_typedef_inline(line,def_info):
	match = re.match('\s*typedef\s+(?P<type_body>[\w\s]+)\s+(?P<type_name>\w+)\s*;',line)
	if(match):
		type_body = match.group('type_body').rstrip()
		type_name = match.group('type_name').strip()

		def_info['marcro_name'] = type_name
		def_info['marcro_body'] = type_body
		return True
	else:
		return False
	pass

def proc_const_def(line, def_info):
	match = re.match('\s*#define\s+(?P<marcro_name>\w+)\s+(?P<marcro_body>[^/][^/]+)?\s*(//)?', line)
	if(match):
		def_info['marcro_name'] = match.group('marcro_name')
		my_assert(match.group('marcro_body') != '','')
		marcro_body = match.group('marcro_body') or '1'
		def_info['marcro_body'] = marcro_body.rstrip()
		return True
	else:
		return False

def parse_const_def(def_info):
	body = def_info['marcro_body']
	name = def_info['marcro_name']
	if(name == 'MSG_GREETING'):
		print('')
	value = None
	try:
		value = eval(body)
		value = (type(value) != type and value) or None
	except:
		pass

	if(value == None):
		match = re.match('\s*\(\s*(?P<base_num>\w+)\s*\+\s*(?P<offset_num>\d+)\s*\)',body)
		if(match):
			base_num = const_def_map[match.group('base_num')]
			if(type(base_num) == str):
				base_num = eval(base_num)
			offset_num = match.group('offset_num')
			value = eval(offset_num) + base_num

	#my_assert(value!=None,'')
	if(value == None):
		value = body

	if(value != None):
		const_def_map[name] = value

#>>>
def proc_struct_def_head(line, struct_info):
	match = re.match('\s*typedef\s+struct\s+(?P<struct_name>\w+)', line)
	if(match):
		struct_info['struct_name_list']['org_name'] = match.group('struct_name')
		return True
	else:
		return False


def proc_struct_def_end(line, struct_info):
	match = re.match('\s*}\s*(?P<struct_name>\w+)\s*,', line)
	if(match):
		struct_info['struct_name_list']['use_name'] = match.group('struct_name')
		return True
	else:
		return False
	pass


def proc_struct_var(line, struct_info):
	var_info_list = struct_info['var_info_list']
	match = re.match('\s*(?P<vartype>[\w\s]+)\s+(?P<varname>\w+)\s*((\[\s*(?P<varwidth>.+)\s*\])?(\[\s*(?P<varlength>[^\]]+)\s*\]))?\s*;', line)
	if(match):
		var_info = {
			'vartype': match.group('vartype').strip(),
			'varname': match.group('varname'),
			'varlength': match.group('varlength'),
			'varwidth':match.group('varwidth'),
		}
		var_info_list.append(var_info)
		return True
	else:
		return False
	pass

def parse_enum_def_list(content):
	pass

def proc_explain_line(line):
	if(re.match('\s*//', line) or re.match('\s*$',line)):
		return True
	else:
		return False

def proc_pragma_line(line):
	if(re.match('\s*#pragma\s+',line)):
		return True
	else:
		return False

const_ifelse_state_stack = o_const_ifelse_state_stack

def proc_const_ifelse(line):
	
	def get_current_ifelse_state():
		if(len(const_ifelse_state_stack) <= 0):
			return True
		return const_ifelse_state_stack[len(const_ifelse_state_stack) - 1]
	
	if(re.match('\s*#endif\s*$',line)):
		const_ifelse_state_stack.pop()

	# skip elif
	elif(re.match('\s*#else\s*$',line)):
		state = const_ifelse_state_stack.pop()
		const_ifelse_state_stack.append(not state)
		return 'skip'

	if(get_current_ifelse_state() == False):
		return 'skip'

	match = re.match('\s*#ifndef\s+(?P<marcro_body>\w+)\s*$',line)
	if(match):
		marcro_body = match.group('marcro_body')
		marcro_value = False

		if(marcro_body in const_def_map):
			marcro_value = const_def_map[marcro_body]
			
		if(marcro_value and marcro_value != 0 and marcro_value != False):
			const_ifelse_state_stack.append(not True)
		else:
			const_ifelse_state_stack.append(not False)

		return 'skip'
	
	if(get_current_ifelse_state() == False):
		return 'skip'
	else:
		return 'keep'

const_include_file_list = dict()
def proc_const_include(line):
	match = re.match('^\s*#\s*include\s+[\'\"\<](?P<filename>[\w\.]+)[\'\"\>]',line)
	if(match):
		filename = match.group('filename')
		return filename

	return None
	pass

def parse_const_include(filename):

	if(filename in const_include_file_list):
		const_include_file_list[filename]
		return
	else:
		const_include_file_list[filename] = True

	f = open(filename,'r',encoding='gbk')
	print('parsing ' + filename)
	parse_content(f)
	f.close()

	pass

def parse_length_info(length_string):
	length_name = length_string or '0'
	length = (type(length_name) == int and length_name) or None

	#if(item['varname']=='szHashPwd'):
		#print('lj')

	offset = 0
	if(length == None):
		match = re.match('(?P<length>\w+)\+(?P<offset>\d+)',length_name)
		if(match):
			length_name = match.group('length')
			offset = eval(match.group('offset'))

	if(length == None):
		try:
			length = eval(length_name)
		except:
			length = const_def_map[length_name]
			pass
		length = length + offset
	else:
		pass

	my_assert(length != None,'')
	return length
	pass

def parse_varlist(varlist):
	for item in varlist:
		typename = ''
		try:
			typename = const_def_map[item['vartype']]
			item['vartype'] = typename
		except:
			typename = item['vartype']
			item['refername'] = typename
			item['vartype'] = 'refer'
			item['varname'] = item['varname']

		varlength=parse_length_info(item['varlength'])
		# if(item['vartype'] == 'refer' and varlength==0):
		# 	varlength=1
		item['varlength']=varlength

		if(item['varwidth']):
			item['varwidth']=parse_length_info(item['varwidth'])
		
	pass

def parse_struct(struct_info):
	parse_varlist(struct_info['var_info_list'])
	pass

struct_info_list = dict()

var_static_env = {
	'const_type_def':const_def_map,
	'struct_type_def':struct_info_list,
	'atom_def_list':atom_def_list,
	}

def parse_content(f):
	struct_info = deepcopy(o_struct_info)
	
	if(f):
		state = 'head'  # or 'body' 'end'
		for line in f:
			#print('current line : '+line)

			if(proc_explain_line(line)):
				continue

			if(proc_const_ifelse(line) == 'skip'):
				continue

			if(proc_pragma_line(line)):
				continue

			const_include_filename = proc_const_include(line)
			if(const_include_filename):
				my_assert(state == 'head','')
				parse_const_include(const_include_filename)
				continue

			def_info = {}
			if(proc_const_def(line, def_info)):
				parse_const_def(def_info)
				continue

			if(proc_typedef_inline(line,def_info)):
				parse_const_def(def_info)
				continue

			#for struct
			if(state == 'head'):
				if(proc_struct_def_head(line, struct_info)):
					state = 'body'
			elif(state == 'body'):
				if(proc_struct_var(line, struct_info) == False):
					if(proc_struct_def_end(line, struct_info)):
						state = 'end'

			if(state == 'end'):
				parse_struct(struct_info)
				struct_name = struct_info['struct_name_list']['use_name']
				struct_info_list[struct_name] = struct_info 
				struct_info = deepcopy(o_struct_info)
				state = 'head'
			pass

		if(parse_enum_def_list(f.read())):
			pass

	pass

if __name__ == '__main__':

	# f = open ( 'PREDEF_MARCROS.h' )
	# parse_content ( f )
	# f.close ( )

	# f = open ( 'MobileDef.h' )
	# parse_content ( f )
	# f.close ( )

	# f = open ( 'MobileReq.h' )
	# parse_content ( f )
	# f.close ( )

	parse_const_include('inc_all.h')

	#dump(var_static_env)
