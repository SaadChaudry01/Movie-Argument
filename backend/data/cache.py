"""Caching layer for API responses."""

import json
import aiosqlite
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import hashlib
from pathlib import Path

from config import get_settings


class CacheManager:
    """SQLite-based cache for API responses."""
    
    def __init__(self, db_path: str = "movie_cache.db"):
        self.db_path = db_path
        self._initialized = False
    
    async def initialize(self):
        """Initialize the cache database."""
        if self._initialized:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS movie_details (
                    movie_id INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    query_hash TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                ON cache(expires_at)
            """)
            
            await db.commit()
        
        self._initialized = True
    
    def _hash_key(self, key: str) -> str:
        """Create a hash of the cache key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT value FROM cache 
                WHERE key = ? AND expires_at > datetime('now')
                """,
                (key,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    # Update hit count
                    await db.execute(
                        "UPDATE cache SET hit_count = hit_count + 1 WHERE key = ?",
                        (key,)
                    )
                    await db.commit()
                    return json.loads(row[0])
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_hours: int = 24,
    ):
        """Set a value in cache."""
        await self.initialize()
        
        expires_at = datetime.now() + timedelta(hours=ttl_hours)
        value_json = json.dumps(value, default=str)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, expires_at)
                VALUES (?, ?, ?)
                """,
                (key, value_json, expires_at.isoformat())
            )
            await db.commit()
    
    async def get_movie(self, movie_id: int) -> Optional[Dict]:
        """Get cached movie details."""
        await self.initialize()
        
        settings = get_settings()
        ttl_hours = settings.cache_ttl_hours
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT data, updated_at FROM movie_details 
                WHERE movie_id = ?
                """,
                (movie_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    updated_at = datetime.fromisoformat(row[1])
                    if datetime.now() - updated_at < timedelta(hours=ttl_hours):
                        return json.loads(row[0])
        return None
    
    async def set_movie(self, movie_id: int, data: Dict):
        """Cache movie details."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO movie_details (movie_id, data, updated_at)
                VALUES (?, ?, datetime('now'))
                """,
                (movie_id, json.dumps(data, default=str))
            )
            await db.commit()
    
    async def get_search(self, query: str) -> Optional[Dict]:
        """Get cached search results."""
        await self.initialize()
        
        query_hash = self._hash_key(query.lower().strip())
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT results, created_at FROM search_cache 
                WHERE query_hash = ?
                """,
                (query_hash,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    created_at = datetime.fromisoformat(row[1])
                    # Search cache expires after 1 hour
                    if datetime.now() - created_at < timedelta(hours=1):
                        return json.loads(row[0])
        return None
    
    async def set_search(self, query: str, results: Dict):
        """Cache search results."""
        await self.initialize()
        
        query_hash = self._hash_key(query.lower().strip())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO search_cache (query_hash, query, results, created_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (query_hash, query, json.dumps(results, default=str))
            )
            await db.commit()
    
    async def clear_expired(self):
        """Clear expired cache entries."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM cache WHERE expires_at < datetime('now')"
            )
            await db.commit()
    
    async def get_stats(self) -> Dict:
        """Get cache statistics."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            async with db.execute("SELECT COUNT(*) FROM cache") as cursor:
                row = await cursor.fetchone()
                stats["total_entries"] = row[0] if row else 0
            
            async with db.execute("SELECT COUNT(*) FROM movie_details") as cursor:
                row = await cursor.fetchone()
                stats["cached_movies"] = row[0] if row else 0
            
            async with db.execute("SELECT COUNT(*) FROM search_cache") as cursor:
                row = await cursor.fetchone()
                stats["cached_searches"] = row[0] if row else 0
            
            async with db.execute(
                "SELECT SUM(hit_count) FROM cache"
            ) as cursor:
                row = await cursor.fetchone()
                stats["total_hits"] = row[0] if row and row[0] else 0
            
            return stats
    
    async def clear_all(self):
        """Clear all cache entries."""
        await self.initialize()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM cache")
            await db.execute("DELETE FROM movie_details")
            await db.execute("DELETE FROM search_cache")
            await db.commit()
