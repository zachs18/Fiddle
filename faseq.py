from abc import ABC, abstractmethod
from fractions import Fraction

from fiter import FIterator
from fnumeric import FNumber, FComplex

class FArithmeticSequence(FIterator):
	"""
	A sequence with a start(=0), an end(=None), and a step(=+/-1)
	If end is None, the sequence is infinite.
	If end is not None, the sequence will be bounded by it (end will not be part of the sequence)
	"""
	def __init__(self, start=None, end=None, step=None, *, _current=None, call=FNumber):
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
		self.call = call
	def __next__(self):
		#print(self.start, self.end, self.step, self._current, self._inf)
		if self.end is None:
			ret = self._current
			self._current += self.step
			return self.call(ret)
		else:
			if self.step > 0:
				if self._current >= self.end:
					raise StopIteration
				ret = self._current
				self._current += self.step
				return self.call(ret)
			else:
				if self._current <= self.end:
					raise StopIteration
				ret = self._current
				self._current += self.step
				return self.call(ret)
	def copy(self):
		return type(self)(self.start, self.end, self.step, _current=self._current, call=self.call)

class FArithmeticComplexSequence(FArithmeticSequence):
	"""
	Bounding is done by absolute value.
	
	"""
	def __init__(self, start=None, end=None, step=None, *, _current=None, call=FNumber):
		if start is not None and not isinstance(start, FNumber):
			start = FNumber(start)
		if end is not None and not isinstance(end, FNumber):
			end = FNumber(end)
		if step is not None and not isinstance(step, FNumber):
			step = FNumber(step)

		if start is None:
			start = FComplex(0)
		
		if step is None:
			if end is None or abs(end) >= abs(start):
				step = FComplex(1) if start==0 else start/abs(start)
			else:
				step = -start/abs(start)
		elif step is not None and end is not None:
			# if end is given, it must eventually be reached
			# make sure start + k*step will pass end's abs circle
			# always will if step!=0 and abs(end)>abs(start)
			# NOTE: I worked around this by checking if current.norm() >= start.norm() if end.norm() <= start.norm() in __next__()
			if step == 0:
				raise ValueError("Invalid sequence(start=%r,end=%r,step=%r)"%(start, end, step))
			#elif abs(end) > abs(start):
			#	pass # will pass eventually
			#elif abs(end) < abs(start):
			#	pass # We check in __next__ if _current got bigger than start (i.e. it passed by end's circle)
			else:
				pass #empty sequence is not an error
		
		self.start = start
		self.end = end if end is not None else None
		self.step = step
		self._inf = (end is None)
		self._current = self.start if _current is None else _current # for copying
		self.call = call
	def __next__(self):
		#print(self.start, self.end, self.step, self._current, self._inf)
		if self.end is None:
			ret = self._current
			self._current += self.step
			return self.call(ret)
		else:
			if self.start.norm() < self.end.norm(): # norm to avoid float precision issues if the components arent floats
				if abs(self._current) >= abs(self.end):
					raise StopIteration
				ret = self._current
				self._current += self.step
				return self.call(ret)
			else:
				if self._current.norm() <= self.end.norm() or (self._current != self.start and self._current.norm() >= self.start.norm()):
					raise StopIteration
				ret = self._current
				self._current += self.step
				return self.call(ret)
			