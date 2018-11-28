"""the rotate command could be two-byte, with the next byte containing the count and times, where times < count
the next byte starts at 
Rotation is done with the top item rotated to the bottom, and the others moving up one

byte value - (count, times)

(count, times) -> bin(Tr(count-2)+times-1))

00000000 - (2,1)
00000001 - (3,1)
00000010 - (3,2)
00000011 - (4,1)
00000100 - (4,2)
00000101 - (4,3)
00000110 - (5,1)
00000111
00001000
00001001
00001010
00001011
00001100
00001101
00001110
00001111
00010000
00010001
00010010
00010011
00010100
00010101
00010110
00010111
00011000
00011001
00011010
00011011
00011100
00011101
00011110
00011111
00100000
00100001
00100010
00100011
00100100
00100101
00100110
00100111
00101000
00101001
00101010
00101011
00101100
00101101
00101110
00101111
00110000
00110001
00110010
00110011
00110100
00110101
00110110
00110111
00111000
00111001
00111010
00111011
00111100
00111101
00111110
00111111
01000000
01000001
01000010
01000011
01000100
01000101
01000110
01000111
01001000
01001001
01001010
01001011
01001100
01001101
01001110
01001111
01010000
01010001
01010010
01010011
01010100
01010101
01010110
01010111
01011000
01011001
01011010
01011011
01011100
01011101
01011110
01011111
01100000
01100001
01100010
01100011
01100100
01100101
01100110
01100111
01101000
01101001
01101010
01101011
01101100
01101101
01101110
01101111
01110000
01110001
01110010
01110011
01110100
01110101
01110110
01110111
01111000
01111001
01111010
01111011
01111100
01111101
01111110
01111111 - (17,8)
10000000 - starts two byte
  BBBBBB BBBBBBBB + 2**7

10000000 00000000 - (17,9) # 128
10000001 00000000 - (29,7) # 384
10111111 11111111 - (183,41) # 16511 = 2**14-1 + 128
11000000 - starts three byte
   BBBBB BBBBBBBB BBBBBBBB + 2**7 + 2**14

11000000 00000000 00000000 - (183, 42) # 0 + 2**14 + 2**7
11011111 11111111 11111111 - (2057, 1124) # 2**21-1 + 2**14 + 2**7
#I'm not adding support for more than this, but using the same logic
11111110 00000000 00000000 00000000 00000000 00000000 00000000 00000000 - (33686278,18002679) # 567382630219904 = sum(2**(7*i) for i in range(1,7+1))
11111110 11111111 11111111 11111111 11111111 11111111 11111111 11111111 - (381116720,108043719) # 72624976668147839

11111111 could be from stack, or could use a command prefix to say from stack
"""
def Tr(x):
	return x*(x+1)//2
import math
def Tr_inv(x):
	return (-1 + int(math.sqrt(1+8*x)))//2

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
