
-- this pack is only for debug,for convenient and readability

require('pack')

local function stringFillZeroR(value,length)
	--	for i = data.value:len()+1, data.length do
	--		data.value = data.value .. string.char(0)
	--	end
	value=value..string.char(0):rep(length-value:len())
	return value
end

local function stringStripZeroR(data)
	data=data:gfind('[^%z]*')()
	return data
end

local parcelFunctionList={
	matrix2=function (value,length,target)
		assert(#target~=length.maxwidth,'')
		if(type(value)=='nil')then
			value={}
		end
		if(#value<length.maxwidth)then
			for i=#value+1,length.maxwidth do
				local item={}
				if(#item<length.maxlen)then
					for j=#item+1,length.maxlen do
						item[j]=0
					end
				end
				value[i]=item
			end
		end


		for _,recode in ipairs(value) do
			for _,item in ipairs(recode) do
				target[#target+1]=item
			end
		end
	end
}
local function parcelComplexType(value,length,target)
	local func=parcelFunctionList[length.complexType]
	return func(value,length,target)
end

local parseFunctionList={
	matrix2=function (length,deDataMap,start)
		local deitem={}
		for recode=1,length.maxwidth do
			local temp={}
			for index=1,length.maxlen do
				temp[index]=deDataMap[start]
				start=start+1
			end
			deitem[recode]=temp
		end
		return deitem,start
	end
}

local function parseComplexType(length,dedata,start)
	local func=parseFunctionList[length.complexType]
	return func(length,dedata,start)
end

local function parcelExchMap(dataMap,exchMap,target)
	local lengthMap=exchMap.lengthMap
	local nameMap=exchMap.nameMap
	local target=target or {}
	local maxlen=lengthMap.maxlen
	--	for _,v in ipairs(dataMap) do
	for index = 1,maxlen do
		local name=nameMap[index]
		assert(name,'')
		local value=dataMap[name]
		local length=lengthMap[index]
		if(type(length)~='table')then
			if(length and length>0)then
				value=value or ''
				assert(type(value)=='string',string.format('type of value(%s %s=%s) should only be string',type(value),exchMap.nameMap[index],''..(value or '')))
				value=stringFillZeroR(value,length)
			end

			-- check value
			value=value or 0
			--			if(type(value)~='number')then
			--printError('number expected, got %s',type(value))
			--			end

			--			value=(type(value)=='number' and value) or 0
			target[#target+1]=value
		elseif(length.complexType)then
			parcelComplexType(value,length,target)
		else
			for i = 1,length.maxlen do
				target[#target+1]=(value and value[i]) or 0
			end
		end
	end
	return target
end

--return pack

local function getData(rest,...)
	-- body
	return {...}
end

local function parseExchMap(exchMap,deDataMap,start)
	-- body
	local varMap={}
	local lengthMap=exchMap.lengthMap
	local nameMap=exchMap.nameMap
	local maxlen=lengthMap.maxlen
	local value,length,varname,deitem
	local start=start or 1
	--	for k,v in ipairs(exchMap) do
	for index = 1,maxlen do
		length=lengthMap[index]
		varname=nameMap[index]
		if(type(length)~='table') then
			deitem=deDataMap[start]
			if(type(deitem)=='string')then
				deitem=stringStripZeroR(deitem)
			end
			start=start+1
		elseif(length.complexType)then
			deitem,start=parseComplexType(length,deDataMap,start)
		else
			--parcelExchMap(v.value,deDataMap,start)
			deitem={}
			for k = 1,length.maxlen do
				deitem[k]=deDataMap[start]
				start=start+1
			end

		end
		varMap[varname]=deitem
	end

	return varMap,start
end

parseFunctionList.link_refer=function(length,deDataMap,start)
	local deitem={}
	local exchMap=length.refered
	local maxwidth=length.maxwidth or 1
	local maxlen = length.maxlen or 1
	local deformatKey=exchMap.deformatKey
	local subDeDataMap
	for i=1,maxwidth do
		local temp={}
		for j=1,maxlen do
			temp[j],start=parseExchMap(exchMap,deDataMap,start)
		end
		deitem[i]=temp
	end

	if(length.maxwidth==nil)then
		deitem=deitem[1]
	end
	if(length.maxlen==nil)then
		deitem=deitem[1]
	end

	return deitem,start
end

parcelFunctionList.link_refer=function (value,length,target)

	if(value==nil)then
		value={}
		if(length.maxlen~=nil)then
			for i=1,length.maxlen do
				value[i]={}
			end
		end
	end

	local exchMap=length.refered
	local formatKey=exchMap.formatKey
	local data,dataList
	--assert(#target~=length.maxwidth,'')
	if(length.maxlen==nil)then
		value={value}
	else
		local _,test_value=next(value)
		if(type(test_value)~='table')then
			if(length.maxwidth==nil)then
				printError('unmatched type, need matrix1 at least')
			else
				printError('unmatched type, need matrix2 at least')
			end
			assert(false)
		end
	end
	
	if(length.maxwidth==nil)then
		value={value}
	else
		local _,test_value=next(value)
		if(type(test_value)~='table')then
			printError('unmatched type, need matrix2 at least')
			assert(false)
		end
	end

	for _,recode in ipairs(value) do
		for _,item in ipairs(recode) do
			assert(type(item)=='table', '')
			parcelExchMap(item,exchMap,target)
		end
	end
end

local function tree_pack(dataMap,exchMap)
	if(DEBUG==0)then
		if(not (dataMap and exchMap and exchMap.formatKey))then
			return nil
		end
	else
		assert(dataMap and exchMap and exchMap.formatKey,'')
	end
	
	local dataList=parcelExchMap(dataMap,exchMap)
	local data = string.pack(exchMap.formatKey, unpack(dataList))
	return data
end

local function parcelAndWrite(dataMap, exchMap, dataListTotal, formatKeyTotal)
    if not (dataMap and exchMap and dataListTotal and formatKeyTotal) then return end

    local dataListTotalTemp = dataListTotal
    local formatKeyTotalTemp = formatKeyTotal

	local dataList=parcelExchMap(dataMap, exchMap)
            
    for i=1, #dataList do
        dataListTotalTemp[#dataListTotalTemp + 1] = dataList[i]
    end
    formatKeyTotalTemp = formatKeyTotalTemp..string.sub(exchMap.formatKey, 2)

    return dataListTotalTemp, formatKeyTotalTemp
end

local function tree_packs(...)
    local treeData = {}
    for i, v in ipairs{...}  do
        treeData[#treeData + 1] = v
    end
    
    local dataListTotal = {}
    local formatKeyTotal = ""

    for i=1, #treeData do
        if not treeData[i] then break end

        local dataMaps   = treeData[i][1]
        local exchMap   = treeData[i][2]
        local count     = treeData[i][3]
        
        if dataMaps and exchMap then
    	    if(DEBUG==0)then
    		    if(not (dataMaps and exchMap))then
    			    return nil
    		    end
    	    else
    		    assert(dataMaps and exchMap,'')
    	    end

            if not (type(count) == 'number' and count > 1) then
                count = 1
            end

            if count==1 then
                dataListTotal, formatKeyTotal = parcelAndWrite(dataMaps, exchMap, dataListTotal, formatKeyTotal)
            else
                for j=1, #dataMaps do
                    dataListTotal, formatKeyTotal = parcelAndWrite(dataMaps[j], exchMap, dataListTotal, formatKeyTotal)
                end
            end        
        end
    end

	local data = string.pack(formatKeyTotal, unpack(dataListTotal))
	return data
end

--return pack

local function getData(rest,...)
	-- body
	return {...}
end

local function parseExchMap(exchMap,dedata)
	-- body
	local varMap={}
	local lengthMap=exchMap.lengthMap
	local nameMap=exchMap.nameMap
	local maxlen=lengthMap.maxlen
	local value,length,varname,deitem
	local start=1
	--	for k,v in ipairs(exchMap) do
	for index = 1,maxlen do
		length=lengthMap[index]
		varname=nameMap[index]
		if(type(length)~='table') then
			deitem=dedata[start]
			if(type(deitem)=='string')then
				deitem=stringStripZeroR(deitem)
			end
			start=start+1
		elseif(length.complexType)then
			deitem,start=parseComplexType(length,dedata,start)
		else
			--parcelExchMap(v.value,dedata,start)
			deitem={}
			for k = 1,length.maxlen do
				deitem[k]=dedata[start]
				start=start+1
			end

		end
		varMap[varname]=deitem
	end

	return varMap
end

local function tree_unpack(data,exchMap)
	if(DEBUG==0)then
		if(not (data and exchMap))then
			return nil
		end
	else
		assert(data and exchMap,'')
	end
	
	local deformatKey=exchMap.deformatKey
	local dedata=getData(string.unpack(data,deformatKey))

	--	local target = clone(exchMap)
	return parseExchMap(exchMap,dedata)
end

local function tree_unpacks(data,...)
    local exchMaps = {}
    for i, v in ipairs{...}  do        
        exchMaps[#exchMaps + 1] = v
    end
    
    local dataMaps = {}
    local dataTemp = data
    for i=1, #exchMaps do
        if not exchMaps[i] then break end

        local exchMap   = exchMaps[i][1]
        local count     = exchMaps[i][2]

        if not exchMap then
            exchMap = exchMaps[i]
            count   = 1
        end
        if not (type(count) == 'number' and count > 1) then
            count = 1
        end

        if count == 1 then
            dataMaps[#dataMaps + 1] = tree_unpack(dataTemp, exchMap)

            dataTemp = string.sub(dataTemp, exchMap.maxsize + 1)
        else
            dataMaps[#dataMaps + 1] = {}
            for k=1, count do
                dataMaps[#dataMaps][k] = tree_unpack(dataTemp, exchMap)
            
                dataTemp = string.sub(dataTemp, exchMap.maxsize + 1)
            end
        end
    end

    return dataMaps
end

local function align(data,alignSize)
	if(DEBUG==0)then
		if(not data)then
			return nil
		end
	else
		assert(data,'')
	end
	
	local alignSize=(alignSize and checknumber(alignSize)) or 4
	local n=alignSize-math.fmod(data:len(),alignSize)
	n=(n==4 and 0) or n
	printInfo('align data size from %d to %d',data:len(),data:len()+n)
	data=data..string.char(0):rep(n)
	return data
end

local function tree_pack_and_aligned(dataMap,exchMap,alignSize)
	local data=tree_pack(dataMap,exchMap)
	return align(data,alignSize)
end

local function tree_pack_and_aligneds(...)
	local data=tree_packs(...)
	return align(data,alignSize)
end

local function tree_pack_warning(...)
	printError('%s','pack data without aligned')
	return tree_pack(...)
end

local totest=true

local function test(treepack)
	if(totest)then
		local tree_pack,tree_unpack=treepack.pack,treepack.unpack
		

		local UNITE_TYPE={
		lengthMap = {
			-- [1] = nCardIDs( int )	: maxsize = 4,
			maxlen = 1
		},
		nameMap = {
			'nCardIDs',		-- [0]
		},
		formatKey = '<i',
		deformatKey = '<i',
		maxsize = 4
	}
		local GAME_PUBLIC_INFO={
		lengthMap = {
					-- WaitCardUnite	: maxsize = 4	=	4 * 1 * 1,
			[1] = {maxlen = 1, maxwidth = 1, refered = UNITE_TYPE, complexType = 'link_refer'},
			-- [2] = nWaitChair( int )	: maxsize = 4,
					-- wfk	: maxsize = 32	=	1 * 32 * 1,
			[3] = 32,
					-- wfk2	: maxsize = 32	=	1 * 32 * 1,
			[4] = 32,
					-- wfk3	: maxsize = 32	=	1 * 32 * 1,
			[5] = 32,
			maxlen = 5
		},
		nameMap = {
			'WaitCardUnite',		-- [0]
			'nWaitChair',		-- [1]
			'wfk',		-- [2]
			'wfk2',		-- [3]
			'wfk3',		-- [4]
		},
		formatKey = '<i2A3',
		deformatKey = '<i2A32A32A32',
		maxsize = 104
	}

		local dataMap={}
		dataMap['nWaitChair']=455
		dataMap['WaitCardUnite']={{{nCardIDs=12}}}
		dataMap['wfk']='lkwjelfk'
		dataMap['wfk2']=''
		dataMap['wfk3']='lkwjelf3k'
		local data=tree_pack(dataMap,GAME_PUBLIC_INFO)

		local target = tree_unpack(data,GAME_PUBLIC_INFO)
		dump(target)

	end

end

local _treepack={
	pack=tree_pack_warning,
	unpack=tree_unpack,
    --unpacks多个结构体格式解包unpacks(pData, exchMap, {exchMap}, {exchMap, 1}, {exchMap, 2}), 返回一个table, table[1], table[2], table[2][1], table[2][2]
    --(pData, {exchMap, count}, ...), count>1时,生成二维table, =1时count,{}均可省略
    unpacks=tree_unpacks,
	alignpack=tree_pack_and_aligned,
    --alignpacks打包多个结构体, alignpacks({dataMap, exchMap}, {dataMap, exchMap, 1}, {dataMap, exchMap, 2})
    --({dataMap, exchMap, count}, ...) count>1时, dataMap必须是table, count=1时可省略
    alignpacks=tree_pack_and_aligneds,
	align=align,
	parseListWithInfoHead=parseListWithInfoHead,
	_test=test,
}

test(_treepack)

return _treepack

