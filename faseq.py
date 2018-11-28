from abc import ABC, abstractmethod
from fractions import Fraction

from fiter import FIterator
import fnumeric

class FArithmeticSequence(FIterator):
	"""
	A sequence with a start(=0), an end(=None), and a step(=+/-1)
	If end is None, the sequence is infinite.
	If end is not None, the sequence will be bounded by it (end will not be part of the sequence)
	"""
	@abstractmethod
	def __init__(self):
		pass
	def __next__(self):
		#print(self.start, self.end, self.step, self._current, self._inf)
		if self.end is None:
			ret = self._current
			self._current += self.step
			return self.type(ret)
		else:
			if self.step > 0:
				if self._current >= self.end:
					raise StopIteration
				ret = self._current
				self._current += self.step
				return self.type(ret)
			else:
				if self._current <= self.end:
					raise StopIteration
				ret = self._current
				self._current += self.step
				return self.type(ret)
	def copy(self):
		return type(self)(self.start, self.end, self.step, _current=self._current)
	
class FArithmeticIntegerSequence(FArithmeticSequence):
	type = fnumeric.FInteger
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = 0
		
		if step is None:
			if end is None or end >= start:
				step = 1
			else:
				step = -1
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if end < start:
				if step >= 0:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif end > start:
				if step <= 0:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
class FArithmeticFloatSequence(FArithmeticSequence):
	type = fnumeric.FFloat
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = 0.
		
		if step is None:
			if end is None or end >= start:
				step = 1.
			else:
				step = -1.
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if end < start:
				if step >= 0:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif end > start:
				if step <= 0:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
class FArithmeticRationalSequence(FArithmeticSequence):
	type = fnumeric.FRational
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = Fraction(0)
		
		if step is None:
			if end is None or end >= start:
				step = Fraction(1)
			else:
				step = Fraction(-1)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if end < start:
				if step >= 0:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif end > start:
				if step <= 0:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
class FArithmeticComplexSequence(FArithmeticSequence):
	"""
	Bounding is done by absolute value.
	
	"""
	type = fnumeric.FComplex
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = complex(0)
		
		if step is None:
			if end is None or abs(end) >= abs(start):
				step = complex(1) if start==0 else start/abs(start)
			else:
				step = -start/abs(start)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			#TODO: (probably not too difficult)
			# make sure start + k*step will pass end's abs circle
			# always will if step!=0 and abs(end)>abs(start)
			if step == 0:
				raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif abs(end) > abs(start):
				pass # will pass eventually
			elif abs(end) < abs(start):
				#TODO
				pass
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
	def __next__(self):
		#print(self.start, self.end, self.step, self._current, self._inf)
		if self.end is None:
			ret = self._current
			self._current += self.step
			return ret
		else:
			if abs(self.start):
				if abs(self._current) >= abs(self.end):
					raise StopIteration
				ret = self._current
				self._current += self.step
				return ret
			else:
				if self._current <= self.end:
					raise StopIteration
				ret = self._current
				self._current += self.step
				return ret
			