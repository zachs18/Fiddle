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
	def __new__(cls, start=None, end=None, step=None, length=None, *, _current=None, _index=0, call=FNumber, inclusive=False):
		if cls is not FArithmeticSequence:
			return object.__new__(cls)
		if isinstance(start, (complex, FComplex)) or \
			isinstance(end, (complex, FComplex)) or \
			isinstance(step, (complex, FComplex)):
			return object.__new__(FArithmeticComplexSequence)
		else:
			return object.__new__(cls)
	
	def __init__(self, start=None, end=None, step=None, length=None, *, _current=None, _index=0, call=FNumber, inclusive=False):
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
			self._current += self.step
			return self.call(ret)
		else:
			if self.step > 0:
				if self._current > self.end or (not self.inclusive and self._current == self.end) or (self.length is not None and self._index >= self.length):
					raise StopIteration
				self._index += 1
				ret = self._current
				self._current += self.step
				return self.call(ret)
			else:
				if self._current < self.end or (not self.inclusive and self._current == self.end) or (self.length is not None and self._index >= self.length):
					raise StopIteration
				self._index += 1
				ret = self._current
				self._current += self.step
				return self.call(ret)
	def copy(self):
		return type(self)(self.start, self.end, self.step, self.length, _current=self._current, _index=self._index, call=self.call, inclusive=self.inclusive)

class FArithmeticComplexSequence(FArithmeticSequence):
	"""
	Bounding is done by absolute value.
	TODO: If abs(start)>abs(end) it can jump over end's circle, it will keep going until it reached start's circle again
		i.e. start=6, end=1, step=-4
		[0] 6
		[1] 2
		# skipped over end's circle
		[2] -2
		[3] -6 # only if inclusive
	"""
	def __init__(self, start=None, end=None, step=None, length=None, *, _current=None, _index=0, call=FNumber, inclusive=False):
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
			self._current += self.step
			return self.call(ret)
		else:
			if self.start.norm() < self.end.norm(): # norm to avoid float precision issues if the components arent floats
				if self._current.norm() > self.end.norm() or (not self.inclusive and self._current.norm() == self.end.norm()) or \
					(self.length is not None and self._index >= self.length):
					raise StopIteration
				self._index += 1
				ret = self._current
				self._current += self.step
				return self.call(ret)
			else:
				if self._current.norm() < self.end.norm() or (not self.inclusive and self._current.norm() == self.end.norm()) or \
					(self._current != self.start and (self._current.norm() > self.start.norm() or (not self.inclusive and self._current.norm() == self.start.norm()))) or \
					(self.length is not None and self._index >= self.length):
					raise StopIteration
				self._index += 1
				ret = self._current
				self._current += self.step
				return self.call(ret)
			