typedef struct _tagUser_ScoreEvent{
	int nUserID;
	int nChairNO;
	int nEvent;	
	int	nScoreDiff;
	int nScore;
	int nFactor; //���� ���ض�����
	int nReserved[4];
}USER_SCOREEVENT, *LPUSER_SCOREEVENT;