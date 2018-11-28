from fcommand import FCommandParserFactory
from fnumeric import FNumber, FInteger, FFloat, FRational, FComplex

@FCommandParserFactory('+', 2, 1)
def add(a, b):
	if type(a) is type(b):
		return type(a)(a+b)
	