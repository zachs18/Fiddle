from itertools import zip_longest
import collections
import math
import re

from parse import FParserSingleton
from encoding import page
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

class SeqType:
	# if start/end/step/length is an int it is an index in the arguments
	# if it is an FNumber it is literal
	# if it is None it is unspecified
	# if it is a tuple of ((int,*), lambda), 
	#    the int(s) is(are) the argument index(es),
	#    which should be passed to the lambda for the argument
	def __init__(self, name, argc, start, end, step, length=None, inclusive=False):
		self.name = name
		self.argc = argc
		self.start = start
		self.end = end
		self.step = step
		self.length = length
		self.inclusive = inclusive

faseqtypes = {
	#NOTE: seqtypes that seem to specify an end and a length will only actually use the length
	
	# 'a': s up
	'a': SeqType('a', 1, 0, None, FInteger(1)),
	# 'b': s up length long
	'b': SeqType('b', 2, 0, None, FInteger(1), length=1),
	
	# 'c': s down
	'c': SeqType('c', 1, 0, None, FInteger(-1)),
	# 'd': s down length long
	'd': SeqType('d', 2, 0, None, FInteger(-1), length=1),
	
	# 'e': s away from 0
	'e': SeqType('e', 1, 0, None, ((0,), lambda s:s.sign())),
	# 'f': s away from 0 length long
	'f': SeqType('f', 2, 0, None, ((0,), lambda s:s.sign()), length=1),
	
	# 'g': s toward 0 exclusive
	'g': SeqType('g', 1, 0, FInteger(0), ((0,), lambda s:-s.sign())),
	# 'h': s toward 0 exclusive length long
	'h': SeqType('h', 2, 0, None, ((0,1), lambda s,l:(-s/l if l else l)), length=1),
	
	# 'i': s toward 0 inclusive
	'i': SeqType('i', 1, 0, FInteger(0), ((0,), lambda s:-s.sign()), inclusive=True),
	# 'j': s toward 0 inclusive length long
	'j': SeqType('j', 2, 0, None, ((0,1), lambda s,l:(-s/(l-1) if l-1 else l-1)), length=1, inclusive=True),
	
	# 'k': 0 up/down to e exclusive
	'k': SeqType('k', 1, FInteger(0), 0, ((0,), lambda e:e.sign())),
	# 'l': +/-1 up/down to e exclusive
	'l': SeqType('l', 1, ((0,), lambda e:e.sign()), 0, ((0,), lambda e:e.sign())),
	# 'm': 0 up/down to e exclusive length long
	'm': SeqType('m', 2, FInteger(0), None, ((0,1), lambda e,l:(e/l if l else l)), length=1),
	
	# 'n': 0 up/down to e inclusive
	'n': SeqType('n', 1, FInteger(0), 0, ((0,), lambda e:e.sign()), inclusive=True),
	# 'o': +/-1 up/down to e inclusive
	'o': SeqType('o', 1, ((0,), lambda e:e.sign()), 0, ((0,), lambda e:e.sign()), inclusive=True),
	# 'p': 0 up/down to e inclusive length long
	'p': SeqType('p', 2, FInteger(0), None, ((0,1), lambda e,l:(e/(l-1) if l-1 else l-1)), length=1, inclusive=True),
	
	# 'q': s up to e exclusive
	'q': SeqType('q', 2, 0, 1, FInteger(1)),
	# 'r': s up/down to e exclusive
	'r': SeqType('r', 2, 0, 1, ((0,1), lambda s,e:(e-s).sign())),
	# 's': s up/down to e exclusive length long
	's': SeqType('s', 3, 0, 1, ((0,1,2), lambda s,e,l:((e-s)/l) if l else l), length=2),
	# 't': s down to e exclusive
	't': SeqType('t', 2, 0, 1, FInteger(-1)),
	
	# 'u': s up to e inclusive
	'u': SeqType('u', 2, 0, 1, FInteger(1), inclusive=True),
	# 'v': s up/down to e inclusive
	'v': SeqType('v', 2, 0, 1, ((0,1), lambda s,e:(e-s).sign()), inclusive=True),
	# 'w': s up/down to e inclusive length long
	'w': SeqType('w', 3, 0, 1, ((0,1,2), lambda s,e,l:((e-s)/(l-1)) if l-1 else l-1), length=2, inclusive=True),
	# 'x': s down to e inclusive
	'x': SeqType('x', 2, 0, 1, FInteger(-1), inclusive=True),
	
	# 'y': 0 up/down by t
	'y': SeqType('y', 1, FInteger(0), None, 0),
	# 'z': 0 up/down by t length long
	'z': SeqType('z', 2, FInteger(0), None, 0, length=1),
	
	# 'A': t up/down by t
	'A': SeqType('A', 1, 0, None, 0),
	# 'B': t up/down by t length long
	'B': SeqType('B', 2, 0, None, 0, length=1),
	
	# 'C': s up/down by t
	'C': SeqType('C', 2, 0, None, 1),
	# 'D': s up/down by t length long
	'D': SeqType('D', 3, 0, None, 1, length=2),
	
	# 'E': 0 up/down to e by t exclusive
	'E': SeqType('E', 2, FInteger(0), 0, 1),
	# 'F':   up/down by t to e length long exclusive
	'F': SeqType('F', 3, ((0,1,2), lambda e,t,l: e-l*t), 0, 1, length=2),
	
	# 'G': 0 up/down to e by t inclusive
	'G': SeqType('G', 2, FInteger(0), 0, 1, inclusive=True),
	# 'H':   up/down by t to e length long inclusive
	'H': SeqType('H', 3, ((0,1,2), lambda e,t,l: e-(l-1)*t), 0, 1, length=2, inclusive=True),
	
	# 'I': normal
	'I': SeqType('I', 3, 0, 1, 2),
	# 'J':   up/down by t to e length long inclusive
	'J': SeqType('J', 3, 0, 1, 2, inclusive=True),
	
	# ...
	
	# 'Y': 1 up
	'Y': SeqType('Y', 0, FInteger(1), None, None),
	# 'Z': 1 up
	'Z': SeqType('Z', 0, FInteger(0), None, None),
}

