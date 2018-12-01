import inspect

from fobject import FObject
from fiter import FIterable, FIterator, FInfiniteIteratorProxy, FIteratorIndex
from faseq import FArithmeticSequence


class FList(FIterable):
	def __init__(self, contents=None):
		if contents is None:
			self.list = []
			self.gen = None
			self._inf = False
		elif isinstance(contents, FIterator):
			try:
				self.list = []
				print(contents)
				self.gen = contents.copy()
				self._inf = self.gen._inf
			except TypeError: # python iterators cannot be copied and FIterator.copy() raises a TypeError for this
				# immediately empty a (proxied) python iterator, as it cannot be copied
				self.list = [*contents] 
				self.gen = None
				self._inf = False
		elif isinstance(contents, FIterable):
			try:
				self.list = []
				self.gen = iter(contents.copy())
				self._inf = self.gen._inf
			except TypeError: # python iterators cannot be copied and FIterator.copy() raises a TypeError for this
				self.list = [*contents]
				self.gen = None
				self._inf = False
		elif hasattr(contents, "__iter__"):
			# immediately empty a python iterator, as it cannot be copied
			self.list = [*contents]
			self.gen = None
			self._inf = False
		else:
			raise TypeError("%r doesn't appear to be a sequence" % contents)
		for item in self.list:
			if not isinstance(item, FObject):
				raise TypeError("%r is not %r" % (item, FObject))
	def __getitem__(self, index):
		if hasattr(index, "__index__"):
			if index >= 0:
				self._fill(index)
				return self.list[index] # could IndexError
			else:
				if self._inf:
					raise IndexError("negative index of infinite FList")
				self._fill()
				return self.list[index]
		#elif isinstance(index, FSlice):
		#	return index.slice(self.copy())
		elif isinstance(index, slice):
			if not self._inf:
				indices = index.indices(len(self))
				return type(self)(FIteratorIndex(self, FArithmeticSequence(*indices)))
			elif index.start is None:
				if index.stop is None:
					if index.step is None:
						return self.copy()
					elif index.step >= 0:
						return type(self)(FIteratorIndex(self, FArithmeticSequence(step=index.step)))
					else: # invalid
						raise ValueError("Cannot use negative step on infinite list without specifying positive start")
				elif index.stop >= 0:
					if index.step is None or index.step >= 0:
						return type(self)(FIteratorIndex(self, FArithmeticSequence(end=index.stop, step=index.step)))
					else:
						raise ValueError("Cannot use negative step on infinite list without specifying positive start")
				else:
					raise IndexError("negative slice stop of infinite FList")
			elif index.start >= 0:
				if index.stop is None:
					return type(self)(FIteratorIndex(self, FArithmeticSequence(start=index.start, step=index.step)))
				elif index.stop >= 0:
					return type(self)(FIteratorIndex(self, FArithmeticSequence(start=index.start, end=index.stop, step=index.step)))
				else:
					raise IndexError("negative slice stop of infinite FList")
			else:
				raise IndexError("negative slice start of infinite FList")
		elif hasattr(index, "__iter__"):
			if hasattr(index, "_inf") and index._inf:
				return type(self)(FIteratorIndex(self, index))
			else:
				return type(self)(self[i] for i in index)
		else:
			raise TypeError(index)
		#TODO: slicing, listing
	def __setitem__(self, index, value):
		if hasattr(index, "__index__"):
			if index >= 0:
				self._fill(index)
				self.list[index] = value
			else:
				if self._inf:
					raise IndexError("negative index of infinite FList")
				self._fill()
				self.list[index] = value
	def __delitem__(self, index):
		if hasattr(index, "__index__"):
			if index >= 0:
				self._fill(index)
				del self.list[index]
			else:
				if self._inf:
					raise IndexError("negative index of infinite FList")
				self._fill()
				del self.list[index]
	def insert(self, index, value):
		if index >= 0:
			self._fill(index)
			try:
				self.list.insert(index, value)
			except IndexError:
				raise IndexError("FList index out of range")
		else:
			if self._inf:
				raise IndexError("negative index of infinite FList")
			self._fill()
			self.list.insert(index, value)
	def pop(self, index):
		ret = self[index]
		del self[index]
		return ret
	def push(self, value):
		self.insert(0, value)
			
	def __len__(self):
		if self._inf:
			raise InfiniteLengthException # cannot return float('inf') from __len__
		elif self.gen is not None:
			self._fill()
			return len(self.list)
		else:
			return len(self.list)
	def length(self):
		try:
			return len(self)
		except InfiniteLengthException:
			return float('inf')
	def _fill(self, length=None):
		if self.gen:
			try:
				while length is None or len(self.list) <= length:
					nxt = next(self.gen)
					if not isinstance(nxt, FObject):
						raise TypeError("%r is not %r" % (nxt, FObject))
					self.list.append(nxt)
			except StopIteration:
				self.gen = None
			
	def copy(self):
		if self.gen:
			out = type(self)(self.gen.copy())
			# self.gen is None or an Fiterator that hasn't been depleted
		else:
			out = type(self)()
		out.list = [i.copy() for i in self.list]
		return out
	def __iter__(self):
		return FListIterator(self)
	def __str__(self):
		if self._inf:
			self._fill(5)
			return '[' + ', '.join(str(i) for i in self.list) + ', ...]'
		elif len(self) > 0:
			return '[' + ', '.join(str(i) for i in self.list) + ']'
		else:
			return '[]'
	def __repr__(self):
		if self._inf:
			self._fill(5)
			return '[' + ', '.join(str(i) for i in self.list) + ', ...]'
		elif len(self) > 0:
			return '[' + ', '.join(str(i) for i in self.list) + ']'
		else:
			return '[]'

class FListIterator(FIterator):
	def __init__(self, ls, *, _index=0):
		self.ls = ls.copy()
		self._inf = hasattr(ls, "_inf") and ls._inf
		self._index = _index
	def __next__(self):
		try:
			i = self._index
			self._index += 1
			return self.ls[i]
		except IndexError:
			raise StopIteration
	def copy(self):
		return FListIterator(self.ls.copy(), _index=self._index)
	def __add__(self, other):
		if self._inf:
			return self.copy()
		elif isinstance(other, FList):
			out = self.copy()
			
	def join(self, it):
		out

class InfiniteLengthException(Exception):
	pass
