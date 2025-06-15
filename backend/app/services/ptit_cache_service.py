from ..config.redis_config import redis_service
from typing import Optional, Dict, Any
import hashlib
import os

class PTITCacheService:
    def __init__(self):
        self.cache_ttl = int(os.getenv('PTIT_CACHE_TTL', 3600))  # 1 hour
        
    def _generate_cache_key(self, chat_session_id: str, api_type: str, params: Dict = None) -> str:
        """Generate cache key for PTIT API data"""
        base_key = f"ptit:{chat_session_id}:{api_type}"
        
        # Add params hash if provided
        if params:
            params_str = str(sorted(params.items()))
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            base_key += f":{params_hash}"
            
        return base_key
    
    def get_cached_data(self, chat_session_id: str, api_type: str, params: Dict = None) -> Optional[Dict]:
        """Get cached PTIT API data"""
        cache_key = self._generate_cache_key(chat_session_id, api_type, params)
        cached_data = redis_service.get_cache(cache_key)
        
        if cached_data:
            print(f"✅ Cache HIT: {cache_key}")
            return cached_data
        else:
            print(f"❌ Cache MISS: {cache_key}")
            return None
    
    def set_cached_data(self, chat_session_id: str, api_type: str, data: Dict, params: Dict = None) -> bool:
        """Cache PTIT API data"""
        cache_key = self._generate_cache_key(chat_session_id, api_type, params)
        success = redis_service.set_cache(cache_key, data, self.cache_ttl)
        
        if success:
            print(f"✅ Cache SET: {cache_key} (TTL: {self.cache_ttl}s)")
        else:
            print(f"❌ Cache SET failed: {cache_key}")
            
        return success
    
    def invalidate_session_cache(self, chat_session_id: str) -> int:
        """Invalidate all cache for a chat session"""
        pattern = f"ptit:{chat_session_id}:*"
        keys = redis_service.get_keys(pattern)
        
        deleted_count = 0
        for key in keys:
            if redis_service.delete_cache(key):
                deleted_count += 1
        
        print(f"🗑️ Invalidated {deleted_count} cache keys for session: {chat_session_id}")
        return deleted_count
    
    def get_cache_info(self, chat_session_id: str) -> Dict:
        """Get cache information for debugging"""
        pattern = f"ptit:{chat_session_id}:*"
        keys = redis_service.get_keys(pattern)
        
        return {
            "session_id": chat_session_id,
            "cached_keys": keys,
            "cache_count": len(keys),
            "ttl": self.cache_ttl
        }

# Global instance
ptit_cache_service = PTITCacheService()
