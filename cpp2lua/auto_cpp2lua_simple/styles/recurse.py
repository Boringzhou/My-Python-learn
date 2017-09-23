
from style_tool_kits import *

def get_refered_definition(var_info):
	# return refered_packagename+var_info['refered_definition']
	return "'"+var_info['refered_definition']+"'"

def process_struct_name(struct_head):
	if(struct_head.startswith('GAME_') and struct_head.count('_')>1):
		struct_head = 'REQ_'+struct_head.lstrip('GAME_')
	return struct_head

def parse_to_tidy_recurse_style(struct_info):
	struct_head = get_struct_name(struct_info)

	struct_varlist = struct_info['var_info_list']

	length_index = 0
	var_length_lines = list()
	maxlen = str(len(struct_varlist))
	count_index=0
	# print(struct_info)
	for var_info in struct_varlist:
		explain_line=''
		varlength = var_info['varlength']
		varwidth = var_info['varwidth']
		var_length_info_line=None
		explain_line=None

		typesize=4
		if('maxsize' in var_info):
			typesize=var_info['maxsize']
		else:
			typesize=get_type_size(var_info['vartype'])
			pass

		explain_line_indent='\t'*10
		virtual_explain_line_indent='\t'*4

		to_add_bracket=True
		length_string=None

		if(varlength > 0):
			length_index = struct_varlist.index(var_info,count_index) + 1

			if(var_info['vartype'] == 'char'):
				var_length_info_line = str(varlength)
				to_add_bracket=False
			elif(var_info['vartype']=='refer'):
				length_string = 'maxlen = ' + str(varlength)
				if(varwidth != None and varwidth>0):
					length_string = ''.join((length_string ,
						', maxwidth = ' , str(varwidth)))
				length_string = ''.join((length_string , 
					', refered = ' , get_refered_definition(var_info),
					', complexType = \'link_refer\''))

				# var_length_info_line = ''.join(('{ ',length_string, ' }'))

			else:
				length_string = 'maxlen = ' + str(varlength)
				if(varwidth != None):
					length_string = ''.join((length_string ,
						', maxwidth = ' , str(varwidth),
						', complexType = \'matrix2\''))
				# var_length_info_line = ''.join(('{ ',length_string, ' }'))

			explain_line=''.join((explain_line_indent,'-- ',var_info['varname']
				,'\t: maxsize = ',str(typesize*varlength*(varwidth or 1))
				,'\t=\t',str(typesize),' * ',str(varlength),' * ',str(varwidth or 1)
					))

		else:
			if(var_info['vartype']=='refer'):
				length_index = struct_varlist.index(var_info,count_index) + 1
				length_string = ''.join((
					'refered = ' , get_refered_definition(var_info),
					', complexType = \'link_refer\''))
				# var_length_info_line = ''.join(('{ ',length_string, ' }'))
				explain_line=''.join((explain_line_indent,'-- ',var_info['varname']
					,'\t: ',virtual_explain_line_indent,'maxsize = ',str(typesize)))
			else:
				length_index = struct_varlist.index(var_info,count_index) + 1
				explain_line='-- [{}] = {}{}{}{}{}'.format(str(length_index) , var_info['varname']
					,'( ',var_info['vartype'],' )\t: maxsize = ',str(get_type_size(var_info['vartype'])))
				pass

		if(explain_line!=None):
			#make calc explain for verifying manual
			var_length_lines.append(explain_line)

		if(to_add_bracket!=None and length_string!=None):
			var_length_info_line = ''.join(('{ ',length_string, ' }'))
		if(var_length_info_line!=None):
			var_length_lines.append('[{}] = {}'.format(str(length_index) , var_length_info_line))


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

		length_index = struct_varlist.index(var_info)+1

		type_string=var_info['vartype']

		var_name_lines.append(''.join(("\t\t'",varname,"',",'\t\t-- [{}]'.format(str(length_index)),' ( {} )'.format(type_string),"\n")))
	# name_map_string = "nameMap = {\n\t\t\'" + "',\n\t\t'".join(var_name_lines) + '\'\n\t}'
	name_map_string = "nameMap = {\n" + "".join(var_name_lines) + '\t}'

	formatkey,deformatkey=generate_format_key_recursely(struct_info)

	formatkey=compress_formatkey(formatkey)
	deformatkey=compress_deformatkey(deformatkey)

	formatkey_name = 'formatKey'
	formatkeystring = formatkey_name + ' = \'<' + formatkey + '\''
	deformatkey_name = 'deformatKey'
	deformatkeystring = deformatkey_name + ' = \'<' + deformatkey + '\''

	struct_length_string_name = 'maxsize'
	struct_length=struct_info['maxsize']
	# struct_length = 0
	# letterList = re.findall('[a-zA-Z]\d*',deformatkey)
	# for letter in letterList:
	# 	struct_length = struct_length + type_key_length_map[letter[0]]
	# 	if(letter[0] == 'A'):
	# 		struct_length = struct_length + int(letter[1:])

	struct_length_string = ''.join((struct_length_string_name,' = ',str(struct_length)))

	struct_body = ',\n\t'.join((length_map_string,name_map_string,formatkeystring,deformatkeystring,struct_length_string))

	struct_body = '{\n'\
		+ struct_body + '\n'\
		+ '}'

	struct_string = process_struct_name(struct_head) + '='\
		+ struct_body

	# print(struct_string)

	return struct_string,struct_body,struct_head
	pass

def parse_target_struct(struct_info):
	struct_info = resolve_struct_reference_relavant_to_recurse_style(struct_info)
	struct_string = parse_to_tidy_recurse_style(struct_info)
	return struct_string

def parse_struct_list(struct_info_list,request_id_list_name='rid.'):
	struct_string_lines = list()
	for value in struct_info_list.values():
		struct_string,struct_body,struct_head = parse_target_struct(value)
		#struct_string='{}={}'.format(struct_head.lower(),struct_body)
		struct_string_lines.append(struct_string)

	struct_string_lines.sort()
	struct_list_string = ',\n\n'.join(struct_string_lines)
	struct_list_string = wrap_list_string(packagename,struct_list_string)
	return struct_list_string
