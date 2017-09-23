import math

import test.hellowrold
import test.class_

print dir(math)

def double_numbers(iterable):
	for i in iterable:
		yield i + i
		
array = (1, 2, 3, 4)
for i in double_numbers(array):
	print i

array2 = (5, 6, 7, 8)
    
array3 = array + array2

print array3