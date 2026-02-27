from fastapi import FastAPI , HTTPException , Depends , Query
from app.database import db
from app.queries import SEARCH_AUTHORS_QUERY
from app.models import AuthorResponse , SearchQuery
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Library API",
    description="A simple library API",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    db.connect()

@app.on_event("shutdown")
def shutdown():
    db.close_all_connections()

@app.get("/search/authors" , response_model=List[AuthorResponse])
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
