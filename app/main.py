from fastapi import FastAPI , HTTPException , Depends , Query
from app.database import db
from app.queries import SEARCH_AUTHORS_QUERY
from app.models import AuthorResponse , SearchQuery
from app.config import settings
import logging
from typing import List
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis.asyncio as redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("Connecting to Redis...")
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding = "utf-8",
        decode_responses = False
    )
    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="library-api-cache"
    )
    logger.info("Redis connected")
    db.connect()
    logger.info(" PostgreSQL connected")
    logger.info("Cache system ready!")


    yield

    logger.info("Shutting down...")
    db.close_all_connections()
    await redis_client.close()
    logger.info("Connections closed")


app = FastAPI(
    title="Library API with Redis Cache",
    description="A simple library API with Redis caching",
    version="3.0.0",
    lifespan=lifespan
)

@app.get("/search/authors" , response_model=List[AuthorResponse])
@cache(expire=60)
async def search_authors(
    q: str = Query(... , min_length=1 , description="Search query for author name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results to return")
    ):
    """
    search for authors by name.(case insensitive partial match)
    Returns author name and number of books written.
    """
    conn = None
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        search_pattern = f"%{q}%"
        cursor.execute(SEARCH_AUTHORS_QUERY, (search_pattern, limit))

        results = cursor.fetchall()

        cursor.close()

        logger.info(f"Found {len(results)} authors matching query: {q}")
        return results
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if conn:
            db.return_connection(conn)
@app.get("/cache-stats")
async def get_cache_stats():
    """Get Redis cache statistics"""
    try:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
            )
        keys = await redis_client.keys("library-api-cache:*")
        key_count = len(keys)

        info = await redis_client.info()

        await redis_client.close()

        return{
            "total_cached_items": key_count,
            "cache_prefix": "library-api-cache" ,
            "redis_version" :info.get("redis_version"), 
            "used_memory_human" : info.get("used_memory_human"),
            "total_connections_received": info.get("total_connections_received"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "sample_keys": keys[:5] if keys else []
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}
    
@app.post("/cache-clear")
async def cache_clear():
    """Clear all Redis cache"""
    try:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
            )
        keys = await redis_client.keys("library-api-cache:*")
        for key in keys:
            await redis_client.delete(key)
        await redis_client.close()
        return{
            "message":f"Cleared {len(keys)} items from Redis cache",
            "cleared_count" : len(keys)
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500 , detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "cache" : "redis",
        "database":"postgresql"    
    }
