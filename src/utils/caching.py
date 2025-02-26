import time

class Cache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        """Retrieve data from cache if not expired."""
        item = self.cache.get(key, None)
        if item and time.time() < item["expiry"]:
            return item["data"]
        return None

    def set(self, key, data, expire=3600):
        """Store data in cache with an expiration time (default 1 hour)."""
        self.cache[key] = {"data": data, "expiry": time.time() + expire}

cache_response = Cache()