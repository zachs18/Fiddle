import re

from parse import FToken, FParser, FParserFactory
from encoding import page
from fnumeric import FNumber, FInteger, FFloat, FRational, FComplex, FBool
from fractions import Fraction # if state.float_parse is False
import state

overbar_s = '\u0305'
overbar_b = bytes([page.find(overbar_s)])

class FNumberToken(FToken):
	def __init__(self, value):
		self.value = value
	def apply(self, stack):
		stack.push(self.value)
	def __repr__(self):
		return "FNumberToken(%s(%r))" % (type(self.value).__name__, self.value)

class FNumberParser(FParser):
	def __init__(self, descriptor, regexes, parser):
		# descriptor is like 'decimal_int', regex is a regex to match, parser parses that regex's match
		self.descriptor = descriptor
		self.regexes = regexes
		self.parser = parser
	def _match(self, s):
		for r in self.regexes:
			if isinstance(s, type(r.pattern)): # Don't try to match a str to a bytes re & vice versa
				match = r.match(s)
				if match:
					return match
		return None
	def match(self, s):
		match = self._match(s)
		if match:
			return match.end()
		return 0
	def parse(self, s):
		match = self._match(s)
		if not match:
			raise ValueError
		length = match.end()
		return self.parser(match), length
	def __repr__(self):
		return "FNumberParser(%s)" % self.descriptor

class FNumberParserFactory(FParserFactory):
	def __init__(self, descriptor, *res):
		self.descriptor = descriptor
		self.regexes = res
	def __call__(self, parser):
		return FNumberParser(self.descriptor, self.regexes, parser)

zero_int_s_re = re.compile( r'0')
zero_int_b_re = re.compile(br'0')
# 0 : match zero
# we don't need to care about matching part of another int, as the parser is greedy (takes the longest match)
# and any conflicting match would be longer
@FNumberParserFactory('zero_int', zero_int_s_re, zero_int_b_re)
def zero_int_parser(match):
	return FNumberToken(FInteger(0))


ten_power_s_re = re.compile( r'(-)?e([+-]?\d+)')
ten_power_b_re = re.compile(br'(-)?e([+-]?\d+)')
# (-)? : '-' if negative, None if not
# e : lowercase e
# (-)? : '-' if abs()<1, None if not
# (\d+) : sequence of decimal digits
@FNumberParserFactory('ten_power', ten_power_s_re, ten_power_b_re)
def ten_power_parser(match):
	groups = match.groups()
	if groups[0]:
		mul = -1
	else:
		mul = 1
	power = int(groups[1])
	if state.float_parse or power >= 0:
		return FNumberToken(FNumber(mul*10**power)) # positive -> int, negative -> float
	else:
		return FNumberToken(FRational(mul, 10**-int(groups[1]))) # negative -> rational

# nrp = no radix point
# groups:
#  0: (-)? : '-' or None
#     0b/0/0x : base prefix
#  1: <digits> : decimal and octal cannot start with 0, binary and hex can
#     (?!<digit>) : make sure the parser doesn't stop short (non-capturing group) #TODO: not needed, parser is greedy
#  2: (e([+-]?\d+)) : scientific-notation exponent
#  3:   ([+-]?\d+) : the actual number for the power
def nrp_parser(match, base):
	groups = match.groups()
	if groups[0]:
		num = -1
	else:
		num = 1
	num *= int(groups[1], base)
	if groups[3]:
		power = int(groups[3])
		if power >= 0:
			num *= base**power
		elif state.float_parse:
			num /= base**(-power)
		else:
			num *= Fraction(1, base**(-power))
	return FNumberToken(FNumber(num))

decimal_nrp_s_re = re.compile( r'(-)?([1-9]\d*)(?![\d.])(e([+-]?\d+))?')
decimal_nrp_b_re = re.compile(br'(-)?([1-9]\d*)(?![\d.])(e([+-]?\d+))?')
# (-)? : '-' if negative, None if not
# ([1-9]\d*) : sequence of decimal digits that isn't just 0 or multiple 0s 
#              (to not match oct (077), hex (0xff), or bin (0b11)
#              (multiple 0s is multiple imdividual 0s)
# (?![\d\.]) : ... not followed by a decimal point or another digit (to not match float representations)
# (e([+-]?\d+))? : optional 10-based, base-10 exponent
@FNumberParserFactory('decimal_nrp', decimal_nrp_s_re, decimal_nrp_b_re)
def decimal_nrp_parser(match):
	return nrp_parser(match, base=10)


