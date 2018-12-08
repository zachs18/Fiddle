
from fnumeric import FNumber, FReal, FInteger, FFloat, FRational, FComplex, FBool
from fseqcommandscommon import SeqType

fgseqtypes = {
	#NOTE: seqtypes that seem to specify an end and a length will only actually use the length
	
	# 'a': s up (magnitude) by 2
	'a': SeqType('a', 1, 0, None, FInteger(2)),
	# 'b': s up (magnitude) by 2 length long
	'b': SeqType('b', 2, 0, None, FInteger(2), length=1),
	
	# 'c': s down (magnitude) by 2
	'c': SeqType('c', 1, 0, None, FRational(1,2)),
	# 'd': s down (magnitude) by 2 length long
	'd': SeqType('d', 2, 0, None, FRational(1,2), length=1),
	
	# 'e': s alternate sign
	'e': SeqType('e', 1, 0, None, FInteger(-1)),
	# 'f': s alternate sign length long
	'f': SeqType('f', 2, 0, None, FInteger(-1), length=1),
	
	# 'g': s, si, -s, -si loop
	'g': SeqType('g', 1, 0, None, FComplex(0, 1)),
	# 'h': s, si, -s, -si loop length long
	'h': SeqType('h', 2, 0, None, FComplex(0, 1), length=1),
	
	# 'i': 1 up/down to abs(e) exclusive
	'i': SeqType('i', 1, FInteger(1), 0, ((0,), lambda e:FInteger(2) if e.norm()>1 else FRational(1,2))),
	# 'j': 1 up/down to abs(e) exclusive length long
	'j': SeqType('j', 2, FInteger(1), 0, ((0,1), lambda e,l:abs(e)**(1/l)), length=1),
	
	# 'k': +/-1 up/down to abs(e) exclusive
	'k': SeqType('k', 1, ((0,), lambda e:e.sign()), 0, ((0,), lambda e:FInteger(2) if e.norm()>1 else FRational(1,2))),
	# 'l': 1 up/down to abs(e) exclusive length long
	'l': SeqType('l', 2, ((0,), lambda e:e.sign()), 0, ((0,1), lambda e,l:abs(e)**(1/l)), length=1),
	
	# 'm': 1 up/down to abs(e) inclusive
	'm': SeqType('m', 1, FInteger(1), 0, ((0,), lambda e:FInteger(2) if e.norm()>1 else FRational(1,2)), inclusive=True),
	# 'n': 1 up/down to abs(e) inclusive length long
	'n': SeqType('n', 2, FInteger(1), 0, ((0,1), lambda e,l:abs(e)**(1/(l-1))), length=1, inclusive=True),
	
	# 'o': +/-1 up/down to abs(e) inclusive
	'o': SeqType('o', 1, ((0,), lambda e:e.sign()), 0, ((0,), lambda e:FInteger(2) if e.norm()>1 else FRational(1,2)), inclusive=True),
	# 'p': 1 up/down to abs(e) inclusive length long
	'p': SeqType('p', 2, ((0,), lambda e:e.sign()), 0, ((0,1), lambda e,l:abs(e)**-(1/(l-1))), length=1, inclusive=True),
	
	
	
	
	# 'q': s up to e exclusive
	'q': SeqType('q', 2, 0, 1, FInteger(2)),
	# 'r': s up/down to e exclusive
	'r': SeqType('r', 2, 0, 1, ((0,1), lambda s,e:FInteger(2) if (e/s).norm() > 1 else FRational(1,2))),
	# 's': s up/down to e exclusive length long
	's': SeqType('s', 3, 0, 1, ((0,1,2), lambda s,e,l:abs(e/s)**-l), length=2),
	# 't': s down to e exclusive
	't': SeqType('t', 2, 0, 1, FRational(1,2)),
	
	# 'u': s up to e inclusive
	'u': SeqType('u', 2, 0, 1, FInteger(2), inclusive=True),
	# 'v': s up/down to e inclusive
	'v': SeqType('v', 2, 0, 1, ((0,1), lambda s,e:FInteger(2) if (e/s).norm() > 1 else FRational(1,2)), inclusive=True),
	# 'w': s up/down to e inclusive length long
	'w': SeqType('w', 3, 0, 1, ((0,1,2), lambda s,e,l:abs(e/s)**-(l-1)), length=2, inclusive=True),
	# 'x': s down to e inclusive
	'x': SeqType('x', 2, 0, 1, FRational(1,2), inclusive=True),
	
	# 'y': 1 up/down by t
	'y': SeqType('y', 1, FInteger(1), None, 0),
	# 'z': 1 up/down by t length long
	'z': SeqType('z', 2, FInteger(1), None, 0, length=1),
	
	# 'A': t up/down by t
	'A': SeqType('A', 1, 0, None, 0),
	# 'B': t up/down by t length long
	'B': SeqType('B', 2, 0, None, 0, length=1),
	
	# 'C': s up/down by t
	'C': SeqType('C', 2, 0, None, 1),
	# 'D': s up/down by t length long
	'D': SeqType('D', 3, 0, None, 1, length=2),
	
	# 'E': 1 up/down to e by t exclusive
	'E': SeqType('E', 2, FInteger(1), 0, 1),
	# 'F': +/-1 up/down to e by t exclusive
	'F': SeqType('F', 2, ((0,), lambda e:e.sign()), 0, 1),
	# 'G':   up/down by t to e length long exclusive
	'G': SeqType('G', 3, ((0,1,2), lambda e,t,l: e/t**l), 0, 1, length=2),
	
	# 'H': 1 up/down to e by t inclusive
	'H': SeqType('H', 2, FInteger(1), 0, 1, inclusive=True),
	# 'I': +/-1 up/down to e by t inclusive
	'I': SeqType('I', 2, ((0,), lambda e:e.sign()), 0, 1, inclusive=True),
	# 'J':   up/down by t to e length long inclusive
	'J': SeqType('J', 3, ((0,1,2), lambda e,t,l: e/t**(l-1)), 0, 1, length=2, inclusive=True),
	
	# 'K': normal
	'K': SeqType('K', 3, 0, 1, 2),
	# 'L':   up/down by t to e length long inclusive
	'L': SeqType('L', 3, 0, 1, 2, inclusive=True),
	
	# ...
	
	# 'X': positive powers of 2
	'X': SeqType('X', 0, FInteger(1), None, FInteger(2)),
	# 'Y': 1, -1 loop
	'Y': SeqType('Y', 0, FInteger(1), None, FInteger(-1)),
	# 'Z': 1, i, -1, -i loop
	'Z': SeqType('Z', 0, FInteger(1), None, FComplex(0,1)),
}
