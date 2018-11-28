from itertools import zip_longest

from fcommand import FCommandParserFactory, FStackCommandParserFactory
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fstring import FString, FUnicode, FBytes, FChar, FByte
from flist import FList
from fiter import FIterable, FIteratorConcatenate

@FCommandParserFactory('g', 2, 1)
def geoseq(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return a + b
	else:
		raise TypeError(a, b)
