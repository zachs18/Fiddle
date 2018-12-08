
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fseqcommandscommon import SeqType

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
