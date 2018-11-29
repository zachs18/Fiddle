import re

from parse import FToken, FParser, FParserSingleton
from fstring import FChar, FByte, FString, FUnicode, FBytes
from stack import Stack
from encoding import page, cmd_ord

class FCharToken(FToken):
	def __init__(self, value):
		self.value = FChar(value)
	def apply(self, stack):
		stack.push(self.value)
	def __repr__(self):
		return "FCharToken('" + repr(self.value) + "')"

class FByteToken(FToken):
	def __init__(self, value):
		self.value = FByte(value)
	def apply(self, stack):
		stack.push(self.value)
	def __repr__(self):
		return "FByteToken(" + repr(self.value) + ")"

class FUnicodeToken(FToken):
	def __init__(self, tokens, source=None):
		self.tokens = tokens
		self.source = source
	def apply(self, stack):
		stack.push(FUnicode(t.value for t in self.tokens))
	def __repr__(self):
		return "FUnicodeToken(\"" + "".join(repr(t.value) for t in self.tokens) + "\", " + repr(self.source) + ")"

class FBytesToken(FToken):
	def __init__(self, tokens, source=None):
		self.tokens = tokens
		self.source = source
	def apply(self, stack):
		stack.push(FBytes(t.value for t in self.tokens))
	def __repr__(self):
		return "FBytesToken('" + "".join(repr(t.value)[2:-1] for t in self.tokens) + "', " + repr(self.source) + ")"

def next_char(s):
	"""
	Used in FUnicodeParser
	Returns FCharToken, length used, rest of string
	"""
	
	

class FUnicodeParser(FParserSingleton):
	@classmethod
	def _match(cls, s):
		_s = s
		if isinstance(s, str):
			start = '"'
			end = '"'
			newline = '\n'
			escape = '\\'
			if not s.startswith(start):
				return [], 0
			length = len(start)
			s = s[len(start):]
			tokens = []
			while s and (not s.startswith(end)) and (not s.startswith(newline)):
				#print(s)
				if not s.startswith(escape):
					tokens.append(FCharToken(s[0]))
					s = s[1:]
					length += 1
				else:
					s = s[len(escape):]
					s += len(escape)
					if not s: # no more characters
						tokens.append(FCharToken(escape))
					elif s.startswith('\n'): # pass
						s = s[1:]
						length += 1
					elif s.startswith('n'):
						tokens.append(FCharToken('\n'))
						s = s[1:]
						length += 1
					elif s.startswith(end):
						tokens.append(FCharToken(end))
						s = s[len(end):]
						length += len(end)
					else:
						tokens.append(FCharToken(escape))
						s = s[len(escape):]
						length += len(escape)
			if s and s.startswith(end): # newlines are not 'eaten', closing quotes are
				length += len(end)
				s = s[len(end):]
			return tokens, length
						
		else:
			start = page.find('"')
			end = page.find('"')
			newline = page.find('\n')
			escape = page.find('\\')
			ordinal, length = cmd_ord(s)
			if ordinal != start:
				return [], 0
			s = s[length:]
			tokens = []
			ordinal, l = cmd_ord(s)
			while s and ordinal != end and ordinal != newline:
				if not l:# special encoding (241-255)
					if s[0] == 248: # integer encoding, add to string as decimal without spaces
						import int_rep
						match = int_rep.int_rep_b_re.match(s[1:])
						if match:
							num = int_rep.bytes_to_int(s[1:1+match.end()])
							numstr = str(num)
							for c in numstr:
								tokens.append(FCharToken(c))
							l = 1 + match.end()
							length += l
							s = s[l:]
						else:
							raise TypeError("Unrecognized special encoding in FUnicode")
					else:
						raise TypeError("Unrecognized special encoding in FUnicode")
				elif ordinal != escape:
					tokens.append(FCharToken(ordinal))
					s = s[l:]
					length += l
				else:
					s = s[l:]
					length += l
					if not s: # no more bytes
						tokens.append(FCharToken(escape))
					elif s[0] == newline:
						pass
						s = s[1:]
					elif s[0] == page.find('n'):
						tokens.append(FCharToken('\n'))
						s = s[1:]
					elif s[0] == end:
						tokens.append(FCharToken(end))
						s = s[1:]
					else: # \(byte) -> chr(byte value)
						tokens.append(FCharToken(chr(s[0])))
						s = s[1:]
				ordinal, l = cmd_ord(s)
			if s and ordinal == end: # newlines are not 'eaten', closing quotes are
				length += l
				s = s[l:]
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
		return FUnicodeToken(tokens, s[:length]), length
		