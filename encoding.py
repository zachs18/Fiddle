from abc import ABC, abstractmethod
import re

import fnumeric

lines = [
	"         \t\n     ", # 0x0_
	"                ", # 0x1_
	" !\"#$%&'()*+,-./", # 0x2_
	"0123456789:;<=>?", # 0x3_
	"@ABCDEFGHIJKLMNO", # 0x4_
	"PQRSTUVWXYZ[\\]^_", # 0x5_
	"`abcdefghijklmno", # 0x6_
	"pqrstuvwxyz{|}~ ", # 0x7_
	"≠≤≥→↣↦↠⇉⇶↑↥↟⇈   ", # 0x8_
	"                ", # 0x9_
	" ¡¢£¤¥¦§¨©ª«¬ ®¯", # 0xa_
	"°±²³´µ¶·¸¹º»¼½¾¿", # 0xb_
	#0123456789abcdef
]

for i in range(12):
	if len(lines[i]) != 16:
		raise ValueError("Line %d in codepage is not of length 16." % i)
	
page = ''.join(lines)

def cmd_ord(bs):
	"""
	returns the integer ordinal of the (possibly multibyte)  character representation, and the number of bytes used
	OR -1, 0 if the bytestring does not start with a (possibly multibyte)  character representation
	"""
	try:
		head = bs[0]
		if head < 0b11000000: # 1-byte paged character
			return ord(page[head]), 1
		elif head < 0b11100000: # 2-byte nonpaged character (no offset: [0, 8192))
			return bs[1] + 256*(head-192), 2
		elif head < 0b11110000: # 3-byte nonpaged character (no offset: [0, 1048576))
			return bs[2] + 256*bs[1] + 256*256*(head-224), 3
		elif head == 0b11110000: # 4-byte nonpaged character (no offset: [0, 1114111))
			return bs[3] + 256*bs[2] + 256*256*bs[1], 4
	except IndexError:
		pass
	# error or special encoding (int literal, etc)
	return -1, 0
		
def encode(char_or_code):
	if isinstance(char_or_code, str) and char_or_code in page:
		return bytes([page.find(char_or_code)])
	code = ord(char_or_code) if isinstance(char_or_code, str) else char_or_code
	if code < 8192:
		return bytes([192 + code//256, code%256])
	elif code < 1048576:
		return bytes([224 + code//256//256, code//256 % 256, code%256])
	else: # elif code < 1114112: # unicode limit
		return bytes([240, code//256//256 % 256, code//256 % 256, code%256])