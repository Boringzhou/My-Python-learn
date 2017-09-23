
from style_tool_kits import *

def process_struct_name(struct_head):
	if(struct_head[len(struct_head) - 3:] == '_MB'):
		struct_head = struct_head[0:len(struct_head) - 3]
	return struct_head

def parse_to_tidy_style(struct_info):
	struct_head = struct_info['struct_name_list']['use_name']

	struct_varlist = struct_info['var_info_list']

	length_index = 0
	var_length_lines = list()
	maxlen = str(len(struct_varlist))
	count_index=0
	for var_info in struct_varlist:
		varlength = var_info['varlength']
		varwidth = var_info['varwidth']
		if(varlength > 0):
			length_index = struct_varlist.index(var_info,count_index) + 1
			var_length_info_line = None
			if(var_info['vartype'] == 'char'):
				var_length_info_line = str(varlength)
			else:
				length_string = 'maxlen = ' + str(varlength)
				if(varwidth != None):
					length_string = length_string + ',maxwidth = ' + str(varwidth)
					length_string = length_string + ',complexType = \'matrix2\''
				var_length_info_line = ''.join(('{',length_string, '}'))

			var_length_lines.append('[{}] = {}'.format(str(length_index) , var_length_info_line))

		else:
			pass
		count_index=count_index+1

	if(len(var_length_lines) == 0):
		var_length_lines = ['--']
	length_map_string = '\tlengthMap = {\n\t\t' + ',\n\t\t'.join(var_length_lines) + (',\n\t\tmaxlen = {}'.format(maxlen)) + '\n\t}'

	# parse name list
	var_name_lines = list()
	var_name_conflict_resolve_space = dict()
	for var_info in struct_varlist:
		varname = var_info['varname']
		try:
			suffix = var_name_conflict_resolve_space[varname]
			tvarname = varname + str(suffix)
			var_name_conflict_resolve_space[varname] = suffix + 1
			varname=tvarname
		except:
			var_name_conflict_resolve_space[varname] = 1
			pass

		var_name_lines.append(varname)
	name_map_string = "nameMap = {\n\t\t\'" + "',\n\t\t'".join(var_name_lines) + '\'\n\t}'

	formatkey_name = 'formatKey'
	keylist = list()
	formatkeystring = None
	for var_info in struct_varlist:
		vartype = var_info['vartype']
		varlength = var_info['varlength']
		varwidth = var_info['varwidth']
		if(varlength > 1):
			if(vartype == 'char'):
				vartype = 'string'
		typekey = type_key_exch_map[vartype]
		if(varlength > 1):
			if(vartype != 'string'):
				typekey = typekey * varlength * (varwidth or 1)
		keylist.append(typekey)
	formatkey = '<' + ''.join(keylist)
	formatkeystring = formatkey_name + ' = \'' + formatkey + '\''
	
	deformatkey_name = 'deformatKey'
	keylist = list()
	deformatkeystring = None
	for var_info in struct_varlist:
		vartype = var_info['vartype']
		varlength = var_info['varlength']
		varwidth = var_info['varwidth']
		if(vartype == 'char' and varlength > 1):
			vartype = 'string'
		typekey = type_key_exch_map[vartype]
		if(varlength > 1):
			if(vartype != 'string'):
				typekey = typekey * varlength * (varwidth or 1)
		if(typekey == 'A'):
			typekey = typekey + str(var_info['varlength'])
		keylist.append(typekey)
	deformatkey = '<' + ''.join(keylist)
	deformatkeystring = deformatkey_name + ' = \'' + deformatkey + '\''

	print(deformatkeystring)
	struct_length_string_name = 'maxsize'
	struct_length = 0
	letterList = re.findall('[a-zA-Z]\d*',deformatkey)
	for letter in letterList:
		struct_length = struct_length + type_key_length_map[letter[0]]
		if(letter[0] == 'A'):
			struct_length = struct_length + int(letter[1:])

	print(struct_length)
	struct_length_string = ''.join((struct_length_string_name,' = ',str(struct_length)))

	struct_body = ',\n\t'.join((length_map_string,name_map_string,formatkeystring,deformatkeystring,struct_length_string))

	print(struct_body)
	
	struct_body = '{\n'\
		+ struct_body + '\n'\
		+ '}'

	struct_string = process_struct_name(struct_head) + '='\
		+ struct_body

	return struct_string,struct_body,struct_head
	pass

def parse_target_struct(struct_info):
	struct_info = resolve_struct_reference_relavant(struct_info)
	struct_string,_,_ = parse_to_tidy_style(struct_info)
	return struct_string

def parse_target_struct_debug(struct_info):
	struct_string = parse_to_clear_style(struct_info)
	pass

def parse_target_struct_by_name(struct_info_list,struct_name):
	struct_info = struct_info_list[struct_name]
	return parse_target_struct(struct_info)

def parse_struct_list(struct_info_list,is_local=False):
	struct_string_lines = list()
	for value in struct_info_list.values():
		struct_string = parse_target_struct(value)
		struct_string_lines.append(struct_string)
	
	struct_list_string = None
	if(is_local):
		struct_list_string = 'local ' + '\n\nlocal '.join(struct_string_lines)
	else:
		struct_list_string = ',\n\n'.join(struct_string_lines)
	
	return struct_list_string

def find_request_id_by_struct_head(struct_head):

	name_proc_list = [lambda name:'MR_' + name,
		lambda name:'GR_' + name,
		lambda name:'MR_' + name.replace('GET_','GET_TEMP',1),
		lambda name:'GR_' + name.replace('GET_','GET_TEMP',1),
		lambda name:'MR_' + name + 'ED',
		lambda name:'MR_' + name + 'ED',
		lambda name:'GR_' + name + 'ED',
		lambda name:'MR_' + name.replace('_MB','',1),
		lambda name:'GR_' + name.replace('_MB','',1),
		lambda name:'MR_' + name.replace('_MB','',1) + 'ED',
		lambda name:'GR_' + name.replace('_MB','',1) + 'ED',]

	request_id = None
	request_name = None
	for name_proc in name_proc_list:
		request_name = name_proc(struct_head)
		try:
			request_id = const_type_def[request_name]
			break
		except:
			continue

	return request_id,request_id and request_name

def parse_struct_list_for_mc(struct_info_list,request_id_list_name='rid.'):
	struct_string_lines = list()
	for value in struct_info_list.values():
		struct_string,struct_body,struct_head = parse_target_struct(value)
		#struct_string='{}={}'.format(struct_head.lower(),struct_body)
		struct_string_lines.append(struct_string)

	struct_string_lines.sort()
	struct_list_string = ',\n\n'.join(struct_string_lines)
	struct_list_string = wrap_list_string('RequestInfoList',struct_list_string)
	return struct_list_string
