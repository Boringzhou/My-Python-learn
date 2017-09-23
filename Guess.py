print 'Guess number.'
print 'If you boring of this, input q to quit.'

import random

minNum = 1
maxNum = 100
realNum = random.randint(minNum, maxNum)
num = -1

while(realNum != num):
	
	str = raw_input('please input a number: ')
	if str == 'Q' or str == 'q':
		break
		
	num = int(str)
	if num > maxNum or num < minNum :
		print 'You can`t guess this num.'
		continue

	if num > realNum :
		maxNum = num - 1
	elif num < realNum :
		minNum = num + 1
	else:
		break
		
	print '%s%d%s%d'%('The num is between ', minNum, ' and ', maxNum)

print('Done')
print "%s%d"%('The realNum is ', realNum)
	