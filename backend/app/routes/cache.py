from flask import Blueprint, request, jsonify
from ..services.ptit_cache_service import ptit_cache_service
from ..config.redis_config import redis_service

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/cache/info/<chat_session_id>', methods=['GET'])
def get_cache_info(chat_session_id):
    """Get cache information for a chat session"""
    try:
        cache_info = ptit_cache_service.get_cache_info(chat_session_id)
        return jsonify(cache_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cache_bp.route('/cache/clear/<chat_session_id>', methods=['DELETE'])
def clear_session_cache(chat_session_id):
    """Clear all cache for a chat session"""
    try:
        deleted_count = ptit_cache_service.invalidate_session_cache(chat_session_id)
        return jsonify({
            "message": f"Cleared {deleted_count} cache entries",
            "session_id": chat_session_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cache_bp.route('/cache/health', methods=['GET'])
def cache_health():
    """Check Redis connection health"""
    try:
        is_connected = redis_service.is_connected()
        
        # Get some stats if connected
        stats = {}
        if is_connected:
            try:
                info = redis_service.redis_client.info()
                stats = {
                    "used_memory_human": info.get('used_memory_human'),
                    "connected_clients": info.get('connected_clients'),
                    "total_commands_processed": info.get('total_commands_processed'),
                    "keyspace_hits": info.get('keyspace_hits'),
                    "keyspace_misses": info.get('keyspace_misses')
                }
            except:
                pass
        
        return jsonify({
            "redis_connected": is_connected,
            "status": "healthy" if is_connected else "disconnected",
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cache_bp.route('/cache/keys', methods=['GET'])
def list_cache_keys():
    """List all PTIT cache keys (for debugging)"""
    try:
        pattern = request.args.get('pattern', 'ptit:*')
        keys = redis_service.get_keys(pattern)
        
        return jsonify({
            "pattern": pattern,
            "keys": keys,
            "count": len(keys)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
