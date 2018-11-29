from itertools import zip_longest

from fcommand import FCommandParserFactory, FStackCommandParserFactory
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fstring import FString, FUnicode, FBytes, FChar, FByte
from flist import FList
from fiter import FIterable, FIteratorConcatenate
from faseq import FArithmeticSequence, FArithmeticComplexSequence

@FCommandParserFactory('→', 1, 1)
def arith_start(a):
	if isinstance(a, FComplex):
		return FList(FArithmeticComplexSequence(start=a))
	elif isinstance(a, FNumber):
		return FList(FArithmeticSequence(start=a))
	else:
		raise TypeError(a)

@FCommandParserFactory('↣', 2, 1)
def arith_start_end(a, b):
	if isinstance(a, FComplex) or isinstance(b, FComplex):
		return FList(FArithmeticComplexSequence(start=a, end=b))
	elif isinstance(a, FNumber) and isinstance(b, FNumber):
		return FList(FArithmeticSequence(start=a, end=b))
	else:
		raise TypeError(a)
		
@FCommandParserFactory('↦', 2, 1)
def arith_start_step(a, b):
	if isinstance(a, FComplex) or isinstance(b, FComplex):
		return FList(FArithmeticComplexSequence(start=a, step=b))
	elif isinstance(a, FNumber) and isinstance(b, FNumber):
		return FList(FArithmeticSequence(start=a, step=b))
	else:
		raise TypeError(a if not isinstance(a, FNumber) else b)
		
@FCommandParserFactory('↠', 3, 1)
def arith_start_end_step(a, b, c):
	if isinstance(a, FComplex) or isinstance(b, FComplex) or isinstance(c, FComplex):
		return FList(FArithmeticComplexSequence(start=a, end=b, step=c))
	elif isinstance(a, FNumber) and isinstance(b, FNumber) and isinstance(c, FNumber):
		return FList(FArithmeticSequence(start=a, end=b, step=c))
	else:
		raise TypeError(a if not isinstance(a, FNumber) else b if not isinstance(b, FNumber) else c)

@FCommandParserFactory('⇶', 0, 1)
def arith_zero_up():
	return FList(FArithmeticSequence())


