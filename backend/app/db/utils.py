import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .connection import get_session

logger = logging.getLogger(__name__)

def check_db_ready() -> dict:
    """
    Check if the database is ready and accessible.

    Returns:
        dict: Status information with 'ready' boolean and optional error message
    """
    try:
        session = get_session()
        # Simple query to test database connectivity
        session.execute(text("SELECT 1"))
        session.close()
        return {"ready": True}
    except SQLAlchemyError as e:
        logger.error(f"Database readiness check failed: {e}")
        return {"ready": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error during database readiness check: {e}")
        return {"ready": False, "error": str(e)}

def soft_delete_filter(query, model_class):
    """
    Apply soft delete filter to a query.

    Args:
        query: SQLAlchemy query object
        model_class: Model class with deleted_at column

    Returns:
        Filtered query excluding soft-deleted records
    """
    if hasattr(model_class, 'deleted_at'):
        return query.filter(model_class.deleted_at.is_(None))
    return query

def paginate_query(query, cursor=None, limit=50):
    """
    Apply cursor-based pagination to a query.

    Args:
        query: SQLAlchemy query object
        cursor: Cursor value (typically created_at timestamp)
        limit: Maximum number of results to return

    Returns:
        Tuple of (paginated_query, next_cursor)
    """
    if cursor:
        # Assuming cursor is a timestamp, filter for records after cursor
        query = query.filter(query._primary_entity.created_at > cursor)

    # Order by created_at for consistent pagination
    query = query.order_by(query._primary_entity.created_at)

    # Limit results
    results = query.limit(limit + 1).all()

    # Determine next cursor
    next_cursor = None
    if len(results) > limit:
        next_cursor = results[-1].created_at
        results = results[:-1]

    return results, next_cursor
