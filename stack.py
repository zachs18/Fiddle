

import flist
import fnumeric

class Stack:
	def __init__(self, stack=None):
		if stack is None:
			stack = flist.FList()
		self.stack = stack
		self._stacktrace = [stack]
	def pop(self):
		try:
			return self.stack.pop(0)
		except IndexError:
			#import fnumeric
			return fnumeric.FInteger(0)
	def popn(self, n):
		ret = []
		for i in range(n):
			try:
				ret.append(self.stack.pop(0))
			except IndexError:
				#import fnumeric
				ret.append(fnumeric.FInteger(0))
		return tuple(ret)[::-1] # Functions expect their arguments in the order they were given (FIFO), not LIFO (like stack)
		# i.e. 5 3/ -> (5/3)
	def __len__(self):
		return len(self.stack)
	def push(self, value):
		self.stack.push(value)
	def zoomin(self):
		newstack = self.pop()
		if type(newstack) is not flist.FList: # cannot zoom in to FStrings, so can't use isinstance
			newstack = flist.FList([newstack])
		self.push(newstack)
		self._stacktrace.append(newstack)
		self.stack = newstack
	def zoomout(self):
		if len(self._stacktrace) > 1:
			if self.stack is not self._stacktrace[-2][0]:
				raise RuntimeError("Stack inconsistency", self)
			self.stack = self._stacktrace[-2]
			del self._stacktrace[-1]
		else:
			newstack = FList([self.stack])
			self.stack = newstack
			self._stacktrace = [newstack]
	def __str__(self):
		return str(self.stack)
	def __repr__(self):
		return str(self.stack)