typedef struct _tagUser_ScoreEvent{
	int nUserID;
	int nChairNO;
	int nEvent;	
	int	nScoreDiff;
	int nScore;
	int nFactor; //因数 供特定需求
	int nReserved[4];
}USER_SCOREEVENT, *LPUSER_SCOREEVENT;