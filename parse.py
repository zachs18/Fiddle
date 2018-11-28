from abc import ABC, abstractmethod
import re



class FToken(ABC):
	@abstractmethod
	def __init__(self):
		pass
	@abstractmethod
	def apply(self, stack):
		pass

parsers = []

class FParser(ABC):
	def __new__(cls, *args, **kwargs):
		self = object.__new__(cls)
		parsers.append(self)
		return self
	@abstractmethod
	def __init__(self):
		pass
	@abstractmethod
	def match(self, s):
		return 0 # length/number of bytes/characters used
	@abstractmethod
	def parse(self, s):
		return [], 0 # 1 token or list of 0,2+ tokens, bytes/characters used

class FParserFactory(ABC):
	@abstractmethod
	def __init__(self):
		pass
	@abstractmethod
	def __call__(self, func):
		pass

class FParserSingletonType(type, FParser):
	def __new__(cls, name, bases, dct):
		if 'parse' not in dct or 'match' not in dct:
			raise ValueError(cls, dct)
		self = type.__new__(cls, name, bases, dct)
		parsers.append(self)
		#print(self, name, bases, dct)
		return self
class FParserSingleton(metaclass=FParserSingletonType):
	@classmethod
	def match(cls, s):
		return 0
	@classmethod
	def parse(cls, s):
		raise ValueError
	
	
class FWhitespaceParser(FParserSingleton):
	"""
	def __new__(cls):
		if hasattr(cls, "instance"):
			return cls.instance
		self = cls.instance = super().__new__(cls)
		self.s_re = re.compile( r'\s+')
		self.b_re = re.compile(br'\s+')
	def __init__(self):
		pass"""
	s_re = re.compile( r'\s+')
	b_re = re.compile(br'\s+')
	@classmethod
	def match(cls, s):
		if isinstance(s, str):
			match = cls.s_re.match(s)
			if match:
				return match.end()
		elif isinstance(s, bytes):
			match = cls.b_re.match(s)
			if match:
				return match.end()
		return 0
	@classmethod
	def parse(cls, s):
		length = cls.match(s)
		return [], length
#whitespace = FWhitespaceParser()

def parse_one(s):
	"""
	Return a tuple: ([tokens,], length used, rest of source)
	"""
	longest, length = None, 0
	for p in parsers:
		if p.match(s) > length:
			longest = p
			length = p.match(s)
	if longest is None:
		raise ValueError(s)
	toks, length = longest.parse(s)
	if isinstance(toks, list):
		pass
	else:
		toks = [toks]
	return toks, length, s[length:]

def parse(s):
	ret = []
	while len(s):
		toks, length, s = parse_one(s)
		ret += toks
	return ret

def test(s):
	import stack
	toks = parse(s)
	st = stack.Stack()
	for tok in toks:
		tok.apply(st)
	return st

import fbasiccommands
import parsenumbers
import parselist
import stack_manipulation
import vectorized
import stringparse