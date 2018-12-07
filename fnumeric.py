from abc import abstractmethod
from fractions import Fraction
import math
import numbers

from fobject import FObject

class FNumber(FObject, numbers.Number):
	def __new__(cls, *args):
		if cls is not FNumber: # subclasses that haven't overridden __new__
			raise TypeError("subclasses of FNumber must override __new__ for initialization")
		
		if len(args) <= 1:
			number = args[0] if len(args) else 0
		else:
			raise TypeError("FNumber takes at most 1 argument")
		
		# FNumber() directly
		if isinstance(number, FNumber):
			if number.imag != 0:
				return FComplex.__new__(FComplex, number)
			elif number.is_integer():
				return FInteger.__new__(FInteger, number)
			elif isinstance(number, FFloat):
				return FFloat.__new__(FFloat, number)
			elif isinstance(number, FRational):
				return FRational.__new__(FRational, number)
			else:
				raise TypeError(number,type(number))
		elif isinstance(number, bool):
			return FBool.__new__(FBool, number)
		elif isinstance(number, int):
			return FInteger.__new__(FInteger, number)
		elif isinstance(number, float):
			if number.is_integer():
				return FInteger.__new__(FInteger, number)
			else:
				return FFloat.__new__(FFloat, number)
		elif isinstance(number, Fraction):
			if number.denominator == 1:
				return FInteger.__new__(FInteger, number)
			else:
				return FRational.__new__(FRational, number)
		elif isinstance(number, complex):
			if number.imag == 0:
				return FNumber.__new__(FNumber, number.real)
			else:
				return FComplex.__new__(FComplex, number)
		else:
			raise TypeError(number)
	def copy(self):
		"""
		Return self (FNumbers are not modifiable)
		"""
		return self
	@property
	@abstractmethod
	def real(self):
		pass
	@property
	@abstractmethod
	def imag(self):
		pass
	def norm(self):
		"complex number times its conjugate"
		return self.real*self.real + self.imag*self.imag
	def __bool__(self):
		return self != 0
	def eq(self, other):
		return FBool(self == other)
	def ne(self, other):
		return FBool(self != other)
	def le(self, other):
		return FBool(self <= other)
	def lt(self, other):
		return FBool(self < other)
	def ge(self, other):
		return FBool(self >= other)
	def gt(self, other):
		return FBool(self > other)
	@abstractmethod
	def is_integer(self):
		pass
	def sign(self):
		return self/abs(self) if self else FNumber(0)


