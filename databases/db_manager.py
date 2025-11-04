# Main Database Manager
# Handles connections and operations for all databases

import logging
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
import json
from datetime import datetime
from db_config import DatabaseConfig, DatabaseURLBuilder


logger = logging.getLogger(__name__)


class MySQLManager:
    """MySQL/MariaDB connection and query manager"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize MySQL manager"""
        self.config = config or DatabaseConfig.get_mysql_config()
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            import mysql.connector
            from mysql.connector import pooling

            self.pool = pooling.MySQLConnectionPool(**self.config)
            self.connection = self.pool.get_connection()
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info("✅ Connected to MySQL successfully")
            return True
        except Exception as e:
            logger.error(f"❌ MySQL connection failed: {e}")
            return False

    def execute(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Execute a SELECT query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return []

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Update failed: {e}")
            return 0

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("MySQL connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PostgreSQLManager:
    """PostgreSQL connection and query manager"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize PostgreSQL manager"""
        self.config = config or DatabaseConfig.get_postgresql_config()
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            from psycopg2 import pool

            self.pool = pool.SimpleConnectionPool(
                1,
                self.config.get("pool_size", 5),
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                connect_timeout=self.config.get("connect_timeout", 10),
            )
            self.connection = self.pool.getconn()
            self.cursor = self.connection.cursor()
            logger.info("✅ Connected to PostgreSQL successfully")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False

    def execute(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Execute a SELECT query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            # Convert results to list of dictionaries
            columns = [desc[0] for desc in self.cursor.description]
            results = []
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return []

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Update failed: {e}")
            return 0

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.pool.putconn(self.connection)
        logger.info("PostgreSQL connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RedisManager:
    """Redis connection and cache manager"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize Redis manager"""
        self.config = config or DatabaseConfig.get_redis_config()
        self.client = None

    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            import redis

            self.client = redis.Redis(
                host=self.config["host"],
                port=self.config["port"],
                db=self.config.get("db", 0),
                password=self.config.get("password"),
                ssl=self.config.get("ssl", False),
                socket_connect_timeout=self.config.get("socket_connect_timeout", 5),
                socket_timeout=self.config.get("socket_timeout", 5),
                retry_on_timeout=self.config.get("retry_on_timeout", True),
                decode_responses=True,
            )
            # Test connection
            self.client.ping()
            logger.info("✅ Connected to Redis successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            return False

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in Redis"""
        try:
            if ttl:
                self.client.setex(key, ttl, json.dumps(value))
            else:
                self.client.set(key, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"❌ Set failed: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"❌ Get failed: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Delete failed: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all keys in current Redis DB"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"❌ Clear all failed: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get Redis statistics"""
        try:
            info = self.client.info()
            return {
                "memory_used": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands": info.get("total_commands_processed"),
                "uptime": info.get("uptime_in_seconds"),
            }
        except Exception as e:
            logger.error(f"❌ Get stats failed: {e}")
            return {}

    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
        logger.info("Redis connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ElasticsearchManager:
    """ElasticSearch connection and search manager"""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize ElasticSearch manager"""
        self.config = config or DatabaseConfig.get_elasticsearch_config()
        self.client = None

    def connect(self) -> bool:
        """Connect to ElasticSearch"""
        try:
            from elasticsearch import Elasticsearch

            hosts = self.config.get("hosts", [{"host": "localhost", "port": 9200}])
            connection_params = {
                "hosts": hosts,
                "timeout": self.config.get("request_timeout", 30),
                "max_retries": self.config.get("max_retries", 3),
                "retry_on_timeout": self.config.get("retry_on_timeout", True),
            }

            if self.config.get("username"):
                connection_params["basic_auth"] = (
                    self.config["username"],
                    self.config.get("password", ""),
                )

            if self.config.get("verify_certs") == False:
                connection_params["verify_certs"] = False

            self.client = Elasticsearch(**connection_params)
            # Test connection
            self.client.info()
            logger.info("✅ Connected to ElasticSearch successfully")
            return True
        except Exception as e:
            logger.error(f"❌ ElasticSearch connection failed: {e}")
            return False

    def create_index(self, index_name: str, mapping: Optional[Dict] = None) -> bool:
        """Create an index"""
        try:
            if mapping:
                self.client.indices.create(index=index_name, body=mapping)
            else:
                self.client.indices.create(index=index_name)
            logger.info(f"✅ Index '{index_name}' created")
            return True
        except Exception as e:
            logger.error(f"❌ Create index failed: {e}")
            return False

    def delete_index(self, index_name: str) -> bool:
        """Delete an index"""
        try:
            self.client.indices.delete(index=index_name)
            logger.info(f"✅ Index '{index_name}' deleted")
            return True
        except Exception as e:
            logger.error(f"❌ Delete index failed: {e}")
            return False

    def index_document(self, index_name: str, doc_id: str, document: Dict) -> bool:
        """Index a document"""
        try:
            self.client.index(index=index_name, id=doc_id, body=document)
            return True
        except Exception as e:
            logger.error(f"❌ Index document failed: {e}")
            return False

    def search(self, index_name: str, query: Dict) -> List[Dict]:
        """Search documents"""
        try:
            results = self.client.search(index=index_name, body=query)
            return [hit["_source"] for hit in results["hits"]["hits"]]
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get ElasticSearch statistics"""
        try:
            stats = self.client.cluster.health()
            return {
                "status": stats.get("status"),
                "nodes": stats.get("number_of_nodes"),
                "active_shards": stats.get("active_shards"),
                "relocating_shards": stats.get("relocating_shards"),
                "initializing_shards": stats.get("initializing_shards"),
                "unassigned_shards": stats.get("unassigned_shards"),
            }
        except Exception as e:
            logger.error(f"❌ Get stats failed: {e}")
            return {}

    def close(self):
        """Close ElasticSearch connection"""
        if self.client:
            self.client.close()
        logger.info("ElasticSearch connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DatabaseManager:
    """Universal database manager for all supported databases"""

    def __init__(self):
        """Initialize database manager"""
        self.mysql = None
        self.postgresql = None
        self.redis = None
        self.elasticsearch = None

    def init_mysql(self, config: Optional[Dict] = None) -> MySQLManager:
        """Initialize MySQL manager"""
        self.mysql = MySQLManager(config)
        self.mysql.connect()
        return self.mysql

    def init_postgresql(self, config: Optional[Dict] = None) -> PostgreSQLManager:
        """Initialize PostgreSQL manager"""
        self.postgresql = PostgreSQLManager(config)
        self.postgresql.connect()
        return self.postgresql

    def init_redis(self, config: Optional[Dict] = None) -> RedisManager:
        """Initialize Redis manager"""
        self.redis = RedisManager(config)
        self.redis.connect()
        return self.redis

    def init_elasticsearch(self, config: Optional[Dict] = None) -> ElasticsearchManager:
        """Initialize ElasticSearch manager"""
        self.elasticsearch = ElasticsearchManager(config)
        self.elasticsearch.connect()
        return self.elasticsearch

    def health_check(self) -> Dict[str, bool]:
        """Check health of all databases"""
        status = {}

        # Check MySQL
        try:
            import mysql.connector

            mysql_mgr = MySQLManager()
            status["mysql"] = mysql_mgr.connect()
            if mysql_mgr.connection:
                mysql_mgr.close()
        except:
            status["mysql"] = False

        # Check PostgreSQL
        try:
            import psycopg2

            pg_mgr = PostgreSQLManager()
            status["postgresql"] = pg_mgr.connect()
            if pg_mgr.connection:
                pg_mgr.close()
        except:
            status["postgresql"] = False

        # Check Redis
        try:
            import redis

            redis_mgr = RedisManager()
            status["redis"] = redis_mgr.connect()
            if redis_mgr.client:
                redis_mgr.close()
        except:
            status["redis"] = False

        # Check ElasticSearch
        try:
            from elasticsearch import Elasticsearch

            es_mgr = ElasticsearchManager()
            status["elasticsearch"] = es_mgr.connect()
            if es_mgr.client:
                es_mgr.close()
        except:
            status["elasticsearch"] = False

        return status

    def close_all(self):
        """Close all database connections"""
        if self.mysql:
            self.mysql.close()
        if self.postgresql:
            self.postgresql.close()
        if self.redis:
            self.redis.close()
        if self.elasticsearch:
            self.elasticsearch.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()