binary_nrp_s_re = re.compile( r'(-)?0b(0|1[01]*)(?![01.])(e([+-]?\d+))?')
binary_nrp_b_re = re.compile(br'(-)?0b(0|1[01]*)(?![01.])(e([+-]?\d+))?')
# (-)? : '-' if negative, None if not
# 0b : '0b'
# (0|1[01]*) : sequence of binary digits that only starts with 0 if it is '0'
# (?![\d\.]) : ... not followed by a radix point or another digit (to not match float representations)
# (e([+-]?\d+))? : optional 2-based, base-10 exponent
@FNumberParserFactory('binary_nrp', binary_nrp_s_re, binary_nrp_b_re)
def binary_nrp_parser(match):
	return nrp_parser(match, base=2)


octal_nrp_s_re = re.compile( r'(-)?0([1-7][0-7]*)(?![0-7.])(e([+-]?\d+))?')
octal_nrp_b_re = re.compile(br'(-)?0([1-7][0-7]*)(?![0-7.])(e([+-]?\d+))?')
# (-)? : '-' if negative, None if not
# 0 : '0'
# ([1-7][0-7]*) : sequence of octal digits that isn't just 0 or multiple 0s
#                 (multiple 0s is multiple imdividual 0s)
# (?![\d\.]) : ... not followed by a radix point or another digit (to not match float representations)
# (e([+-]?\d+))? : optional 8-based, base-10 exponent
@FNumberParserFactory('octal_nrp', octal_nrp_s_re, octal_nrp_b_re)
def octal_nrp_parser(match):
	return nrp_parser(match, base=8)



hexadecimal_lower_nrp_s_re = re.compile( r'(-)?0x(0|[1-9a-f][\da-f]*)(?![\da-f.])(p([+-]?\d+))?')
hexadecimal_lower_nrp_b_re = re.compile(br'(-)?0x(0|[1-9a-f][\da-f]*)(?![\da-f.])(p([+-]?\d+))?')
hexadecimal_upper_nrp_s_re = re.compile( r'(-)?0X(0|[1-9A-F][\dA-F]*)(?![\dA-F.])(p([+-]?\d+))?')
hexadecimal_upper_nrp_b_re = re.compile(br'(-)?0X(0|[1-9A-F][\dA-F]*)(?![\dA-F.])(p([+-]?\d+))?')
#TODO: should upper's exponent 'p' be 'P'?
# (-)? : '-' if negative, None if not
# 0x or 0X : '0x' or '0X'
# (0|[1-9a-f][\da-f]*) : sequence of hexadecimal digits that only starts with 0 if it is '0'
# (?![\d\.]) : ... not followed by a radix point or another digit (to not match float representations)
# (e([+-]?\d+))? : optional 16-based, base-10 exponent
@FNumberParserFactory(
	'hexadecimal_nrp',
	hexadecimal_lower_nrp_s_re,
	hexadecimal_lower_nrp_b_re,
	hexadecimal_upper_nrp_s_re,
	hexadecimal_upper_nrp_b_re
)
def hexadecimal_nrp_parser(match):
	return nrp_parser(match, base=16)

def _digit_helper(c, base):
	if isinstance(c, str):
		return int(c, base)
	else:
		return int(chr(c), base)

# float = has a radix point
# groups:
#  0: (-)? : '-' or None
#     ''/0b/0/0x : base prefix
#  1: (<digits>).                         : integral part
#  2:            (<digits>)              : fractional part (optional)
#  3:                      (\u0305(<digits>)) : repeated fractional part
#  4:                             (<digits>)  : digits of repeated fractional part
#  5: (e([+-]?\d+)) : scientific-notation exponent
#  6:   ([+-]?\d+) : the actual number for the power
def float_parser(match, base):
	groups = match.groups()
	if groups[0]:
		sign = -1
	else:
		sign = 1
	power = 0
	if groups[1]: # has an integer part (even if 0)
		num = int(groups[1], base)
		if groups[2]:
			num = num*base**len(groups[2]) + int(groups[2], base)
			power -= len(groups[2])
		if groups[4]:
			num += Fraction(int(groups[4], base), base**len(groups[4])-1)
	elif groups[2]: # no integer part
		num = int(groups[2], base)
		power -= len(groups[2])
		if groups[4]:
			num += Fraction(int(groups[4], base), base**len(groups[4])-1)
	elif groups[4]: # no integer OR finite fractional part
		num = Fraction(int(groups[4], base), base**len(groups[4])-1)
	else:
		num = 0
	if groups[6]:
		power += int(groups[6])
	if power >= 0:
		num *= base**power
		num /= base**(-power) # e.g. 51/10 != 51*0.1 because 0.1 != 1/10
	else:
		num *= Fraction(1, base**(-power))
	if state.float_parse and num % 1:
		return FNumberToken(FFloat(sign*num))
	else:
		return FNumberToken(FNumber(sign*num))
	

