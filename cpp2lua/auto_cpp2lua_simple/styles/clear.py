
from style_tool_kits import *

#<<<
def parse_to_clear_style(struct_info):
	
	struct_head = struct_info['struct_name_list']['use_name']

	var_lines = list()
	struct_varlist = struct_info['var_info_list']
	for var_info in struct_varlist:
		type_option = var_info['vartype']
		varlength = var_info['varlength']
		if(type_option == 'char'):
			type_option = 'value = \'\''
		else:
			if(varlength > 0):
				type_option = 'value = {' + '0,' * varlength + '}'
			else:
				type_option = 'value = 0,\t' + 'type = \'' + var_info['vartype'] + '\''

		var_line = '{ name = \'' + var_info['varname'] + '\',\tlength = ' + str(var_info['varlength']) + ',\t' + type_option + ',\t}'
		var_lines.append(var_line)

	struct_body = '\t' + ',\n\t'.join(var_lines)

	struct_string = struct_head + '={\n'\
		+ struct_body + '\n'\
		+ '}\n'

	return struct_string

def parse_target_clear_struct(struct_info):
	struct_info = resolve_struct_reference_relavant(struct_info)
	struct_string = parse_to_clear_style(struct_info)
	return struct_string

def parse_struct_list_to_clear(struct_info_list,is_local=False):
	struct_string_lines = list()
	for value in struct_info_list.values():
		struct_string = parse_target_clear_struct(value)
		struct_string_lines.append(struct_string)
	
	struct_list_string = None
	if(is_local):
		struct_list_string = 'local ' + '\n\nlocal '.join(struct_string_lines)
	else:
		struct_list_string = ',\n\n'.join(struct_string_lines)
	
	return struct_list_string

#>>>

parse_struct_list=parse_struct_list_to_clear
