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
from faseqcommands import faseqtypes
from fgseqcommands import fgseqtypes
from faseq import FArithmeticSequence
from fgseq import FGeometricSequence

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
		'_': ((lambda x: x.real), FList),
		'|': ((lambda x: x.imag), FList),
	}
)
for k, v in casts.copy().items():
	casts[k.encode()] = v
casttypes_s =  ''.join(k for k in casts if isinstance(k, str))
casttypes_b = b''.join(k for k in casts if isinstance(k, bytes))
	
def get_permutation(sequence, index):
	if sequence and index:
		group = index // len(sequence)
		index_in_group = index % len(sequence)
		item = sequence[:1]
		sequence = get_permutation(sequence[1:], group)
		return sequence[:index_in_group] + item + sequence[index_in_group:]
	else:
		return sequence

fseq_s_re = re.compile("(⇉|⇈)([" + casttypes_s + "]?)([0-9]*)([a-zA-Z])");
fseq_b_re = re.compile(
	bytes([
		*b"(",
		page.find("⇉"),
		*b"|",
		page.find("⇈"),
		*b")",
		*b"([",
		*casttypes_b,
		*b"])?([0-9]*)([a-zA-Z])"
	])
)

class FExtendedSequenceToken(FCommandToken):
	def __init__(self, match):
		self.source = match.group(0)
		self.arithmetic = match.group(1) in ["⇉", bytes([page.find("⇉")])]
		self.geometric  = match.group(1) in ["⇈", bytes([page.find("⇈")])]
		self.cast = casts[match.group(2)]
		self.arg_permutation = int(match.group(3) or 0)
		self.name = match.group(4)
		if self.arithmetic:
			self.seqtype = faseqtypes[self.name]
		else:
			self.seqtype = fgseqtypes[self.name]
		self.argc = self.seqtype.argc
		if self.cast[0] is None: # Indicates custom function
			self.custom = True
			self.argc += 1
		else:
			self.custom = False
	def apply(self, stack):
		args = stack.popn(self.argc)
		args = get_permutation(args, self.arg_permutation)
		arg_dict = get_arg_dict(self.seqtype, args)
		if self.arithmetic:
			stack.push(self.cast[1](FArithmeticSequence(**arg_dict, call=self.cast[0])))
		else:
			stack.push(self.cast[1](FGeometricSequence(**arg_dict, call=self.cast[0])))
	def __repr__(self):
		return "%s(%s)" % (type(self).__name__, self.source)
		
		

class FExtendedSequenceParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		if isinstance(s, str):
			return fseq_s_re.match(s)
		else:
			return fseq_b_re.match(s)
	@classmethod
	def match(cls, s):
		match = cls._match(s)
		return (match and match.endpos) or 0
	@classmethod
	def parse(cls, s):
		match = cls._match(s)
		if match:
			return FExtendedSequenceToken(match), match.endpos
		else:
			return None, 0