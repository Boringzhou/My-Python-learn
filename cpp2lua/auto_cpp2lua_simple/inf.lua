RequestInfoList = {
	USER_SCOREEVENT={
		lengthMap = {
			-- [1] = nUserID( int )	: maxsize = 4,
			-- [2] = nChairNO( int )	: maxsize = 4,
			-- [3] = nEvent( int )	: maxsize = 4,
			-- [4] = nScoreDiff( int )	: maxsize = 4,
			-- [5] = nScore( int )	: maxsize = 4,
			-- [6] = nFactor( int )	: maxsize = 4,
													-- nReserved	: maxsize = 16	=	4 * 4 * 1,
			[7] = { maxlen = 4 },
			maxlen = 7
		},
		nameMap = {
			'nUserID',		-- [1] ( int )
			'nChairNO',		-- [2] ( int )
			'nEvent',		-- [3] ( int )
			'nScoreDiff',		-- [4] ( int )
			'nScore',		-- [5] ( int )
			'nFactor',		-- [6] ( int )
			'nReserved',		-- [7] ( int )
		},
		formatKey = '<i10',
		deformatKey = '<i10',
		maxsize = 40
	}
}