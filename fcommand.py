import enum

from fobject import FObject
import encoding
from parse import FToken, FParser, FParserFactory

commands = dict()

class CallType(enum.Enum):
	basic = 1 # takes argc arguments, returns a tuple of M items (>1) or 1 item
	stack = 2 # takes and manipulates the stack directly, does not return a value


class FCommandToken(FToken):
	def __init__(self, name, func, call=(CallType.basic, 1, 1)):
		self.name = name
		self.func = func
		self.call = call
	def apply(self, stack):
		if self.call[0] == CallType.basic:
			args = stack.popn(self.call[1]) # stack.popn should return an iterable of the length its argument
			#print(args)
			ret = self.func(*args)
			if self.call[2] == 0 and ret != None:
				raise TypeError("FCommandToken (%r)'s func returned the wrong number of items (0 expected)" % self.name)
			elif self.call[2] == 1 and not isinstance(ret, FObject):
				raise TypeError("FCommandToken (%r)'s func returned a non-FObject object: %r" % (self.name, ret))
			elif self.call[2] > 1 and not (hasattr(ret, '__len__') and len(ret) == self.call[2]):
				raise TypeError("FCommandToken (%r)'s func returned the wrong number of items (%d expected)" % (self.name, self.call[2]))
			elif self.call[2] == 0:
				pass
			elif self.call[2] == 1:
				stack.push(ret)
			else:
				for item in ret:
					stack.push(item)
		elif self.call[0] == CallType.stack:
			self.func(stack)
		else:
			raise ValueError(self.call)
	def __repr__(self):
		return "FCommandToken(%s)" % self.name
			
class FCommandParserFactory(FParserFactory):
	"""
	Basic command type:
		takes arguments from the stack
		returns outputs to the stack
		does not depends on data around it
	"""
	def __init__(self, name, argc, retc):
		self.name = name
		self.argc = argc # argument count
		self.retc = retc # return count
	def __call__(self, func):
		if isinstance(func, FCommandParser):
			cmd = FCommandParser(self.name, func.func, call=(CallType.basic, self.argc, self.retc))
		else:
			cmd = FCommandParser(self.name, func, call=(CallType.basic, self.argc, self.retc))
		commands[self.name] = cmd
		return cmd

class FStackCommandParserFactory(FParserFactory):
	"""
	Stack command type:
		takes the stack as its arguments
		modifies the stack in-place
		returns None
		does not depends on data around it
	"""
	def __init__(self, name):
		self.name = name
	def __call__(self, func):
		if isinstance(func, FCommandParser):
			cmd = FCommandParser(self.name, func.func, call=(CallType.stack,))
		else:
			cmd = FCommandParser(self.name, func, call=(CallType.stack,))
		commands[self.name] = cmd
		return cmd

		

class FCommandParser(FParser):
	def __init__(self, name, func, call=(CallType.basic, 1, 1)):
		self.name = name
		self.ords = [ord(c) for c in name]
		self.func = func
		self.inpage = len(self.name) == 1 and self.name in encoding.page
		self.pageindex = len(self.name) == 1 and encoding.page.find(self.name)
		self.call = call
		
	def match(self, s):
		if isinstance(s, str):
			if s.startswith(self.name):
				return len(self.name) # len(self.name) characters
			else:
				return 0 # no match
		elif isinstance(s, bytes):
			if self.inpage and s[0] == self.pageindex:
				return 1 # 1 byte paged command
			length = 0
			for i in range(len(self.name)):
				num, _length = encoding.cmd_ord(s[length:])
				if self.ords[i] != num:
					return 0
				length += _length
			return length
	
	def parse(self, s):
		length = self.match(s)
		if not length:
			raise ValueError
		return FCommandToken(self.name, self.func, self.call), length
	def __repr__(self):
		return 'FCommandParser(%s)' % self.name
