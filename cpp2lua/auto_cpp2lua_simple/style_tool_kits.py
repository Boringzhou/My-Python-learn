
import re
from copy import copy

from parse import parse_const_include,parse_content,var_static_env,my_assert

struct_info_list = var_static_env['struct_type_def']
const_type_def = var_static_env['const_type_def']
atom_def_list = var_static_env['atom_def_list']

type_key_exch_map = {
	'int':'i',
	'unsigned long':'L',
	'string':'A',
	'long':'l',
	'unsigned int':'I',
	'float':'f',
	'double':'d',
	'long long':'d',
	'lua number':'n',
	'char':'c',
	'byte':'b',
	'unsigned char':'b',
	'short':'h',
	'unsigned short':'H',
	'little endian':'<',
	'big endian':'>',
	'native endian':'=',
	'zero limit string':'z',
	'blength limit string':'a',
	'wlength limit string':'p',
	'slength limit string':'P',
}

type_key_length_map = {
	'i':4,
	'L':4,
	'f':4,
	'c':1,
	'b':1,
	'h':2,
	'l':4,
	'I':4,
	'H':2,
	'd':8,
	'<':0,
	'>':0,
	'=':0,
	'A':0,
}

packagename='RequestInfoList'
refered_packagename=''

def get_type_size(typename):
	my_assert(typename in type_key_exch_map,'')
	return type_key_length_map[type_key_exch_map[typename]]

def adjust_struct_indent_in_string(struct_body_string,add_size=1):
	struct_body_string_indented = struct_body_string.replace('\n','\n' + '\t' * add_size)
	return struct_body_string_indented
	pass

def wrap_list_string(head,list_string):
	return ''.join([head,' = {\n\t',adjust_struct_indent_in_string(list_string),'\n}'])

def get_struct_name(struct_info):
	return struct_info['struct_name_list']['use_name']
	
def register_struct(space,struct_info):
	space[get_struct_name(struct_info)]=struct_info
	pass

def struct_registed(space,struct_info):
	name=get_struct_name(struct_info)
	if(name in space):
		return space[name]
	else:
		return None

def _compress_formatkey(formatkey,compress_keyset):
	keyset='[iLfcbhlIHdA<=>]'
	keyiter=re.finditer('(?P<key>'+keyset+')(?P<sum>\d*)?',formatkey)
	lastsum=0
	lastkey=''
	keyslice_list=[]
	for key in keyiter:
		rawkey=key.group('key')
		tsum=key.group('sum')
		if(tsum==''):
			tsum='1'
		tsum=int(tsum)
		if(lastkey!=rawkey or rawkey not in compress_keyset):
			keyslice_list.append(lastkey+(lastsum>1 and str(lastsum) or ''))
			lastsum=tsum
			lastkey=rawkey
		else:
			lastsum=lastsum+tsum

	keyslice_list.append(lastkey+(lastsum>1 and str(lastsum) or ''))

	new_formatkey=''.join(keyslice_list)

	return new_formatkey

	pass

def compress_formatkey(formatkey):
	keyset='[iLfcbhlIHdA]'
	return _compress_formatkey(formatkey,keyset)

def compress_deformatkey(deformatkey):
	keyset='[iLfhlIHd]'
	return _compress_formatkey(deformatkey,keyset)

def trans_deformatkey_to_formatkey(deformatkey):
	return re.sub('[AabczpP]\d*','A',deformatkey)

def _generate_format_key_recursely(struct_info):
	keylist = list()
	deformatkey = None
	struct_varlist=struct_info['var_info_list']
	for var_info in struct_varlist:
		vartype = var_info['vartype']
		varlength = var_info['varlength']
		varwidth = var_info['varwidth']
		typekey=''
		if(varlength > 1):
			if(vartype == 'char'):
				vartype = 'string'
		if(vartype in type_key_exch_map):
			typekey = type_key_exch_map[vartype]

		if(vartype=='refer'):
			refername=var_info['refername']
			refered_struct=struct_info_list[refername]
			sub_format_key,sub_deformat_key=_generate_format_key_recursely(refered_struct)
			totolsize=(varlength or 1) * (varwidth or 1)
			typekey = sub_deformat_key*totolsize
		elif(varlength > 1):
			typekey = typekey+str(varlength * (varwidth or 1))
		keylist.append(typekey)

	deformatkey=''.join(keylist)
	formatkey=trans_deformatkey_to_formatkey(deformatkey)

	return formatkey,deformatkey
	pass

