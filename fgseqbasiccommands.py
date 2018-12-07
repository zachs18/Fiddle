from itertools import zip_longest

from fcommand import FCommandParserFactory, FStackCommandParserFactory
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fstring import FString, FUnicode, FBytes, FChar, FByte
from flist import FList
from fiter import FIterable, FIteratorConcatenate
from fgseq import FGeometricSequence

@FCommandParserFactory('↑', 1, 1)
def geo_start(a):
	if isinstance(a, FNumber):
		return FList(FGeometricSequence(start=a))
	else:
		raise TypeError(a)

#@FCommandParserFactory('↣', 2, 1)
#def geo_start_end(a, b):
#	if isinstance(a, FNumber) and isinstance(b, FNumber):
#		return FList(FGeometricSequence(start=a, end=b))
#	else:
#		raise TypeError(a)
		
@FCommandParserFactory('↥', 2, 1)
def geo_start_step(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return FList(FGeometricSequence(start=a, step=b))
	else:
		raise TypeError(a if not isinstance(a, FNumber) else b)
		
@FCommandParserFactory('↟', 3, 1)
def geo_start_end_step(a, b, c):
	if isinstance(a, FNumber) and isinstance(b, FNumber) and isinstance(c, FNumber):
		return FList(FGeometricSequence(start=a, end=b, step=c))
	else:
		raise TypeError(a if not isinstance(a, FNumber) else b if not isinstance(b, FNumber) else c)

#@FCommandParserFactory('⇶', 0, 1)
#def geo_zero_up():
#	return FList(FArithmeticSequence())




