# Main -> eviction strategy -> pass which cache to use (ENUM) -> cache.py -> cache(evictionStrategy.LRU) [use singleton to create one object of a cache] 
# -> To create cache it will call HashMapStore(size, evictionStrategy.LRU) (model) -> talks to datastore in DAO -> talks to actual LRU.py
# EvictionStrategyEnum → Cache (singleton) → HashStore → Datastore → LRU
# HashStore - model or controller for the cache data.
# Datastore - bridge between storage and eviction logic.
from enum import Enum
from abc import ABC, abstractmethod

# ------EvictionStrategy.py
class EvictionStrategy(Enum):
    LRU = 1
    LFU = 2
    MRU = 3

# ------EvictionPolicy.py
class EvictionPolicy(ABC):

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def put(self, key, val):
        pass

    @abstractmethod
    def remove(self, key):
        pass


# ------LRU.py

class DoublyLinkedList:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None


class LRU(EvictionPolicy):
    def __init__(self, capacity, store):
        self.left, self.right = DoublyLinkedList(0, 0), DoublyLinkedList(0, 0)
        self.left.right, self.right.prev = self.right, self.left
        self.store = store
        self.capacity = capacity
  

    def deleteNode(self, node: DoublyLinkedList):
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def insertAtLast(self, node: DoublyLinkedList): 
        prev = self.right.prev
        next = self.right
        prev.next = node
        node.next = next
        next.prev = node
        node.prev = prev
        return True
        
    def get(self, key):
        if key in self.store:
            node = self.store[key]
            self.deleteNode(node)
            self.insertAtLast(node)
            return node.val
            
    def put(self, key, val):
        if key in self.store:
            self.deleteNode(self.store[key])
        node = DoublyLinkedList(key, val)
        self.insertAtLast(node)
        self.store[key] = node
        if len(self.store) > self.capacity:
            del self.store[self.left.next.key]
            self.deleteNode(self.left.next)

    def remove(self, key):
        if key in self.store:
            node = self.store[key]
            self.deleteNode(node)
            del self.store[key]
            return True


# ------datastoreInt.py

class datastoreInt(ABC):
        
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def put(self, key, val):
        pass

    @abstractmethod
    def remove(self, key):
        pass

    
# ------datastore.py

class Datastore(datastoreInt):
    def __init__(self, capacity, evictionStrategy: EvictionStrategy):
        self.map = {}
        if evictionStrategy == EvictionStrategy.LRU:
            self.evictionPolicy = LRU(capacity, self.map)
        # Add LFU, MRU here later
        
        
    def get(self, key):
        return self.evictionPolicy.get(key)

    def put(self, key, val):
        return self.evictionPolicy.put(key, val)

    def remove(self, key):
        return self.evictionPolicy.remove(key)


# ------Store.py

class Store(ABC):

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def put(self, key, val):
        pass

    @abstractmethod
    def remove(self, key):
        pass


# ------HashStore.py

class HashStore(Store):
    def __init__(self, capacity, evictionStrategy: EvictionStrategy):
        self.datastore = Datastore(capacity, evictionStrategy)
    
    def get(self, key):
        return self.datastore.get(key)
   
    def put(self, key, val):
        return self.datastore.put(key, val)
   
    def remove(self, key):
        return self.datastore.remove(key)

# ------Cache.py

from pyclbr import Class
import threading

class Cache:
    _conObject = None
    _lock = threading.Lock()

    def __new__(cls, size, evictionStrategy):
        with cls._lock:
            if cls._conObject is None:
                cls._conObject = super(Cache, cls).__new__(cls)
                cls._conObject.store = HashStore(size, evictionStrategy)
        return cls._conObject

    def __init__(self, size, evictionStrategy):
        pass

    @staticmethod
    def getInstance(size, evictionStrategy):
        return Cache(size, evictionStrategy)

    def get(self, key):
        return self.store.get(key)

    def put(self, key, value):
        return self.store.put(key, value)

    def remove(self, key):
        return self.store.remove(key)



# ------Main.py

cache = Cache(10, EvictionStrategy.LRU)
cache.put(10, "test2")
print(cache.get(10))
