class A:
	def __new__(cls, *args):
		print("A.__new__%r"%(args,))
#		return B(*args)
		return object.__new__(B)
	def __init__(self, *args):
		print('A.__init__%r'%(args,))
class B(A):
	def __new__(cls, *args):
		print("B.__new__%r"%(args,))
		return object.__new__(B)
	def __init__(self, *args):
		print('B.__init__%r'%(args,))
