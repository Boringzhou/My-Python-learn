import re

#print dir(re)

line = 'Cats are smarter than dogs'

matchObj = re.match( r'(.*) are (.*?) .*', line, re.M|re.I)

if matchObj:
   print ("matchObj.groups() : ", matchObj.groups())
   print ("matchObj.group() : ", matchObj.group())
   print ("matchObj.group(1) : ", matchObj.group(1))
   print ("matchObj.group(2) : ", matchObj.group(2))
else:
   print ("No match!!")
   
   
string = 'This is my python reglar \expression'
matchObj = re.match( r'This (.*) \\(e.*)', string, re.M|re.I)

print (dir(matchObj))

if matchObj:
    print (matchObj.group())
    '''
    print matchObj.group(1)
    print matchObj.group(2)
    '''
else:
    print ("No match!!")
