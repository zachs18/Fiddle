import re
import math

from parse import FToken, FParser, FParserSingleton, parse, parse_one
from fcommand import CallType, FCommandToken, FCommandParserFactory
from stack import Stack
import int_rep

def Tr(x):
	return x*(x+1)//2
def int_sqrt(x):
	if x < 0:
		raise ValueError(x)
	if x == 0:
		return 0
	a = b = c = x // 2**(x.bit_length()//2+1) or 1
	while a*a != x:
		a, b, c = b, c, (c + x//c)//2
		if b == c or a == c:
			break
	#print(a,b,c)
	if c*c > x:
		return c-1
	return c
def Tr_inv(x):
	return (-1 + int_sqrt(1+8*x))//2


class FRotateParser(FParserSingleton):
	@staticmethod
	def int_to_rot(i):
		"""
		Converts an integer to a rotate tuple
		# (2, 1) is just swap
		0 -> (3, 1) # b'r\x00'
		1 -> (3, 2)
		2 -> (4, 1)
		127 -> (17, 9) # b'r\x7f', highest 2-byte
		    0 + 128 -> (17, 10) # b'r\x80\x00', lowest 3-byte
		16383 + 128 -> (183, 42) # b'r\xbf\xff', highest 3-byte
		      0 + 16384 + 128 -> (183, 42) # b'r\xc0\x00\x00', lowest 4-byte
		2113663 + 16384 + 128 -> (2057, 1125) # b'\xdf\xff\xff', highest 4-byte
		72624976668147839 -> (381116720, 108043720) # b'\xfe\xff\xff\xff\xff\xff\xff\xff', highest
		"""
		i += 1 # (2, 1) is not counted here
		count = Tr_inv(i)
		times = i - Tr(count)
		count += 2
		times += 1
		return (count, times)
		
	@classmethod
	def _match(cls, s):
		if isinstance(s, str):
			if s[0] != 'r':
				return None, 0
			else:
				return None, 1
		else:
			if s[0] != b'r'[0]:
				return None, 0
			else:
				import int_rep
				match = int_rep.int_rep_b_re.match(s[1:])
				if match:
					length = 1 + match.end()
					return cls.int_to_rot(int_rep.bytes_to_int(s[1:length])), length
				elif len(s) == 1: # implicit from stack at end of file
					return None, 1
				elif s[1] == 255: # explicit from stack
					return None, 2
				else: # no match
					return None, 0
	
	@classmethod
	def match(cls, s):
		# returns match length
		_, length = cls._match(s)
		return length
	
	@classmethod
	def parse(cls, s):
		rotate, length = cls._match(s)
		if not length:
			raise ValueError
		return FRotateCommandToken('r', rotate), length

class FRotateCommandToken(FCommandToken):
	def __init__(self, name, rotate=None):
		self.name = name
		self.rotate = rotate
	def apply(self, s):
		if self.rotate:
			count = self.rotate[0]
			times = self.rotate[1]
		else:
			times = int(s.pop())
			count = int(s.pop())
		if count < 3:
			raise ValueError(count)
		if times >= count:
			raise ValueError(times)
		items = s.popn(count)
		newitems = items[times:] + items[:times]
		for item in newitems:
			s.push(item)
	def __repr__(self):
		return "FRotateCommandToken(%s, %r))" % (self.name, self.rotate)

@FCommandParserFactory('s', 2, 2)
def swap(a, b):
	return (b, a)

class FFlipParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		if isinstance(s, str):
			if s[0] != 'f':
				return None, 0
			else:
				return None, 1
		else:
			if s[0] != b'f'[0]:
				return None, 0
			else:
				import int_rep
				match = int_rep.int_rep_b_re.match(s[1:])
				if match:
					length = 1 + match.end()
					return int_rep.bytes_to_int(s[1:length]), length
					# NOTE: length 0 is interpreted as from stack
				elif len(s) == 1: # error
					return None, 0
				elif s[1] == 255: # explicit full stack
					return None, 2
				else: # no match
					return None, 0
	
	@classmethod
	def match(cls, s):
		# returns match length
		_, length = cls._match(s)
		return length
	
	@classmethod
	def parse(cls, s):
		flip, length = cls._match(s)
		if not length:
			raise ValueError
		return FRotateCommandToken('f', flip), length
	

class FFlipCommandToken(FCommandToken):
	def __init__(self, name, flip=None):
		self.name = name
		self.flip = flip
	def apply(self, stack):
		if self.flip == 0:
			count = stack.length()
		elif self.flip is not None:
			count = self.flip
		else:
			count = int(stack.pop())
		if count < 0:
			raise ValueError(count)
		if count < float('inf'):
			items = stack.popn(count)[::-1]
			for item in items:
				stack.push(item)
		else:
			raise ValueError("cannot (yet) flip infinite stack")
	def __repr__(self):
		return "FRotateCommandToken(%s, %r))" % (self.name, self.rotate)
	
