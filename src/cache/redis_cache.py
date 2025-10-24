import redis
import json
from typing import Any, Optional
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, CACHE_TTL


class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        self.available = self.client.ping()
        print("✅ Redis cache connected" if self.available else "⚠️ Redis unavailable")

    def get(self, key: str) -> Optional[Any]:
        if not self.available:
            return None
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: Any, ttl: int = CACHE_TTL):
        if not self.available:
            return
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key: str):
        if not self.available:
            return
        self.client.delete(key)

    def clear_pattern(self, pattern: str):
        if not self.available:
            return
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)

    def flush_all(self):
        if not self.available:
            return
        self.client.flushdb()
        print("✅ Cache cleared")

cache = RedisCache()

'''
NOTE:
1. The RedisCache class manages connection to a Redis server and provides methods to get, set, delete, and clear cache entries.

2. It handles connection errors gracefully, allowing the application to function without caching if Redis is unavailable.

3. The cache uses JSON serialization for storing complex data structures.

4. The global `cache` instance can be imported and used throughout the application for caching needs.

5. Each method checks if the Redis server is available before performing operations, ensuring robustness.
'''