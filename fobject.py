from abc import ABC, abstractmethod

class FObject(ABC):
	@abstractmethod
	def copy(self):
		pass
	 