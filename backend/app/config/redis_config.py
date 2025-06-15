import redis
import os
from dotenv import load_dotenv
import json
from typing import Optional, Any
import logging

load_dotenv()

class RedisService:
    def __init__(self):
        self.redis_client = None
        self.connect()

    def connect(self):
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD', None),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None

    def is_connected(self) -> bool:
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False

    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache with TTL (default 1 hour)"""
        try:
            if not self.is_connected():
                return False
            
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logging.error(f"Redis set error: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            if not self.is_connected():
                return None
            
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            return None

    def delete_cache(self, key: str) -> bool:
        """Delete cache key"""
        try:
            if not self.is_connected():
                return False
            
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
            return False

    def get_keys(self, pattern: str) -> list:
        """Get keys matching pattern"""
        try:
            if not self.is_connected():
                return []
            
            return self.redis_client.keys(pattern)
        except Exception as e:
            logging.error(f"Redis keys error: {e}")
            return []

# Global Redis instance
redis_service = RedisService()
