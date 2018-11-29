from abc import ABC, abstractmethod

from fobject import FObject
import flist


class FIterable(FObject):
	@abstractmethod
	def __init__(self):
		self._inf = False
		pass
	@abstractmethod
	def __iter__(self):
		pass

class FIterator(FIterable):
	def __iter__(self):
		return self
	@abstractmethod
	def __next__(self):
		pass

class FIteratorProxy(FIterator):
	"""
	FIterator proxy for an iterator.
	Must be finite.
	
	"""
	def __new__(cls, it, call=(lambda x:x)):
		if cls is not FIteratorProxy:
			return object.__new__(cls)
		if hasattr(it, "_inf") and it._inf:
			return object.__new__(FInfiniteIteratorProxy)
		return object.__new__(FIteratorProxy)
		
		
	def __init__(self, it, call=(lambda x:x)):
		self.it = it
		self._inf = False
		self.call = call
	def __next__(self):
		return self.call(next(self.it))
	def copy(self):
		if hasattr(self.it, 'copy'):
			return FIteratorProxy(self.it.copy(), call=self.call)
		raise TypeError("Python iterators cannot be copied")

class FInfiniteIteratorProxy(FIteratorProxy):
	"""
	FIterator proxy for an iterator.
	May be infinite.
	
	"""
	def __init__(self, it, call=(lambda x:x)):
		self.it = it
		self._inf = it._inf if hasattr(it, "_inf") else True
		self.call = call
	def __next__(self):
		return self.call(next(self.it))
	

class FIteratorZip(FIterator):
	def __init__(self, *its, call=(lambda *x:flist.FList([*x])), _inf=False, longest=False, default=None):
		self.its = [iter(it) for it in its]
		self._inf = _inf or \
			(longest and any(hasattr(it, "_inf") and it._inf for it in its)) or \
			all(hasattr(it, "_inf") and it._inf for it in its)
		self.call = call
		self.longest = longest
		self.default = default
	def __next__(self):
		ret = []
		done = True
		for it in self.its:
			try:
				ret.append(next(it))
				done = False
			except StopIteration:
				if self.longest:
					if self.default is not None:
						ret.append(self.default)
					else:
						pass
				else:
					raise StopIteration
		if done:
			raise StopIteration
		return self.call(*ret)
	def copy(self):
		if all(hasattr(it, 'copy') for it in self.its):
			return FIteratorZip(*(it.copy() for it in self.its), call=self.call, _inf=self._inf, longest=self.longest, default=self.default)
		raise TypeError("Python iterators cannot be copied")
		
class FIteratorConcatenate(FIterator):
	def __init__(self, *its, call=(lambda x:x), _inf=False):
		self.its = [iter(it) for it in its]
		self._inf = _inf or \
			(hasattr(its, "_inf") and its._inf) or \
			any(hasattr(it, "_inf") and it._inf for it in its)
		self._index = 0
		self.call = call
	def __next__(self):
		while True:
			try:
				return self.call(next(self.its[self._index]))
			except StopIteration:
				self._index += 1
			except IndexError:
				raise StopIteration
	def copy(self):
		if all(hasattr(it, 'copy') for it in self.its[self._index:]):
			return FIteratorConcatenate(*(it.copy() for it in self.its[self._index:]), call=self.call, _inf=self._inf)
		raise TypeError("Python iterators cannot be copied")
			
class FIteratorIndex(FIterator):
	def __init__(self, lst, index, call=(lambda x:x), _inf=False):
		self.list = lst.copy()
		self.index = iter(index)
		self._inf = _inf or (hasattr(index, "_inf") and index._inf)
		self.call = call
	def __next__(self):
		return self.call(self.list[next(self.index)])
	def copy(self):
		if all(hasattr(it, 'copy') for it in [self.list, self.index]):
			return FIteratorIndex(self.list, self.index, _inf=self._inf)
		raise TypeError("Python iterators cannot be copied")
	
class FIteratorRepeat(FIterator):
	def __init__(self, it, count=None, call=(lambda x:x), _inf=False, _current=None, _index=0):
		self.it = it
		self._inf = _inf or (hasattr(it, "_inf") and it._inf) or (count is None)
		self.count = count
		self._index = _index
		if hasattr(it, 'copy'):
			self._current = it.copy() if _current is None else _current.copy()
		else:
			raise TypeError("Python iterators cannot be copied (and therefore repeated)")
		try:
			next(it.copy())
		except StopIteration:
			if self.count is not None:
				self._index = count # so we dont loop in next
			else:
				raise ValueError("Cannot repeat empty list indefnitely")
		self.call = call
	def __next__(self):
		while True:
			if self.count is not None and self._index >= self.count:
				raise StopIteration
			try:
				return self.call(next(self._current))
			except StopIteration:
				self._current = self.it.copy()
				self._index += 1	
	def copy(self):
		return FIteratorRepeat(self.it, count=self.count, call=self.call, _inf=self._inf, _current=self._current, _index=self._index)
		#raise TypeError("Python iterators cannot be copied") # .copy is a requirement for FIteratorRepeat
	