import re

from parse import FToken, FParser, FParserSingleton, parse, parse_one
from stack import Stack

class FListToken(FToken):
	def __init__(self, tokens, source=None):
		self.tokens = tokens
		self.source = source
	def apply(self, stack):
		temp = Stack()
		for token in self.tokens:
			token.apply(temp)
		stack.push(temp.stack)
		del temp
	def __repr__(self):
		return "FListToken([" + ", ".join(repr(t) for t in self.tokens) + "], " + repr(self.source) + ")"

class FListParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		if isinstance(s, str):
			start = '['
			end = ']'
			newline = '\n'
		else:
			start = b'['
			end = b']'
			newline = b'\n'
		if not s.startswith(start):
			return [], 0
		length = len(start)
		s = s[len(start):]
		tokens = []
		while s and (not s.startswith(end)) and (not s.startswith(newline)):
			toks, leng, s = parse_one(s)
			length += leng
			tokens += toks
		if s and s.startswith(end): # newlines are not 'eaten', closing brackets are
			length += len(end)
			s = s[len(end):]
		return tokens, length
	@classmethod
	def match(cls, s):
		# returns length
		_, length = cls._match(s)
		return length
	@classmethod
	def parse(cls, s):
		tokens, length = cls._match(s)
		if not length:
			raise ValueError
		return FListToken(tokens, s[:length]), length
		