def generate_format_key_recursely(struct_info):
	formatkey,deformatkey=_generate_format_key_recursely(struct_info)
	deformatkey = deformatkey
	formatkey=formatkey
	return formatkey,deformatkey
	pass

refered_struct_maxsize_count_space={}

def count_struct_maxsize(struct_info):
	maxsize=0

	ss=struct_registed(refered_struct_maxsize_count_space,struct_info)
	if(ss!=None and 'maxsize' in ss):
		maxsize=ss['maxsize']
		return maxsize,ss

	struct_info=copy(struct_info)
	register_struct(refered_struct_maxsize_count_space,struct_info)

	for var_info in struct_info['var_info_list']:
		var_name=var_info['varname']
		vartype=var_info['vartype']
		var_maxsize=0
		if(vartype=='refer'):
			refername=var_info['refername']
			my_assert((refername in struct_info_list),'')
			var_maxsize,_=count_struct_maxsize(struct_info_list[refername])
		else:
			var_maxsize=get_type_size(vartype)

		varlength=var_info['varlength']
		if(varlength==0):
			varlength=1
		maxsize=maxsize+var_maxsize*varlength*(var_info['varwidth'] or 1)

	struct_info['maxsize']=maxsize

	return maxsize,struct_info

def resolve_varlist_reference_relavant(struct_info):
	struct_varlist = {}
	struct_varlist = struct_info['var_info_list']
	struct_varlist_for_modify = copy(struct_varlist)
	struct_varlist_list = dict()

	last_type=None
	last_index = 0
	for var_info in struct_varlist:
		vartype = var_info['vartype']
		if(vartype == 'refer'):
			varname = var_info['refername']
			refer_varlist = resolve_varlist_reference_relavant(struct_info_list[varname])
			index = struct_varlist.index(var_info)
			struct_varlist_list[index] = refer_varlist
			#if(index - last_index > 1):
			if(index!=last_index and last_type != 'refer'):
				struct_varlist_list[last_index] = struct_varlist[last_index:index]

			last_index = index + 1
			last_type=True
		else:
			last_type=False
	
	struct_varlist_list[last_index] = struct_varlist[last_index:]

	final_varlist = list()
	for value in struct_varlist_list.values():
		final_varlist.extend(value)

	return final_varlist
	pass

def resolve_struct_reference_relavant(struct_info):
	struct_info = copy(struct_info)
	struct_varlist = resolve_varlist_reference_relavant(struct_info)
	struct_info['var_info_list'] = struct_varlist
	return struct_info
	pass
	
refered_struct_space={}

def resolve_struct_reference_relavant_to_recurse_style(struct_info):
	struct_name=struct_info['struct_name_list']['use_name']
	if(struct_name in refered_struct_space):
		return refered_struct_space[struct_name]
	else:
		maxsize,_=count_struct_maxsize(struct_info)

		struct_info = copy(struct_info)
		register_struct(refered_struct_space,struct_info)

		struct_info['maxsize']=maxsize
		
		struct_varlist = struct_info['var_info_list']
		for var_info in struct_varlist:
			vartype=var_info['vartype']
			if(vartype=='refer'):
				refername=var_info['refername']
				my_assert(refername in struct_info_list,'')
				refered_struct=struct_info_list[refername]
				var_info['refered_definition']=refername
				var_info['maxsize'],_=count_struct_maxsize(refered_struct)

		return struct_info
	error('')
	pass
