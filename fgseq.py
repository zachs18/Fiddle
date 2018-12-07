from abc import ABC, abstractmethod
from fractions import Fraction

from fiter import FIterator
import fnumeric
from fnumeric import FNumber, FComplex
	
class FGeometricSequence(FIterator):
	"""
	A sequence with a start(=1), an end(=None), and a step(=2)
	If end is None, the sequence is infinite.
	If end is not None, the sequence will be bounded by it (end will not be part of the sequence)
	Geometric sequences are bounded by absolute value
	i.e. [*FGeometricIntegerSequence(1,8,-2)] == [1, -2, 4] # -8 is not included because abs(-8) is past the bound
	"""
	
	def __init__(self, start=None, end=None, step=None, length=None, *, _current=None, _index=0, call=FNumber, inclusive=False):
		if start is None:
			start = FInteger(1)
		
		if step is None:
			if end is None or (end.norm() >= start.norm()):
				step = FInteger(2)
			else: #if (end.norm() <= start.norm()):
				step = FRational(1,2)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if end.norm() < start.norm():
				if step.norm() >= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif end.norm() > start.norm():
				if step.norm() <= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None) and (length is None)
		self.length = length
		self._index = _index
		self._current = self.start if _current is None else _current # for copying
		self.call = call
		self.inclusive = inclusive
	def __next__(self):
		#print(self.start, self.end, self.step, self._current, self._inf)
		if self.end is None:
			if self.length is not None and self._index >= self.length:
				raise StopIteration
			self._index += 1
			ret = self._current
			self._current *= self.step
			return self.call(ret)
		else:
			if self.step.norm() > 1: # 1, 2, 4 or -1, -2, -4 or -1, 2, -4
				if self._current.norm() >= self.end.norm() or (self.length is not None and self._index >= self.length):
					raise StopIteration
				self._index += 1
				ret = self._current
				self._current *= self.step
				return self.call(ret)
			elif 0 < self.step.norm() < 1: # 4, 2, 1 or -4, -2, -1 or -4, 2, -1
				if self._current.norm() <= self.end.norm() or (self.length is not None and self._index >= self.length):
					raise StopIteration
				self._index += 1
				ret = self._current
				self._current *= self.step
				return self.call(ret)
			else:
				raise ValueError(self.step) # end should be None if abs(step) == 0 or 1
	def copy(self):
		return type(self)(self.start, self.end, self.step, self.length, _current=self._current, _index=self._index, call=self.call, inclusive=self.inclusive)
