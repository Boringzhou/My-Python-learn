# treepack
tools based on lpack

大纲：
	parse.py 用于解析较规整的C++代码，支持结构体嵌套，支持头文件包含
	style.py 用于构造lua代码，简单支持结构体嵌套引用

依赖：
	python3


使用：
-	1.修改 inc_all.h 中的头文件列表，加入自己要解析的文件名列表，其中，'PREDEF_MARCROS.h',需要保留，其他两个可删
-	2.运行命令 python style.py recurse
-	3.生成的 lua 代码在 inf.lua 文件里
-	4.若结构体之间存在互相引用，那么对最终的结构体列表调用cc.load('treepack').resolveReference(CommonReqList)，其中CommonReqList为你的结构体列表。例如（以下代码仅供参考）：

```lua
CommonReqList={
	HUZI_CARDOPE={
		lengthMap = {
			-- [1] = nChairNO( int )	: maxsize = 4,
			-- [2] = nNextChair( int )	: maxsize = 4,
			maxlen = 8
		},
		nameMap = {
			'nChairNO',		-- [1] ( int )
			'nNextChair',		-- [2] ( int )
		},
		formatKey = '<i3',
		deformatKey = '<i3',
		maxsize = 12
	},

    CARDS_UNIT={
		lengthMap = {
													-- nCardIDs	: maxsize = 16	=	4 * 4 * 1,
			[1] = { maxlen = 4 },
			-- [2] = nCardChair( int )	: maxsize = 4,
			[3] = { maxlen = 3, refered = 'CARDS_UNIT', complexType = 'link_refer' },
			maxlen = 3
		},
		nameMap = {
			'nCardIDs',		-- [1] ( int )
			'nCardChair',		-- [2] ( int )
			'dwFlags',		-- [3] ( unsigned long )
		},
		formatKey = '<i5L',
		deformatKey = '<i5L',
		maxsize = 24
	},

}

cc.load('treepack').resolveReference(CommonReq)
```

注意：
-   和老版本兼容
-	若提示找不到宏定义，则拷贝相关宏定义到 PREDEF_MARCROS.h 中
-	暂不支持字节对齐
-	暂未支持枚举
-   暂未支持字符串数组，可以做个变通，把字符数组变换成结构体，就可以当做二维结构体支持了；目前暂未对这种情况做处理。
-   最多支持二位结构体数组，超过二维数组一般用不到吧。。，请找移动平台研发人员解决吧。。
