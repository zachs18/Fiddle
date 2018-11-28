from abc import ABC, abstractmethod
from fractions import Fraction

from fiter import FIterator
import fnumeric
	
class FGeometricSequence(FIterator):
	"""
	A sequence with a start(=1), an end(=None), and a step(=2)
	If end is None, the sequence is infinite.
	If end is not None, the sequence will be bounded by it (end will not be part of the sequence)
	Geometric sequences are bounded by absolute value
	i.e. [*FGeometricIntegerSequence(1,8,-2)] == [1, -2, 4] # -8 is not included because abs(-8) is past the bound
	"""
	@abstractmethod
	def __init__(self):
		pass
	def __next__(self):
		print(self.start, self.end, self.step, self._current, self._inf)
		if self.end is None:
			ret = self._current
			self._current = self.type(self._current * self.step)
			return self.type(ret)
		else:
			if abs(self.step) > 1: # 1, 2, 4 or -1, -2, -4 or -1, 2, -4
				if abs(self._current) >= abs(self.end):
					raise StopIteration
				ret = self._current
				self._current *= self.step
				return self.type(ret)
			elif 0 < abs(self.step) < 1: # 4, 2, 1 or -4, -2, -1 or -4, 2, -1
				if abs(self._current) <= abs(self.end):
					raise StopIteration
				ret = self._current
				self._current *= self.step
				return self.type(ret)
			else:
				raise ValueError(self.step)
	
class FGeometricIntegerSequence(FGeometricSequence):
	type = fnumeric.FInteger
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = 1
		
		if step is None:
			if end is None or (end > 0 and start > 0 and end >= start) or (end < 0 and start < 0 and end <= start):
				step = 2
			elif (end > 0 and start > 0 and end <= start) or (end < 0 and start < 0 and end >= start):
				step = Fraction(1,2)
			elif ((end < 0 and start > 0) or (end > 0 and start < 0)) and abs(end) >= abs(start):
				step = -2
			else:
				step = Fraction(-1,2)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if abs(end) < abs(start):
				if abs(step) >= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif abs(end) > abs(start):
				if abs(step) <= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
class FGeometricFloatSequence(FGeometricSequence):
	type = fnumeric.FFloat
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = 1.
		
		if step is None:
			if end is None or (end > 0 and start > 0 and end >= start) or (end < 0 and start < 0 and end <= start):
				step = 2.
			elif (end > 0 and start > 0 and end <= start) or (end < 0 and start < 0 and end >= start):
				step = 0.5
			elif ((end < 0 and start > 0) or (end > 0 and start < 0)) and abs(end) >= abs(start):
				step = -2.
			else:
				step = -0.5
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if abs(end) < abs(start):
				if abs(step) >= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif abs(end) > abs(start):
				if abs(step) <= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
class FGeometricRationalSequence(FGeometricSequence):
	type = fnumeric.FRational
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = 1
		
		if step is None:
			if end is None or (end > 0 and start > 0 and end >= start) or (end < 0 and start < 0 and end <= start):
				step = 2
			elif (end > 0 and start > 0 and end <= start) or (end < 0 and start < 0 and end >= start):
				step = Fraction(1,2)
			elif ((end < 0 and start > 0) or (end > 0 and start < 0)) and abs(end) >= abs(start):
				step = -2
			else:
				step = Fraction(-1,2)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if abs(end) < abs(start):
				if abs(step) >= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif abs(end) > abs(start):
				if abs(step) <= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
class FGeometricComplexSequence(FGeometricSequence):
	type = fnumeric.FComplex
	def __init__(self, start=None, end=None, step=None, *, _current=None):
		if start is None:
			start = 1
		
		if step is None:
			if end is None or abs(end) >= abs(start):
				step = 2
			elif abs(end) <= abs(start):
				step = Fraction(1,2)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			if abs(end) < abs(start):
				if abs(step) >= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			elif abs(end) > abs(start):
				if abs(step) <= 1:
					raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
			
		
	