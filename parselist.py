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
			start = b'['[0]
			end = b']'[0]
			newline = b'\n'[0]
		if s[0] != start:
			return [], 0
		length = 1
		s = s[1:]
		tokens = []
		while s and s[0] != end and s[0] != newline:
			toks, leng, s = parse_one(s)
			length += leng
			tokens += toks
		if s and s[0] == end: # newlines are not 'eaten', closing brackets are
			length += 1
			s = s[1:]
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
		