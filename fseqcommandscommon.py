

class SeqType:
	# if start/end/step/length is an int it is an index in the arguments
	# if it is an FNumber it is literal
	# if it is None it is unspecified
	# if it is a tuple of ((int,*), lambda), 
	#    the int(s) is(are) the argument index(es),
	#    which should be passed to the lambda for the argument
	def __init__(self, name, argc, start, end, step, length=None, inclusive=False):
		self.name = name
		self.argc = argc
		self.start = start
		self.end = end
		self.step = step
		self.length = length
		self.inclusive = inclusive
