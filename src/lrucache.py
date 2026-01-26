from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, _key):
        if _key not in self.cache:
            return None
        self.cache.move_to_end(_key)
        return self.cache[_key]

    def put(self, _key, _value):
        self.cache[_key] = _value
        self.cache.move_to_end(_key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
