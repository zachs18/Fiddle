from itertools import zip_longest

from fcommand import FCommandParserFactory, FStackCommandParserFactory
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fstring import FString, FUnicode, FBytes, FChar, FByte
from flist import FList
from fiter import FIterable, FIteratorConcatenate, FIteratorZip

@FCommandParserFactory('+', 2, 1)
def add(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return a + b
	elif isinstance(a, FIterable) and isinstance(b, FIterable):
		return FList(FIteratorZip(iter(a), iter(b), call=add.func))
	else:
		raise TypeError(a, b)

@FCommandParserFactory('|', 2, 1)
def concatenate(a, b):
	if hasattr(a, "_inf") and a._inf:
		return a
	elif isinstance(a, (FUnicode, FChar)):
		if isinstance(b, FChar):
			return FUnicode(FIteratorConcatenate(a, b))
		elif isinstance(b, FInteger):
			return FUnicode(FIteratorConcatenate(a, FChar(b)))
		elif isinstance(b, FUnicode):
			return FUnicode(FIteratorConcatenate(a, b))
		elif isinstance(b, FBytes):
			return FBytes(FIteratorConcatenate(a.encode(), b))
		else:
			#return FList([a, b]) # b could be a list
			pass
	elif isinstance(a, (FBytes, FByte)):
		if isinstance(b, FByte):
			return FBytes(FIteratorConcatenate(a, b))
		elif isinstance(b, FChar):
			return FBytes(FIteratorConcatenate(a, b.encode()))
		elif isinstance(b, FInteger):
			return FBytes(FIteratorConcatenate(a, FByte(b)))
		elif isinstance(b, FUnicode):
			return FBytes(FIteratorConcatenate(a, b.encode()))
		elif isinstance(b, FBytes):
			return FBytes(FIteratorConcatenate(a, b))
		else:
			pass
			#return FList([a, b]) # b could be a list
	elif isinstance(a, FInteger):
		if isinstance(b, (FUnicode, FChar)):
			return FUnicode(FIteratorConcatenate(FChar(a), b))
		elif isinstance(b, (FBytes, FByte)):
			return FBytes(FIteratorConcatenate(FByte(a), b))
		else:
			#return FList([a, b]) # b could be a list
			pass
	elif isinstance(a, FList):
		if isinstance(b, FList):
			return FList(FIteratorConcatenate(a, b))
		else:
			return FList(FIteratorConcatenate(a, FList([b])))
	
	if isinstance(b, FList):
		return FList(FIteratorConcatenate(FList([a]), b))
	else:
		#print(a,b)
		return FList([a, b])

		
@FCommandParserFactory('-', 2, 1)
def subtract(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return a - b
	else:
		raise TypeError(a, b)

@FCommandParserFactory('*', 2, 1)
def multiply(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return a * b
	elif isinstance(a, FReal) and isinstance(b, FIterable):
		if a <= 0:
			return type(b)()
		elif b._inf:
			return b.copy() # inf * 1.5 == inf, inf * 0.5 == inf
		elif a.is_integer():
			return type(b)(FIteratorConcatenate(*(b.copy() for _ in range(a))))
			
		else:
			raise TODO
	else:
		raise TypeError(a, b)

@FCommandParserFactory('/', 2, 1)
def divide(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return a / b
	else:
		raise TypeError(a, b)

@FCommandParserFactory('%', 2, 1)
def mod(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return a % b
	else:
		raise TypeError(a, b)
	
@FCommandParserFactory('§', 2, 2)
def basicdivmod(a, b):
	if isinstance(a, FNumber) and isinstance(b, FNumber):
		return divmod(a, b)
	else:
		raise TypeError(a, b)

@FCommandParserFactory('i', 1, 1)
def imag(a):
	if isinstance(a, FNumber):
		return a*FComplex(0,1)
	else:
		raise TypeError(a)

@FStackCommandParserFactory(']')
def wrap(stack):
	"""
	Wrap the stack in a FList
	"""
	newstack = FList([stack.stack])
	stack.stack = newstack
	if len(stack._stacktrace) > 1:
		stack._stacktrace[-2][0] = newstack
	stack._stacktrace[-1] = newstack

@FCommandParserFactory('d', 1, 2)
def dup(a):
	return a, a.copy()

@FCommandParserFactory('=', 2, 1)
def equal(a, b):
	if isinstance(a, FList):
		if isinstance(b, FList):
			return FBool(all(equal.func(A, B) for A, B in zip_longest(a, b)))
		
	return FBool(a == b)

@FCommandParserFactory('≠', 2, 1)
def notequal(a, b):
	return FBool(a != b)

@FCommandParserFactory('<', 2, 1)
def less(a, b):
	return FBool(a < b)

@FCommandParserFactory('≤', 2, 1)
def lessequal(a, b):
	return FBool(a <= b)

@FCommandParserFactory('>', 2, 1)
def greater(a, b):
	return FBool(a > b)

@FCommandParserFactory('≥', 2, 1)
def greaterequal(a, b):
	return FBool(a >= b)

