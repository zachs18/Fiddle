from abc import abstractmethod
from fractions import Fraction
import math
import numbers

from fobject import FObject

class FNumber(FObject, numbers.Number):
	def __new__(cls, *args):
		if cls is not FNumber: # subclasses that haven't overridden __new__
			return object.__new__(cls)
		
		if len(args) <= 1:
			number = args[0] if len(args) else 0
		else:
			raise TypeError("FNumber takes at most 1 argument")
		
		# FNumber() directly
		if isinstance(number, FNumber): 
			return object.__new__(type(number))
		elif isinstance(number, int):
			return object.__new__(FInteger)
		elif isinstance(number, float):
			return object.__new__(FFloat)
		elif isinstance(number, Fraction):
			return object.__new__(FRational)
		elif isinstance(number, complex):
			return object.__new__(FComplex)
		else:
			raise TypeError(number)
	def copy(self):
		"""
		Return self (FNumbers are not modifiable)
		"""
		return self
	def __eq__(self, other):
		"""
		All FNumbers use self.value unless otherwise configured
		FNumbers that do not use self.value should override all magic methods
		of FNumber that use it.
		"""
		return FInteger(self.value == other)
	def __ne__(self, other):
		return FInteger(self.value != other)
	def __lt__(self, other):
		return FInteger(self.value < other)
	def __le__(self, other):
		return FInteger(self.value <= other)
	def __gt__(self, other):
		return FInteger(self.value > other)
	def __ge__(self, other):
		return FInteger(self.value >= other)
	def __pos__(self):
		return self
	def __neg__(self):
		return type(self)(-self.value)
	def __abs__(self):
		return type(self)(abs(self.value))
	def __int__(self):
		return int(self.value)
	def __index__(self):
		return int(self.value)
	def __float__(self):
		return float(self.value)
	def __complex__(self):
		return complex(self.value)
	@property
	def real(self):
		# FComplex overrides this
		return self
	@property
	def imag(self):
		# FComplex overrides this
		return FInteger(0)
	def conjugate(self):
		# FComplex overrides this
		return self
	def norm(self):
		"complex number times its conjugate"
		return self.real*self.real + self.imag*self.imag
#	@abstractmethod
	def __add__(self, other):
		return FNumber(self.value + other)
#	@abstractmethod
	def __radd__(self, other):
		return FNumber(other + self.value)
#	@abstractmethod
	def __mul__(self, other):
		return FNumber(self.value * other)
	#@abstractmethod
	def __rmul__(self, other):
		return FNumber(other * self.value)
	def __ceil__(self):
		return FInteger(self.value.__ceil__())
	def __floor__(self):
		return FInteger(self.value.__floor__())
#	@abstractmethod
	def __truediv__(self, other):
		""" int / int -> rational """
		if isinstance(self, FInteger) and isinstance(other, FInteger):
			return FRational(self, FNumber(other))
		return FNumber(self.value / other)
#	@abstractmethod
	def __rtruediv__(self, other):
		""" int / int -> rational """
		if isinstance(self, FInteger) and isinstance(other, FInteger):
			return FRational(FNumber(other), self)
		return FNumber(other / self.value)
#	@abstractmethod
	def __floordiv__(self, other):
		return self.value // other
#	@abstractmethod
	def __rfloordiv__(self, other):
		return other // self.value
#	@abstractmethod
	def __mod__(self, other):
		return self.value % other
#	@abstractmethod
	def __rmod__(self, other):
		return other % self.value
#	@abstractmethod
	def __pow__(self, other):
		return self.value ** other
#	@abstractmethod
	def __rpow__(self, other):
		return other ** self.value
#	@abstractmethod
	def __round__(self, other):
		return round(self.value, other)
#	@abstractmethod
	def __trunc__(self, other):
		return self.value.__trunc__(other)
	
	
	
		