class FReal(FNumber, numbers.Real):
	"""
	All FReals use self.value unless otherwise configured
	FNumbers that do not use self.value should override all magic methods
	of FReal that use it.
	"""
	def __eq__(self, other):
		return self.value == other
	def __ne__(self, other):
		return self.value != other
	def __lt__(self, other):
		return self.value < other
	def __le__(self, other):
		return self.value <= other
	def __gt__(self, other):
		return self.value > other
	def __ge__(self, other):
		return self.value >= other
	def __pos__(self):
		return self
	def __neg__(self):
		return FNumber(-self.value)
	def __abs__(self):
		return FNumber(abs(self.value))
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
		return self
	@property
	def imag(self):
		return FInteger(0)
	def conjugate(self):
		return self
	def __add__(self, other):
		return FNumber(self.value + other)
	def __radd__(self, other):
		return FNumber(other + self.value)
	def __mul__(self, other):
		return FNumber(self.value * other)
	def __rmul__(self, other):
		return FNumber(other * self.value)
	def __ceil__(self):
		return FInteger(self.value.__ceil__())
	def __floor__(self):
		return FInteger(self.value.__floor__())
	def __truediv__(self, other):
		""" int / int -> rational """
		if isinstance(self, FInteger) and isinstance(other, FInteger):
			return FRational(self, FNumber(other))
		return FNumber(self.value / other)
	def __rtruediv__(self, other):
		""" int / int -> rational """
		if isinstance(self, FInteger) and isinstance(other, FInteger):
			return FRational(FNumber(other), self)
		return FNumber(other / self.value)
	def __floordiv__(self, other):
		return FNumber(self.value // other)
	def __rfloordiv__(self, other):
		return FNumber(other // self.value)
	def __mod__(self, other):
		return FNumber(self.value % other)
	def __rmod__(self, other):
		return FNumber(other % self.value)
	def __pow__(self, other):
		return FNumber(self.value ** other)
	def __rpow__(self, other):
		return FNumber(other ** self.value)
	def __round__(self, other):
		return FNumber(round(self.value, other))
	def __trunc__(self, other):
		return FNumber(self.value.__trunc__(other))
	def sign(self):
		if self > 0:
			return FNumber(1)
		elif self:
			return FNumber(-1)
		else:
			return FNumber(0)

class FInteger(FReal, numbers.Integral):
	def __new__(cls, value=0):
		self = object.__new__(cls)
		self.value = int(value.real//1)
		return self
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
	def is_integer(self):
		return True
	
class FBool(FInteger):
	def __new__(cls, value=False):
		self = object.__new__(cls)
		self.value = bool(value)
		return self
	def __bool__(self):
		return self.value
	
	
class FFloat(FReal, numbers.Real):
	def __new__(cls, value=0.):
		self = object.__new__(cls)
		self.value = float(value)
		return self
	def __str__(self):
		return str(self.value)
	def __repr__(self):
		return str(self.value)
	def is_integer(self):
		return self.value.is_integer()
	
class FRational(FReal, numbers.Rational):
	def __new__(cls, *args):
		self = object.__new__(cls)
		if len(args) == 0:
			self.value = Fraction(0)
		elif len(args) == 1:
			arg = args[0]
			if isinstance(arg, (int, FInteger)):
				self.value = Fraction(int(arg))
			elif isinstance(arg, float):
				self.value = Fraction(*arg.as_integer_ratio())
			elif isinstance(arg, FFloat):
				a, b = arg.as_integer_ratio()
				a = int(a)
				b = int(b)
				self.value = Fraction(a, b)
			elif isinstance(arg, Fraction):
				self.value = arg
			elif isinstance(arg, FRational):
				self.value = arg.value
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
			elif isinstance(denom, FReal(float, FFloat)):
				denom, nmul = denom.as_integer_ratio()
			elif isinstance(denom, (Fraction, FRational)):
				denom, nmul = denom.numerator, denom.denominator
			else:
				raise TypeError(denom)
			num *= nmul
			denom *= dmul
			gcd = math.gcd(int(num), int(denom))
			num = num // gcd
			denom = denom // gcd
			if denom < 0:
				num *= -1
				denom *= -1
			elif denom == 0:
				raise ZeroDivisionError("FRational(%r, %r)" % args)
			self.value = Fraction(int(num), int(denom))
		else:
			raise TypeError("FRational takes at most 2 arguments (%d given)" % len(args))
		return self
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
	def is_integer(self):
		return self.denominator == 1

class FComplex(FNumber, numbers.Complex):
	def __new__(cls, *args):
		self = object.__new__(cls)
		if len(args) == 0:
			self._real = FInteger(0)
			self._imag = FInteger(0)
		elif len(args) == 1:
			self._real = FNumber(args[0].real) # 0.0 == FInteger(0) but will 
			self._imag = FNumber(args[0].imag)
		elif len(args) == 2:
			self._real = FNumber(args[0].real - args[1].imag)
			self._imag = FNumber(args[1].real + args[0].imag)
		else:
			raise TypeError("FComplex takes at most 2 arguments (%d given)" % len(args))
		return self
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
		if self.imag == 0:
			return self.real < other
		return NotImplemented
	def __le__(self, other):
		if self.imag == 0:
			return self.real <= other
		return NotImplemented
	def __gt__(self, other):
		if self.imag == 0:
			return self.real > other
		return NotImplemented
	def __ge__(self, other):
		if self.imag == 0:
			return self.real >= other
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
	def is_integer(self):
		return self.imag == 0 and self.real.denominator == 1
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
		
	
		
	
	
			