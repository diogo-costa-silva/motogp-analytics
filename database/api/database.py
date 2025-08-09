"""
MotoGP Database Connection Management
====================================
Purpose: Database connection handling with pooling and health checks
Author: Claude Code Assistant
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager with connection pooling"""
    
    def __init__(self, min_connections: int = 1, max_connections: int = 20):
        """Initialize database manager with connection pool"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'motogp_analytics'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_pool = None
        
    def connect(self) -> bool:
        """Initialize connection pool"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                **self.db_config,
                cursor_factory=RealDictCursor
            )
            logger.info(f"✅ Database connection pool created ({self.min_connections}-{self.max_connections} connections)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create connection pool: {e}")
            return False
            
    def disconnect(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            try:
                self.connection_pool.closeall()
                logger.info("🔌 Connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")
                
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if not self.connection_pool:
            raise RuntimeError("Database connection pool not initialized")
            
        connection = None
        try:
            # Get connection from pool
            connection = self.connection_pool.getconn()
            yield connection
            
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
            
        finally:
            if connection:
                # Return connection to pool
                self.connection_pool.putconn(connection)
                
    def test_connection(self) -> bool:
        """Test database connection health"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return bool(result)
                    
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
            
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_one: bool = False, fetch_all: bool = True) -> Any:
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    
                    if fetch_one:
                        return cursor.fetchone()
                    elif fetch_all:
                        return cursor.fetchall()
                    else:
                        return cursor.rowcount
                        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
            
    def execute_transaction(self, queries: list) -> bool:
        """Execute multiple queries in a transaction"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    for query_data in queries:
                        query = query_data.get('query')
                        params = query_data.get('params')
                        cursor.execute(query, params)
                        
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Transaction execution failed: {e}")
            return False

# Global database manager instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        if not _db_manager.connect():
            raise RuntimeError("Failed to initialize database connection")
    return _db_manager

def get_database():
    """FastAPI dependency for database connections"""
    try:
        db_manager = get_database_manager()
        with db_manager.get_connection() as conn:
            yield conn
    except Exception as e:
        logger.error(f"Database dependency failed: {e}")
        raise

class QueryBuilder:
    """SQL query builder utilities"""
    
    @staticmethod
    def build_where_clause(conditions: Dict[str, Any]) -> tuple:
        """Build WHERE clause from conditions dictionary"""
        if not conditions:
            return "", []
            
        where_parts = []
        params = []
        
        for field, value in conditions.items():
            if value is not None:
                if isinstance(value, str) and '%' in value:
                    where_parts.append(f"{field} ILIKE %s")
                    params.append(value)
                elif isinstance(value, list):
                    placeholders = ','.join(['%s'] * len(value))
                    where_parts.append(f"{field} IN ({placeholders})")
                    params.extend(value)
                else:
                    where_parts.append(f"{field} = %s")
                    params.append(value)
                    
        where_clause = " AND ".join(where_parts)
        return f"WHERE {where_clause}" if where_clause else "", params
        
    @staticmethod
    def build_order_clause(order_by: Optional[str] = None, order_dir: str = "ASC") -> str:
        """Build ORDER BY clause"""
        if order_by:
            return f"ORDER BY {order_by} {order_dir.upper()}"
        return ""
        
    @staticmethod
    def build_limit_offset(limit: Optional[int] = None, offset: int = 0) -> str:
        """Build LIMIT and OFFSET clause"""
        clause = ""
        if limit:
            clause += f" LIMIT {limit}"
        if offset > 0:
            clause += f" OFFSET {offset}"
        return clause

# Connection health monitoring
class ConnectionMonitor:
    """Monitor database connection health and performance"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.health_stats = {
            'total_queries': 0,
            'failed_queries': 0,
            'avg_response_time': 0.0,
            'last_health_check': None
        }
        
    def record_query(self, success: bool, response_time: float):
        """Record query statistics"""
        self.health_stats['total_queries'] += 1
        if not success:
            self.health_stats['failed_queries'] += 1
            
        # Update average response time
        current_avg = self.health_stats['avg_response_time']
        total_queries = self.health_stats['total_queries']
        self.health_stats['avg_response_time'] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
        
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get current health metrics"""
        success_rate = 0.0
        if self.health_stats['total_queries'] > 0:
            success_rate = (
                (self.health_stats['total_queries'] - self.health_stats['failed_queries']) 
                / self.health_stats['total_queries'] * 100
            )
            
        return {
            'total_queries': self.health_stats['total_queries'],
            'failed_queries': self.health_stats['failed_queries'],
            'success_rate_percent': round(success_rate, 2),
            'avg_response_time_ms': round(self.health_stats['avg_response_time'] * 1000, 2),
            'connection_pool_size': getattr(self.db_manager.connection_pool, '_pool', []),
            'database_status': 'healthy' if success_rate > 95 else 'degraded' if success_rate > 80 else 'unhealthy'
        }
        
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            connection_ok = self.db_manager.test_connection()
            response_time = time.time() - start_time
            
            self.record_query(connection_ok, response_time)
            self.health_stats['last_health_check'] = time.time()
            
            metrics = self.get_health_metrics()
            metrics['last_check_success'] = connection_ok
            metrics['last_check_time'] = self.health_stats['last_health_check']
            
            return metrics
            
        except Exception as e:
            self.record_query(False, time.time() - start_time)
            return {
                'status': 'error',
                'error': str(e),
                'last_check_time': time.time()
            }