class FInteger(FNumber, numbers.Integral):
	def __init__(self, value=0):
		self.value = int(value//1)
	def __str__(self):
		return str(self.value)
	def __repr__(self):
		return str(self.value)
	def __and__(self, other):
		return FInteger(self.value & other)
	def __rand__(self, other):
		return FInteger(other & self.value)
	def __or__(self, other):
		return FInteger(self.value | other)
	def __ror__(self, other):
		return FInteger(other | self.value)
	def __xor__(self, other):
		return FInteger(self.value ^ other)
	def __rxor__(self, other):
		return FInteger(other ^ self.value)
	def __invert__(self):
		return FInteger(~self.value)
	def __lshift__(self):
		return FInteger(self.value << other)
	def __rshift__(self):
		return FInteger(self.value >> other)
	def __rlshift__(self):
		return FInteger(other << self.value)
	def __rrshift__(self):
		return FInteger(other >> self.value)
	
		
	
class FFloat(FNumber, numbers.Real):
	def __init__(self, value=0.):
		self.value = float(value)
	def __str__(self):
		return str(self.value)
	def __repr__(self):
		return str(self.value)
	
class FRational(FNumber, numbers.Rational):
	def __init__(self, *args):
		if len(args) == 0:
			self.value = Fraction(0)
		elif len(args) == 1:
			arg = args[0]
			if isinstance(arg, (int, FInteger)):
				self.value = Fraction(int(arg))
			elif isinstance(arg, (float, FFloat)):
				self.value = Fraction(*arg.as_integer_ratio())
			elif isinstance(arg, (Fraction, FRational)):
				self.value = arg
			else:
				raise TypeError(arg)
		elif len(args) == 2:
			num, denom = args
			nmul = dmul = 1
			if isinstance(num, (int, FInteger)):
				num = int(num)
			elif isinstance(num, (float, FFloat)):
				num, dmul = num.as_integer_ratio()
			elif isinstance(num, (Fraction, FRational)):
				num, dmul = num.numerator, num.denominator
			else:
				raise TypeError(num)
			if isinstance(denom, (int, FInteger)):
				denom = int(denom)
			elif isinstance(denom, (float, FFloat)):
				denom, nmul = denom.as_integer_ratio()
			elif isinstance(denom, (Fraction, FRational)):
				denom, nmul = denom.numerator, denom.denominator
			else:
				raise TypeError(denom)
			num *= nmul
			denom *= dmul
			gcd = math.gcd(num, denom)
			num = num // gcd
			denom = denom // gcd
			if denom < 0:
				num *= -1
				denom *= -1
			elif denom == 0:
				raise ZeroDivisionError("FRational(%r, %r)" % args)
			self.value = Fraction(num, denom)
		else:
			raise TypeError("FRational takes at most 2 arguments (%d given)" % len(args))
	@property
	def numerator(self):
		return self.value.numerator
	@property
	def denominator(self):
		return self.value.denominator
	def __str__(self):
		return '('+str(self.numerator)+'/'+str(self.denominator)+')'
	def __repr__(self):
		return '('+str(self.numerator)+'/'+str(self.denominator)+')'
	"""
	def __eq__(self, other):
		if isinstance(other, (int, FInteger)):
			return self.denominator == 1 and self.numerator == other
		elif isinstance(other, (float, FFloat)):
			return (self.numerator, self.denominator) == other.as_integer_ratio()
		elif isinstance(other, (Fraction, FRational)):
			return self.numerator == other.numerator and self.denominator == other.denominator
		elif isinstance(other, (complex, FComplex)):
			return other.imag == 0 and self == other.real
		else:
			return NotImplemented
	def __lt__(self, other):
		if isinstance(other, (int, FInteger, float, FFloat, Fraction, FRational, complex, FComplex)):
			return self.value < other
		else:
			return NotImplemented
	def __le__(self, other):
		if isinstance(other, (int, FInteger, float, FFloat, Fraction, FRational, complex, FComplex)):
			return self.value <= other
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, (int, FInteger, float, FFloat, Fraction, FRational, complex, FComplex)):
			return self.value > other
		else:
			return NotImplemented
	def __ge__(self, other):
		if isinstance(other, (int, FInteger, float, FFloat, Fraction, FRational, complex, FComplex)):
			return self.value >= other
		else:
			return NotImplemented"""

class FComplex(FNumber, numbers.Complex):
	def __init__(self, *args):
		if len(args) == 0:
			self._real = FInteger(0)
			self._imag = FInteger(0)
		elif len(args) == 1:
			self._real = FNumber(args[0].real) if args[0].real else FInteger(0) # 0.0 == FInteger(0) but will 
			self._imag = FNumber(args[0].imag) if args[0].imag else FInteger(0)
		elif len(args) == 2:
			self._real = FNumber(args[0].real - args[1].imag) if args[0].real or args[1].imag else FInteger(0)
			self._imag = FNumber(args[1].real + args[0].imag) if args[0].imag or args[1].real else FInteger(0)
			self._imag = FNumber(args[1]) if args[1] else FInteger(0)
		else:
			raise TypeError("FComplex takes at most 2 arguments (%d given)" % len(args))
	def __str__(self):
		return '('+str(self._real)+'+'+str(self._imag)+'j)'
	def __repr__(self):
		return '('+str(self._real)+'+'+str(self._imag)+'j)'
	def __eq__(self, other):
		"""
		FComplex does not use self.value.
		FNumbers that do not use self.value should override all magic methods
		of FNumber that use it.
		"""
		return self.real == other.real and self.imag == other.imag
	def __ne__(self, other):
		return self.real != other.real or self.imag != other.imag
	def __lt__(self, other):
		return NotImplemented
	def __le__(self, other):
		return NotImplemented
	def __gt__(self, other):
		return NotImplemented
	def __ge__(self, other):
		return NotImplemented
	def __pos__(self):
		return self
	def __neg__(self):
		return FComplex(-self.real, -self.imag)
	def __abs__(self):
		import math
		return FFloat(math.hypot(self.real, self.imag))
	def __int__(self):
		return NotImplemented
	def __float__(self):
		return NotImplemented
	def __complex__(self):
		return complex(self.real, self.imag)
	@property
	def real(self):
		return self._real
	@property
	def imag(self):
		return self._imag
	def conjugate(self):
		return FComplex(self.real, -self.imag)
	def __add__(self, other):
		return FComplex(self.real + other.real, self.imag + other.imag)
	def __radd__(self, other):
		return self + other
	def __mul__(self, other):
		return FComplex(self.real*other.real - self.imag*other.imag, self.real*other.imag + self.imag*other.real)
	def __rmul__(self, other):
		return self*other
	def __pow__(self, other):
		if isinstance(other, numbers.Integral) and other >= 0:
			out = FComplex(1)
			for i in range(other):
				out *= self
			return out
		else:
			return FComplex(complex(self)**other)
	def __rpow__(self, other):
		return other ** complex(self)
	def __truediv__(self, other):
		if isinstance(other, numbers.Real):
			return FComplex(self.real/other, self.imag/other)
		elif isinstance(other, numbers.Complex):
			return FComplex( # a*b.conjugate()/b.norm()
				(self.real*other.real+self.imag*other.imag)/(other.real**2+other.imag**2),
				(self.imag*other.real-self.real*other.imag)/(other.real**2+other.imag**2)
			)
		else:
			return complex(self)/other
	def __rtruediv__(self, other):
		if isinstance(other, numbers.Complex):
			return other * self.conjugate() / self.norm()
		else:
			return other/complex(self)
		
	
		
	
	
			