def get_arg_dict(seqtype, args):
	"""
	Returns a dict with keys start, end, step, length, inclusive
	Assumes args list has already been permuted appropriately
	"""
	arg_dict = {
		'start': None,
		'end': None,
		'step': None,
		'length': None,
		# 'inclusive': False, # This is handled separately b/c isinstance(False, int), which is interpreted as an index
	}
	if len(args) != seqtype.argc:
		raise ValueError("%r is not %d args long for seqtype %s" % (args, seqtype.argc, seqtype.name))
	for attr in arg_dict:
		if not hasattr(seqtype, attr):
			continue
		value = getattr(seqtype, attr)
		if isinstance(value, int): # index in arg list
			arg_dict[attr] = args[value]
		elif isinstance(value, tuple): # tuple of tuple(arg list indexes) and lambda
			lambda_args = [args[i] for i in value[0]]
			arg_dict[attr] = value[1](*lambda_args)
		else: # default value
			arg_dict[attr] = value
	arg_dict['inclusive'] = seqtype.inclusive
	return arg_dict

casts = collections.defaultdict(
	lambda: (FNumber, FList),
	{
		'#': (FInteger, FList),
		'%': (FRational, FList),
		'@': (FFloat, FList),
		'!': (FComplex, FList),
		'.': (FChar, FUnicode),
		',': (FByte, FBytes),
		':': ((lambda x: FChar(x % 1114112)), FUnicode),
		';': ((lambda x: FByte(x % 256)), FBytes),
		'?': (None, FList), # Indicates custom function
	}
)
for k, v in casts.copy().items():
	casts[k.encode()] = v

def get_permutation(sequence, index):
	if sequence and index:
		group = index // len(sequence)
		index_in_group = index % len(sequence)
		item = sequence[:1]
		sequence = get_permutation(sequence[1:], group)
		return sequence[:index_in_group] + item + sequence[index_in_group:]
	else:
		return sequence

faseq_s_re = re.compile("⇉([#%@!.,:;?]?)([0-9]*)([a-zA-Z])");
faseq_b_re = re.compile(
	bytes([
		page.find("⇉"),
		*b"([#%@!.,:;?])?([0-9]*)([a-zA-Z])"
	])
)

class FExtendedArithmeticToken(FCommandToken):
	def __init__(self, match):
		self.source = match.group(0)
		self.cast = casts[match.group(1)]
		self.arg_permutation = int(match.group(2) or 0)
		self.name = match.group(3)
		self.seqtype = faseqtypes[self.name]
		self.argc = self.seqtype.argc
		if self.cast[0] is None: # Indicates custom function
			self.custom = True
			self.argc += 1
		else:
			self.custom = False
	def apply(self, stack):
		args = stack.popn(self.argc)
		args = get_permutation(args, self.arg_permutation)
		print(args)
		arg_dict = get_arg_dict(self.seqtype, args)
		print(arg_dict)
		stack.push(self.cast[1](FArithmeticSequence(**arg_dict, call=self.cast[0])))
	def __repr__(self):
		return "%s(%s)" % (type(self).__name__, self.source)
		
		

class FExtendedArithmeticParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		print(cls,s)
		if isinstance(s, str):
			return faseq_s_re.match(s)
		else:
			return faseq_b_re.match(s)
	@classmethod
	def match(cls, s):
		match = cls._match(s)
		return (match and match.endpos) or 0
	@classmethod
	def parse(cls, s):
		match = cls._match(s)
		print(match, match.endpos)
		if match:
			return FExtendedArithmeticToken(match), match.endpos
		else:
			return None, 0