from itertools import zip_longest

from parse import FParserSingleton
from fcommand import FCommandToken
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fstring import FString, FUnicode, FBytes, FChar, FByte
from flist import FList
from fiter import FIterable, FIteratorConcatenate
from faseq import FArithmeticSequence, FArithmeticComplexSequence

#TODO: all of this

argcs = [
	"ZY", # no args
	"acegiklnoyA", # one arg
	"bdfhjmpqrtuvxzBCEG", # two args
	"swDFHIJ", # three args
	"", # four args
]


class FExtendedArithmeticToken(FCommandToken):
	def __init__(self, source, name, call, inclusive):
		self.source = source
		self.name = name
		self.call = call
		self.inclusive = inclusive
		argc = -1
		for i in range(len(argcs)):
			if self.flags.name in argcs[i]:
				argc = i
				break
		if argc == -1:
			raise ValueError(self.flags.name)
		self.argc = argc
	def apply(self, stack):
		args = stack.popn(self.argc)
		if self.name == 'a':
			arg = args[0]
			if isinstance(arg, 
			stack.push(

class FExtendedArithmeticParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		_s = s
		name = ''
		call = lambda x:x
		inclusive = False
		if isinstance(s, str):
			if not s.startswith("⇉"):
				return None, 0
	@classmethod
	def match(cls, s):
		pass
	@classmethod
	def parse(cls, s):
		pass
