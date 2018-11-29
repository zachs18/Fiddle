from abc import abstractmethod

from fnumeric import FInteger, FNumber
from flist import FList, FListIterator, InfiniteLengthException
from fiter import FIterable, FIterator, FIteratorProxy, FInfiniteIteratorProxy

class FString(FList):
	def __new__(cls, *args):
		if cls is not FString: # subclasses that haven't overridden __new__
			return object.__new__(cls)
		
		if len(args) <= 1:
			string = args[0] if len(args) else 0
		else:
			raise TypeError("FString takes at most 1 argument")
		
		# FString() directly
		if isinstance(string, bytes):
			return object.__new__(FBytes)
		elif isinstance(string, str):
			return object.__new__(FUnicode)
		elif isinstance(string, FIterable):
			_s = iter(string.copy())
			_c = next(_s)
			if isinstance(_s, FByte):
				return object.__new__(FBytes)
			else:
				return object.__new__(FUnicode)		
		else:
			raise TypeError(string)
	def push(self, value):
		raise TypeError("FStrings are immutable")
	def pop(self, index):
		raise TypeError("FStrings are immutable")


class FChar(FInteger):
	def __new__(cls, value='\x00'):
		self = object.__new__(cls)
		if isinstance(value, str):
			self.value = ord(value)
		elif isinstance(value, bytes):
			self.value = ord(value.encode())
		elif isinstance(value, (int, FNumber)): # includes FChar and FByte
			self.value = int(value)
		elif isinstance(value, FUnicode):
			if value.length() != 1:
				raise ValueError(value)
			self.value = value.list[0]
		elif isinstance(value, FBytes):
			_value = value.encode()
			if _value.length() != 1:
				raise ValueError(value)
			self.value = _value.list[0]
		else:
			raise TypeError(value)
		if self.value < 0:
			raise ValueError(value)
		return self
	def __str__(self):
		try:
			return chr(self.value)
		except (ValueError, OverflowError):
			return '?'
	def __repr__(self):
		try:
			return repr(chr(self.value))[1:-1] # get rid of ''
		except (ValueError, OverflowError):
			if self.value.bit_length() <= 32: # 1114112 - 2**32-1
				return '\\U' + hex(self.value)[2:].rjust(8, '0')
			elif self.value.bit_length() <= 64: # 2**32 - 2**64-1
				return '\\V' + hex(self.value)[2:].rjust(16, '0')
			else:
				raise ValueError("%d is too big" % self.value)
	def encode(self, encoding='utf-8', errors='strict'):
		if encoding == 'utf-8':
			if self.value < 2**7:
				return FBytes([self.value])
			elif self.value < 2**11: # 2 byte
				return FBytes([192 + self.value//64, 128 + self.value % 64])
			elif self.value < 2**16: # 3 byte
				return FBytes([224 + self.value//64//64, 128 + self.value//64 % 64, 128 + self.value % 64])
			elif self.value <= 1114111: # 4 byte, unicode limit
				return FBytes([240 + self.value//64//64//64, 128 + self.value//64//64 % 64, 128 + self.value//64 % 64, 128 + self.value % 64])
			elif self.value < 2**21 and 'big' in errors: # 4 byte
				return FBytes([240 + self.value//64//64//64, 128 + self.value//64//64 % 64, 128 + self.value//64 % 64, 128 + self.value % 64])
			elif self.value < 2**26 and 'big' in errors: # 5 byte
				return FBytes([248 + self.value//64//64//64//64, 128 + self.value//64//64//64 % 64, 128 + self.value//64//64 % 64, 128 + self.value//64 % 64, 128 + self.value % 64])
			elif self.value < 2**31 and 'big' in errors: # 6 byte
				return FBytes([252 + self.value//64//64//64//64//64, 128 + self.value//64//64//64//64 % 64, 128 + self.value//64//64//64 % 64, 128 + self.value//64//64 % 64, 128 + self.value//64 % 64, 128 + self.value % 64])
			elif self.value < 2**36 and 'big' in errors: # 7 byte
				return FBytes([254, 128 + self.value//64//64//64//64//64 % 64, 128 + self.value//64//64//64//64 % 64, 128 + self.value//64//64//64 % 64, 128 + self.value//64//64 % 64, 128 + self.value//64 % 64, 128 + self.value % 64])
			else:
				if 'ignore' in errors:
					return FBytes()
				else:
					raise ValueError("%d is too big for UTF-8 encoding" % self.value)
		elif encoding == 'fiddle':
			import encoding as ec
			if self.value <= 1114111 and chr(self.value) in ec.page:
				return FBytes([ec.page.find(chr(self.value))])
			elif self.value < 2**13: # 2 bytes
				return FBytes([192 + self.value//256, self.value % 256])
			elif self.value < 2**20: # 3 bytes
				return FBytes([224 + self.value//256//256, self.value//256 % 256, self.value % 256])
			elif self.value <= 1114111: # fiddle can only encode unicode
				return FBytes([240 + self.value//256//256//256, self.value//256//256 % 256, self.value//256 % 256, self.value % 256])
			else:
				if 'ignore' in errors:
					return FBytes()
				else:
					raise ValueError("%d is too big for Fiddle encoding" % self.value)
		else:
			raise ValueError(encoding)
	def __iter__(self):
		return FListIterator([self])
		
		
	
class FUnicode(FString):
	def __init__(self, contents=None):
		if contents is None:
			self.list = []
			self.gen = None
			self._inf = False
		elif isinstance(contents, FUnicode):
			_self = contents.copy()
			self.list = _self.list
			self.gen = _self.gen
			self._inf = _self._inf
		elif isinstance(contents, FChar):
			self.list = [contents]
			self.gen = None
			self._inf = False
		elif isinstance(contents, FBytes) and contents._inf:
			self.list = []
			self.gen = contents._decode()
			self._inf = True
		elif isinstance(contents, bytes) or isinstance(contents, FBytes):
			self.list = [FChar(c) for c in contents.decode()]
			self.gen = None
			self._inf = False
		elif isinstance(contents, FIterable) and contents._inf:
			self.list = []
			self.gen = FInfiniteIteratorProxy(iter(contents), call=FChar)
			self._inf = True
		elif hasattr(contents, "__iter__"):
			self.list = [FChar(c) for c in contents]
			self.gen = None
			self._inf = False
		elif hasattr(contents, "__str__"):
			self.list = [FChar(c) for c in str(contents)]
			self.gen = None
			self._inf = False
		else:
			raise TypeError("%r cannot be converted to FUnicode" % contents)
	def __str__(self):
		if self._inf:
			self._fill(20)
			return '"' + ''.join(repr(i) for i in self.list) + '..."'
		return '"' + ''.join(repr(i) for i in self.list) + '"'
	def __repr__(self):
		if self._inf:
			self._fill(20)
			return '"' + ''.join(repr(i) for i in self.list) + '..."'
		return '"' + ''.join(repr(i) for i in self.list) + '"'
	def _encode(self, encoding='utf-8', errors='strict'): # iterator
		for c in self:
			yield from c.encode(encoding, errors)
	def encode(self, encoding='utf-8', errors = 'strict'):
		if self._inf:
			return FBytes(FInfiniteIteratorProxy(self.copy._encode(encoding, errors)))
		else:
			return FBytes(self._encode(encoding, errors))
		
			
		
	
class FByte(FInteger):
	def __init__(self, value='\x00'):
		if isinstance(value, (str, bytes)):
			self.value = ord(value)
		elif isinstance(value, (int, FNumber)): # includes FChar and FByte
			self.value = int(value)
		elif isinstance(value, FString):
			if value.length() != 1:
				raise ValueError(value)
			self.value = value.list[0]
		else:
			raise TypeError(value)
		if self.value < 0 or self.value > 255:
			raise ValueError(value)
	def __bytes__(self):
		return bytes([self.value])
	def __repr__(self):
		return repr(bytes(self))
	def __iter__(self):
		return FListIterator([self])

class FBytes(FString):
	def __init__(self, contents=None):
		if contents is None:
			self.list = []
			self.gen = None
			self._inf = False
		elif isinstance(contents, FBytes):
			_self = contents.copy()
			self.list = _self.list
			self.gen = _self.gen
			self._inf = _self._inf
		elif isinstance(contents, FByte):
			self.list = [contents]
			self.gen = None
			self._inf = False
		elif isinstance(contents, FChar):
			self.list = contents.encode().list
			self.gen = None
			self._inf = False
		elif isinstance(contents, FUnicode) and contents._inf:
			self.list = []
			self.gen = contents._encode()
			self._inf = True
		elif isinstance(contents, str) or isinstance(contents, FUnicode):
			self.list = [FByte(c) for c in contents.encode()]
			self.gen = None
			self._inf = False
		elif isinstance(contents, FIterator) and contents._inf:
			self.list = []
			self.gen = FInfiniteIteratorProxy(contents, call=FByte)
			self._inf = True
		elif hasattr(contents, "__iter__"):
			self.list = [FByte(c) for c in contents]
			self.gen = None
			self._inf = False
		elif hasattr(contents, "__bytes__"):
			self.list = [FByte(c) for c in bytes(contents)]
			self.gen = None
			self._inf = False
		elif hasattr(contents, "__str__"):
			self.list = [FByte(c) for c in str(contents).encode()]
			self.gen = None
			self._inf = False
		else:
			raise TypeError("%r cannot be converted to FUnicode" % contents)
	def __repr__(self):
		self._fill()
		return 'b"' + ''.join(repr(i)[2:-1] for i in self) + '"' # [2:-1] to get rid of b''
	def _decode(self, encoding, errors): # iterator
		i=0
		if encoding == 'utf-8':
			def decode_rest(self, start, length): # start is i+1, length is the length left, so 1 for starting 2-byte
				if not 0b10000000 <= self[i+1] < 0b11000000:
					if 'ignore' not in errors:
						raise ValueError("%r at position %d is an invalid utf-8 continuation byte" % (self[start], start))
					else:
						return -start # to skip
				elif length>1:
					val = decode_rest(self, start+1, length-1)
					if val < 0:
						return val
				else:
					val = 0
				val += (self[start].value-128)*64**length
				return val
			while True:
				try:
					if self[i].value < 0b10000000:
						yield FChar(self[i].value)
						i += 1
					elif self[i].value < 0b11000000:
						if 'ignore' not in errors:
							raise ValueError("%r at position %d is an invalid utf-8 start byte" % (self[i].value, i))
						else:
							i += 1
					elif self[i].value < 0b11100000: # 2 byte
						val = decode_rest(self, i+1, 1)
						if val < 0:
							i -= val
						else:
							val += (self[i].value-224)*64
							yield FChar(val)
							i += 2
					elif self[i].value < 0b11110000: # 3 byte
						val = decode_rest(self, i+1, 2)
						if val < 0:
							i -= val
						else:
							val += (self[i].value-224)*64**2
							yield FChar(val)
							i += 3
					elif self[i].value < 0b11111000: # 4 byte
						val = decode_rest(self, i+1, 3)
						if val < 0:
							i -= val
						else:
							val += (self[i].value-224)*64**3
							if val > 1114111 and 'big' not in errors:
								if 'ignore' not in errors:
									raise ValueError("%r at positions %d-%d is too large for a unicode character when decoded" % (self[i:i+4], i, i+3))
								else:
									i += 4
							else:
								yield FChar(val)
								i += 4
					elif self[i].value < 0b11111100: # 5 byte
						val = decode_rest(self, i+1, 4)
						if val < 0:
							i -= val
						else:
							val += (self[i].value-224)*64**4
							if val > 1114111 and 'big' not in errors:
								if 'ignore' not in errors:
									raise ValueError("%r at positions %d-%d is too large for a unicode character when decoded" % (self[i:i+4], i, i+3))
								else:
									i += 5
							else:
								yield FChar(val)
								i += 5
					elif self[i].value < 0b11111110: # 6 byte
						val = decode_rest(self, i+1, 5)
						if val < 0:
							i -= val
						else:
							val += (self[i].value-224)*64**5
							if val > 1114111 and 'big' not in errors:
								if 'ignore' not in errors:
									raise ValueError("%r at positions %d-%d is too large for a unicode character when decoded" % (self[i:i+4], i, i+3))
								else:
									i += 6
							else:
								yield FChar(val)
								i += 6
					elif self[i].value == 0b11111110: # 7 byte
						val = decode_rest(self, i+1, 6)
						if val < 0:
							i -= val
						else:
							val += (self[i].value-224)*64**6
							if val > 1114111 and 'big' not in errors:
								if 'ignore' not in errors:
									raise ValueError("%r at positions %d-%d is too large for a unicode character when decoded" % (self[i:i+4], i, i+3))
								else:
									i += 7
							else:
								yield FChar(val)
								i += 7
					else: # self[i].value == 255:
						if 'ignore' not in errors:
							raise ValueError("b'\xff' at position %d an invalid utf-8 start byte" % i)
						else:
							i += 1
				except IndexError:
					if 'ignore' in errors:
						raise StopIteration
					else:
						raise ValueError("multibyte sequence interrupted by end-of-sequence")
		elif encoding == 'fiddle':
			import encoding as ec
			def decode_rest(self, start, length): # start is i+1, length is the length left, so 1 for starting 2-byte
				if length>1:
					val = decode_rest(self, start+1, length-1)
				else:
					val = 0
				val += (self[start].value)*256**length
				return val
			while i < self.length():
				try:
					if self[i].value < 0b11000000: # 1 byte paged
						yield FChar(ec.page[self[i].value])
						i += 1
					elif self[i].value < 0b11100000: # 2 byte
						yield FChar((self[i].value - 192)*256 + decode_rest(self, i+1, 1))
						i += 2
					elif self[i].value < 0b11110000: # 3 byte
						yield FChar((self[i].value - 224)*256**2 + decode_rest(self, i+1, 2))
						i += 3
					elif self[i].value == 0b11110000: # 4 byte
						yield FChar(decode_rest(self, i+1, 3))
						i += 4
					elif self[i].value == 0b11111000: # integer encoding
						i += 1
						head = bs[i].value
						for j in range(9):
							if head >= 256-2**j:
								length = 9-j # 7 -> 2, 6 -> 3
								break
						if length == 9: # 255
							if 'ignore' not in errors:
								raise ValueError("b'\xff' is not a valid integer representation start byte")
							else:
								i += 1
						else:
							head = head + 2**(9-length) - 256 # get rid of leading bits
							bs = bytes([head]) + bytes(self[i+1:i+length])
							yield from FUnicode(' '+ str(int.from_bytes(bs, 'big') + sum(2**(7*i) for i in range(1,length))) + ' ')
							i += length
					else:
						if 'ignore' in errors:
							i += 1
						else:
							raise ValueError("unused special encoding byte %r at position %d" % (self[i], i))
				except IndexError:
					if 'ignore' in errors:
						raise StopIteration
					else:
						raise ValueError("multibyte sequence interrupted by end-of-sequence")
				
					
						
			
	def decode(self, encoding='utf-8', errors='strict'):
		if self._inf:
			return FBytes(FInfiniteIteratorProxy(self.copy._decode()))
		else:
			return FBytes(self._decode())
