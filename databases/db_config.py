# Database Configuration Manager
# Supports: MySQL/MariaDB, PostgreSQL, Redis, ElasticSearch

import os
from typing import Dict, Optional
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Central database configuration manager"""

    # MySQL/MariaDB Configuration
    MYSQL_CONFIG = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "moai_db"),
        "charset": "utf8mb4",
        "autocommit": True,
        "pool_size": int(os.getenv("MYSQL_POOL_SIZE", 5)),
        "max_overflow": int(os.getenv("MYSQL_MAX_OVERFLOW", 10)),
        "pool_recycle": int(os.getenv("MYSQL_POOL_RECYCLE", 3600)),
    }

    # PostgreSQL Configuration
    POSTGRESQL_CONFIG = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "database": os.getenv("POSTGRES_DATABASE", "moai_db"),
        "sslmode": os.getenv("POSTGRES_SSLMODE", "prefer"),
        "pool_size": int(os.getenv("POSTGRES_POOL_SIZE", 5)),
        "max_overflow": int(os.getenv("POSTGRES_MAX_OVERFLOW", 10)),
        "pool_recycle": int(os.getenv("POSTGRES_POOL_RECYCLE", 3600)),
        "connect_timeout": int(os.getenv("POSTGRES_TIMEOUT", 10)),
    }

    # Redis Configuration
    REDIS_CONFIG = {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": int(os.getenv("REDIS_DB", 0)),
        "password": os.getenv("REDIS_PASSWORD", None),
        "ssl": os.getenv("REDIS_SSL", "false").lower() == "true",
        "ssl_certfile": os.getenv("REDIS_SSL_CERTFILE", None),
        "ssl_keyfile": os.getenv("REDIS_SSL_KEYFILE", None),
        "ssl_ca_certs": os.getenv("REDIS_SSL_CA_CERTS", None),
        "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", 50)),
        "socket_keepalive": os.getenv("REDIS_KEEPALIVE", "true").lower() == "true",
        "socket_connect_timeout": int(os.getenv("REDIS_CONNECT_TIMEOUT", 5)),
        "socket_timeout": int(os.getenv("REDIS_SOCKET_TIMEOUT", 5)),
        "retry_on_timeout": os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true",
    }

    # ElasticSearch Configuration
    ELASTICSEARCH_CONFIG = {
        "hosts": [
            {
                "host": os.getenv("ELASTICSEARCH_HOST", "localhost"),
                "port": int(os.getenv("ELASTICSEARCH_PORT", 9200)),
                "scheme": os.getenv("ELASTICSEARCH_SCHEME", "http"),
            }
        ],
        "username": os.getenv("ELASTICSEARCH_USER", None),
        "password": os.getenv("ELASTICSEARCH_PASSWORD", None),
        "verify_certs": os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true",
        "ca_certs": os.getenv("ELASTICSEARCH_CA_CERTS", None),
        "request_timeout": int(os.getenv("ELASTICSEARCH_TIMEOUT", 30)),
        "max_retries": int(os.getenv("ELASTICSEARCH_MAX_RETRIES", 3)),
        "retry_on_timeout": os.getenv("ELASTICSEARCH_RETRY_ON_TIMEOUT", "true").lower() == "true",
        "min_delay_between_retrying": float(os.getenv("ELASTICSEARCH_MIN_DELAY", 0.1)),
        "max_delay_between_retrying": float(os.getenv("ELASTICSEARCH_MAX_DELAY", 10.0)),
    }

    # Database Selection
    DATABASE_SELECTION = {
        "primary": os.getenv("PRIMARY_DB", "postgresql"),  # postgresql or mysql
        "cache": os.getenv("CACHE_DB", "redis"),  # redis
        "search": os.getenv("SEARCH_DB", "elasticsearch"),  # elasticsearch
    }

    @classmethod
    def get_mysql_config(cls) -> Dict:
        """Get MySQL configuration"""
        return cls.MYSQL_CONFIG.copy()

    @classmethod
    def get_postgresql_config(cls) -> Dict:
        """Get PostgreSQL configuration"""
        return cls.POSTGRESQL_CONFIG.copy()

    @classmethod
    def get_redis_config(cls) -> Dict:
        """Get Redis configuration"""
        return cls.REDIS_CONFIG.copy()

    @classmethod
    def get_elasticsearch_config(cls) -> Dict:
        """Get ElasticSearch configuration"""
        return cls.ELASTICSEARCH_CONFIG.copy()

    @classmethod
    def get_primary_db_config(cls) -> Dict:
        """Get primary database configuration"""
        primary_db = cls.DATABASE_SELECTION.get("primary", "postgresql")
        if primary_db.lower() == "mysql":
            return cls.get_mysql_config()
        else:
            return cls.get_postgresql_config()

    @classmethod
    def get_cache_db_config(cls) -> Dict:
        """Get cache database configuration"""
        return cls.get_redis_config()

    @classmethod
    def get_search_db_config(cls) -> Dict:
        """Get search database configuration"""
        return cls.get_elasticsearch_config()

    @classmethod
    def to_dict(cls) -> Dict:
        """Convert all configurations to dictionary"""
        return {
            "mysql": cls.get_mysql_config(),
            "postgresql": cls.get_postgresql_config(),
            "redis": cls.get_redis_config(),
            "elasticsearch": cls.get_elasticsearch_config(),
            "selection": cls.DATABASE_SELECTION,
        }

    @classmethod
    def print_config(cls, show_passwords: bool = False) -> None:
        """Print configuration for debugging"""
        config = cls.to_dict()

        if not show_passwords:
            if config["mysql"]["password"]:
                config["mysql"]["password"] = "***"
            if config["postgresql"]["password"]:
                config["postgresql"]["password"] = "***"
            if config["redis"]["password"]:
                config["redis"]["password"] = "***"
            if config["elasticsearch"]["password"]:
                config["elasticsearch"]["password"] = "***"

        print(json.dumps(config, indent=2))


class DatabaseURLBuilder:
    """Build connection URLs for different databases"""

    @staticmethod
    def build_mysql_url(config: Optional[Dict] = None) -> str:
        """Build MySQL connection URL"""
        if config is None:
            config = DatabaseConfig.get_mysql_config()

        url = f"mysql+pymysql://{config['user']}"
        if config.get("password"):
            url += f":{config['password']}"
        url += f"@{config['host']}:{config['port']}/{config['database']}"
        url += f"?charset={config.get('charset', 'utf8mb4')}"
        return url

    @staticmethod
    def build_postgresql_url(config: Optional[Dict] = None) -> str:
        """Build PostgreSQL connection URL"""
        if config is None:
            config = DatabaseConfig.get_postgresql_config()

        url = f"postgresql://{config['user']}"
        if config.get("password"):
            url += f":{config['password']}"
        url += f"@{config['host']}:{config['port']}/{config['database']}"
        if config.get("sslmode"):
            url += f"?sslmode={config['sslmode']}"
        return url

    @staticmethod
    def build_redis_url(config: Optional[Dict] = None) -> str:
        """Build Redis connection URL"""
        if config is None:
            config = DatabaseConfig.get_redis_config()

        scheme = "rediss" if config.get("ssl") else "redis"
        url = f"{scheme}://"
        if config.get("password"):
            url += f":{config['password']}@"
        url += f"{config['host']}:{config['port']}/{config.get('db', 0)}"
        return url

    @staticmethod
    def build_elasticsearch_url(config: Optional[Dict] = None) -> str:
        """Build ElasticSearch connection URL"""
        if config is None:
            config = DatabaseConfig.get_elasticsearch_config()

        hosts = config.get("hosts", [{}])[0]
        scheme = hosts.get("scheme", "http")
        host = hosts.get("host", "localhost")
        port = hosts.get("port", 9200)

        url = f"{scheme}://"
        if config.get("username"):
            url += f"{config['username']}"
            if config.get("password"):
                url += f":{config['password']}"
            url += "@"
        url += f"{host}:{port}"
        return url
