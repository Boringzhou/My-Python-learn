class Animal(object):
	species = 'Dog'
	
	def __init__(self, name):
		self.name = name
		self._age = 100
		self.__attr1 = 'private attr'
		
		self.__privateAttr = 'test private attr'
	
	def brak(self, msg):
		return '{0}: {1}'.format(self.name, msg)
		
	@classmethod
	def get_specise(cls):
		return cls.species
		
	@staticmethod
	def grunt():
		return '*grunt*'
		
	@property
	def age(self):
		return self._age
		
	@age.setter
	def age(self, age):
		self._age = age
		
	@age.deleter
	def age(self):
		del self._age
		
	def __del__(self):
		print(self.__class__, 'destory')
		
	def __str__(self):
		return 'this is my dog, it`s name is {0}.'.format(self.name)
		
	

dog = Animal('xixiangzai')
'''
print dog.brak('wangwangwang')
print dog.get_specise()

print dog.__dict__
print dog.__weakref__

print dog.age
print dog._age

dog.__attr1 = 'public attr??'
print dog.__attr1

print Animal.__dict__
print Animal.__doc__
print Animal.__name__
print Animal.__module__
print Animal.__bases__
'''
print(str(dog))

print(dog._Animal__privateAttr)

del dog
	
	