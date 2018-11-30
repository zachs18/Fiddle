import re

from parse import FToken, FParser, FParserSingleton, parse, parse_one
from fcommand import CallType, FCommandToken, FCommandParser
from fiter import FIterable, FIteratorZip, FIteratorRepeat
from flist import FList
from stack import Stack
import state

class FVectorizedCommandToken(FCommandToken):
	def __init__(self, cmdtok, depth):
		self.cmdtok = cmdtok
		self.call = cmdtok.call
		self.func = cmdtok.func
		print(self.func)
		self.depth = depth
	def _apply(self, *args):
		lengths = [-1 for _ in args]
		for i in range(len(args)):
			if isinstance(args[i], FIterable):
				lengths[i] = args[i].length()
		if all(i == -1 for i in lengths):
			return self.func(*args)
		elif len(set(lengths) - {-1}) > 1: # More than one length iterable
				raise ValueError("Multiple iterator lengths", lengths, args)
		else:
			return FList(FIteratorZip(((args[i] if lengths[i] != -1 else FIteratorRepeat([args[i]])) for i in range(len(args))), call=self._apply))
	def apply(self, stack):
		if self.call[0] == CallType.basic:
			args = stack.popn(self.call[1])
			ret = self._apply(*args)
			stack.push(ret)
	def __repr__(self):
		return "FVectorizedCommandToken(" + ("v"*self.depth if self.depth < float('inf') else 'V') + self.cmdtok.name + ")"

class FVectorizedParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		if isinstance(s, str):
			start_single = 'v'
			start_full = 'V'
		else:
			start_single = b'v'[0]
			start_full = b'V'[0]
		if s[0] not in [start_single, start_full]:
			return None, 0, 0
		depth = 1 if s[0] == start_single else float('inf')
		length = 1
		s = s[1:]
		toks, leng, s = parse_one(s)
		if len(toks) != 1:
			return None, 0, 0
		tok = toks[0]
		if isinstance(tok, FVectorizedCommandToken): # because recursion (parse_one above), we don't need 'while'
			depth += tok.depth
			tok = tok.cmdtok
		if hasattr(tok, "call") and \
			isinstance(tok.call, tuple) and \
			isinstance(tok.call[0], CallType):
			return tok, depth, length+leng
		return tok, 0, 0
		
	@classmethod
	def match(cls, s):
		# returns length
		_, _, length = cls._match(s)
		return length
	@classmethod
	def parse(cls, s):
		cmdtok, depth, length = cls._match(s)
		if not length:
			raise ValueError
		return FVectorizedCommandToken(cmdtok, depth), length
		