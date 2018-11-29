from itertools import zip_longest

from fcommand import FCommandParserFactory, FStackCommandParserFactory
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fstring import FString, FUnicode, FBytes, FChar, FByte
from flist import FList
from fiter import FIterable, FIteratorConcatenate
from faseq import FArithmeticIntegerSequence, FArithmeticFloatSequence, FArithmeticRationalSequence, FArithmeticComplexSequence

@FCommandParserFactory('→', 1, 1)
def arith_start(a):
	if isinstance(a, FComplex):
		return FList(FArithmeticComplexSequence(start=a))
	elif isinstance(a, FFloat):
		return FList(FArithmeticFloatSequence(start=a))
	elif isinstance(a, FRational):
		return FList(FArithmeticRationalSequence(start=a))
	elif isinstance(a, FInteger):
		return FList(FArithmeticIntegerSequence(start=a))
	else:
		raise TypeError(a)

@FCommandParserFactory('↣', 2, 1)
def arith_start_end(a, b):
	if isinstance(a, FComplex) or isinstance(b, FComplex):
		return FList(FArithmeticComplexSequence(start=a, end=b))
	elif isinstance(a, FFloat) or isinstance(b, FFloat):
		return FList(FArithmeticFloatSequence(start=a, end=b))
	elif isinstance(a, FRational) or isinstance(b, FRational):
		return FList(FArithmeticRationalSequence(start=a, end=b))
	elif isinstance(a, FInteger) or isinstance(b, FInteger):
		return FList(FArithmeticIntegerSequence(start=a, end=b))
	else:
		raise TypeError(a)