#decimal_float_s_re = re.compile( r'(-)?(\d+\.\d*|\d*\.\d+)(e([+-]?\d+))?')
# this ^ one matches 001. etc
decimal_float_s_re = re.compile( r'(-)?(?!0\d)(\d*)\.(\d*)('+overbar_s+ r'(\d+))?(e([+-]?\d+))?')
decimal_float_b_re = re.compile(br'(-)?(?!0\d)(\d*)\.(\d*)('+overbar_b+br'(\d+))?(e([+-]?\d+))?')
# (-)? : '-' if negative, None if not
# (?!0\d) : do not match possible octal
# (\d+\.\d*|\d*\.\d+) : floating point decimal number with at leas one (possibly zero) digit
# (e([+-]?\d+))? : optional 10-based, base-10 exponent 
@FNumberParserFactory('decimal_float', decimal_float_s_re, decimal_float_b_re)
def decimal_float_parser(match):
	return float_parser(match, base=10)


binary_float_s_re = re.compile( r'(-)?0b([01]*)\.([01]*)('+overbar_s+ r'([01]+))?(e([+-]?\d+))?')
binary_float_b_re = re.compile(br'(-)?0b([01]*)\.([01]*)('+overbar_b+br'([01]+))?(e([+-]?\d+))?')
# (-)? : '-' if negative, None if not
# 0b : '0b'
# ([01]*) : sequence of binary digits
# (e([+-]?\d+))? : optional 2-based, base-10 exponent
@FNumberParserFactory('binary_float', binary_float_s_re, binary_float_b_re)
def binary_float_parser(match):
	return float_parser(match, base=2)


octal_float_s_re = re.compile( r'(-)?0([0-7])\.([0-7]*)('+overbar_s+ r'([0-7]+))?(e([+-]?\d+))?')
octal_float_b_re = re.compile(br'(-)?0([0-7])\.([0-7]*)('+overbar_b+br'([0-7]+))?(e([+-]?\d+))?')
# (-)? : '-' if negative, None if not
# 0b : '0b'
# ([01]*) : sequence of octal digits
# (e([+-]?\d+))? : optional 2-based, base-10 exponent
@FNumberParserFactory('octal_float_s', octal_float_s_re, octal_float_b_re)
def octal_float_parser(match):
	return float_parser(match, base=8)


hexadecimal_lower_float_s_re = re.compile( r'(-)?0x([0-9a-f]*)\.([0-9a-f]*)('+overbar_s+ r'([0-9a-f]+))?(p([+-]?\d+))?')
hexadecimal_lower_float_b_re = re.compile(br'(-)?0x([0-9a-f]*)\.([0-9a-f]*)('+overbar_b+br'([0-9a-f]+))?(p([+-]?\d+))?')
hexadecimal_upper_float_s_re = re.compile( r'(-)?0X([0-9A-F]*)\.([0-9A-F]*)('+overbar_s+ r'([0-9A-F]+))?(p([+-]?\d+))?')
hexadecimal_upper_float_b_re = re.compile(br'(-)?0X([0-9A-F]*)\.([0-9A-F]*)('+overbar_b+br'([0-9A-F]+))?(p([+-]?\d+))?')
#TODO: should upper's exponent 'p' be 'P'?
# (-)? : '-' if negative, None if not
# 0x or 0X : '0x' or '0X'
# ([\da-f]*) : sequence of hexadecimal digits
# (?![\d\.]) : ... not followed by a radix point or another digit (to not match float representations)
# (e([+-]?\d+))? : optional 16-based, base-10 exponent
@FNumberParserFactory(
	'hexadecimal_float',
	hexadecimal_lower_float_s_re,
	hexadecimal_lower_float_b_re,
	hexadecimal_upper_float_s_re,
	hexadecimal_upper_float_b_re
)
def hexadecimal_float_parser(match):
	return float_parser(match, base=16)


int_rep_b_re = re.compile(
	b'''\xf8(
		[\x00-\x7f]|       # 0xxxxxxx
		[\x80-\xbf].|      # 10xxxxxx xxxxxxxx + 2**7
		[\xc0-\xdf]..|     # 110xxxxx xxxxxxxx xxxxxxxx + 2**7 + 2**14
		[\xe0-\xef]...|    # 1110xxxx xxxxxxxx xxxxxxxx xxxxxxxx + 2**7 + 2**14 + 2**21
		[\xf0-\xf7]....|   # 11110xxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx + etc.
		[\xf8-\xfb].....|  # 111110xx ...
		[\xfc-\xfd]......| # 1111110x ...
		\xfe.......)       # 11111110 ...
		# \xff does not match
	''',
	re.X
)
@FNumberParserFactory('int_rep_b', int_rep_b_re)
def int_rep_parser(match):
	import int_rep
	return FNumberToken(FNumber(int_rep.bytes_to_int(match.group(1))))
	



