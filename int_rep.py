"""
00000000 - 0
00000001 - 1
00000010 - 2
00000011 - 3
00000100 - 4
00000101 - 5
00000110 - 6
01111110 - 126
01111111 - 127
10000000 - starts two byte
  BBBBBB BBBBBBBB + 2**7

10000000 00000000 - 128
10000001 00000000 - 384
10111111 11111111 - 16511 = 2**14-1 + 128
11000000 - starts three byte
   BBBBB BBBBBBBB BBBBBBBB + 2**7 + 2**14

11000000 00000000 00000000 - 0 + 2**14 + 2**7
11011111 11111111 11111111 - 2**21-1 + 2**14 + 2**7
11111110 00000000 00000000 00000000 00000000 00000000 00000000 00000000 - 567382630219904 = sum(2**(7*i) for i in range(1,7+1))
11111110 11111111 11111111 11111111 11111111 11111111 11111111 11111111 - 72624976668147839

11111111 could be from stack, or could use a command prefix to say from stack
"""
import re

int_rep_b_re = re.compile(
	b"""
		[\x00-\x7f]|       # 0xxxxxxx
		[\x80-\xbf].|      # 10xxxxxx xxxxxxxx + 2**7
		[\xc0-\xdf]..|     # 110xxxxx xxxxxxxx xxxxxxxx + 2**7 + 2**14
		[\xe0-\xef]...|    # 1110xxxx xxxxxxxx xxxxxxxx xxxxxxxx + 2**7 + 2**14 + 2**21
		[\xf0-\xf7]....|   # 11110xxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx + etc.
		[\xf8-\xfb].....|  # 111110xx ...
		[\xfc-\xfd]......| # 1111110x ...
		\xfe.......        # 11111110 ...
		# \xff does not match
	""",
	re.X
)
	


def int_to_bytes(i):
	_i = i
	length = 1
	while i.bit_length() > 7*length: # i > 2**(7*length)
		i -= 2**(7*length)
		length += 1
	if length > 8:
		raise ValueError(_i)
	bs = i.to_bytes(length, 'big')
	head = bs[0] + sum(2**(8-j) for j in range(1,length))
	return bytes([head]) + bs[1:]
def bytes_to_int(bs):
	head = bs[0]
	for i in range(9):
		if head >= 256-2**i:
			length = 9-i # 7 -> 2, 6 -> 3
			break
	if length == 9: # 255
		return -1
	head = head + 2**(9-length) - 256 # get rid of leading bits
	bs = bytes([head]) + bs[1:length]
	return int.from_bytes(bs, 'big') + sum(2**(7*i) for i in range(1,length))
			


def Tr(x):
	return x*(x+1)//2
#import math
def sqrt(n):
	if n < 0:
		raise ValueError('sqrt of a negative number')
	x = n
	y = n >> 1 or 1
	while y < x:
		print(x,y)
		x, y = y, (y + n//y)//2
	print(x,y)
	return x
def Tr_inv(x):
	return (-1 + sqrt(1+8*x))//2

rot_cmd = b'r'
def rot_to_int(count, times):
#	return sum(range(count-1)) + times - 1
	return (count-2)*(count-1)//2 + times - 1
#	return Tr(count-2) + times - 1
def rot_to_bytes(count, times):
	out = rot_cmd # or whatever rotate command
	_num = num = rot_to_int(count, times)
	length = 1
	while num.bit_length() > (7*length): # num >= 2**(7*length)
		num -= 2**(7*length)
		length += 1
	if length > 8: # > 8
		raise ValueError(_num)
	bs = num.to_bytes(length, 'big')
	
	out += bytes([bs[0] + sum(2**(8-i) for i in range(1,length))]) + bs[1:]
	return out

#def int_to_rot(num):
#	i = 1
#	num += 1 # otherwise itr(0) returns (1,0)
#	while i <= num:
#		num -= (i-1) # the nth count has n-1 possible timeses
#		i += 1
#	return i, num
def int_to_rot(num):
	#num += 1 # otherwise itr(0) returns (1,0)
	i = Tr_inv(num)
	num -= Tr(i)
	#i = 1
	#print(Tr_inv(num))
#	print(i)
#	print(num)
	while i < num: # for residual float errors from math.sqrt
		print(1,end='')
		num -= i
		i += 1
	while num < 1: # for residual float errors from math.sqrt
		# when num is originally > about 2**105
		#print(2,end='')
		i -= 1
		num += i
	return i+2, num+1
def bytes_to_rot(bs):
	if not bs.startswith(rot_cmd):
		raise ValueError
	bs = bs.lstrip(rot_cmd)
	num = 0
	length = 1
	mask = 128
	while bs[0] >= mask:
		length += 1
		mask += 2**(8-length)
	bs = bytes([bs[0] & ~mask]) + bs[1:length]
	num += int.from_bytes(bs, 'big') + sum(2**(7*i) for i in range(1,length))
	return int_to_rot(num)
