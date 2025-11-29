class CacheService:
    def __init__(self):
        self._store = {}
    def get(self, k):
        return self._store.get(k)
    def set(self,k,v):
        self._store[k]=v
    def clear(self):
        self._store.clear()
