# Database Utilities and Helpers

import os
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


logger = logging.getLogger(__name__)


class DatabaseUtils:
    """Utility functions for database operations"""

    @staticmethod
    def generate_connection_string(db_type: str, config: Dict) -> str:
        """Generate connection string for database"""
        if db_type == "mysql":
            return f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        elif db_type == "postgresql":
            return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        elif db_type == "redis":
            password = f":{config['password']}@" if config.get("password") else ""
            return f"redis://{password}{config['host']}:{config['port']}/{config.get('db', 0)}"
        elif db_type == "elasticsearch":
            user = config.get("username", "")
            password = config.get("password", "")
            auth = f"{user}:{password}@" if user else ""
            host = config["hosts"][0]["host"]
            port = config["hosts"][0]["port"]
            return f"http://{auth}{host}:{port}"
        return ""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def validate_connection_string(connection_string: str, db_type: str) -> bool:
        """Validate connection string format"""
        if db_type == "mysql":
            return connection_string.startswith("mysql://")
        elif db_type == "postgresql":
            return connection_string.startswith("postgresql://")
        elif db_type == "redis":
            return connection_string.startswith("redis://")
        elif db_type == "elasticsearch":
            return connection_string.startswith("http")
        return False

    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize SQL query for logging"""
        # Remove sensitive data
        sanitized = query.lower()
        sensitive_keywords = ["password", "secret", "token", "key"]
        for keyword in sensitive_keywords:
            if keyword in sanitized:
                return f"{query[:100]}... [SANITIZED]"
        return query

    @staticmethod
    def format_db_size(size_bytes: int) -> str:
        """Format database size to human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()

    @staticmethod
    def parse_dsn(dsn: str) -> Dict:
        """Parse database connection DSN"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(dsn)
            return {
                "scheme": parsed.scheme,
                "user": parsed.username,
                "password": parsed.password,
                "host": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path.lstrip("/"),
                "query": parsed.query,
            }
        except Exception as e:
            logger.error(f"DSN parse failed: {e}")
            return {}


class DatabaseMigration:
    """Database migration utilities"""

    def __init__(self, migrations_dir: str = "./migrations"):
        """Initialize migrations"""
        self.migrations_dir = migrations_dir
        self.executed_migrations = []

    def create_migration(self, name: str, db_type: str) -> bool:
        """Create a new migration file"""
        try:
            os.makedirs(self.migrations_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{name}.sql"
            filepath = os.path.join(self.migrations_dir, filename)

            with open(filepath, "w") as f:
                f.write(f"-- Migration: {name}\n")
                f.write(f"-- Database: {db_type}\n")
                f.write(f"-- Created: {datetime.now()}\n\n")
                f.write("-- ADD YOUR SQL HERE\n")

            logger.info(f"✅ Migration created: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Create migration failed: {e}")
            return False

    def get_migrations(self) -> List[str]:
        """Get list of migration files"""
        try:
            migrations = sorted(os.listdir(self.migrations_dir))
            return [m for m in migrations if m.endswith(".sql")]
        except Exception as e:
            logger.error(f"❌ Get migrations failed: {e}")
            return []

    def record_migration(self, migration_name: str, status: str) -> None:
        """Record migration execution"""
        self.executed_migrations.append(
            {"name": migration_name, "status": status, "timestamp": DatabaseUtils.get_timestamp()}
        )


class DatabaseBackup:
    """Database backup utilities"""

    @staticmethod
    def backup_mysql(config: Dict, output_file: str) -> bool:
        """Backup MySQL database"""
        try:
            import subprocess

            cmd = [
                "mysqldump",
                f"--host={config['host']}",
                f"--port={config['port']}",
                f"--user={config['user']}",
                f"--password={config.get('password', '')}",
                config["database"],
            ]

            with open(output_file, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)

            logger.info(f"✅ MySQL backup created: {output_file}")
            return True
        except Exception as e:
            logger.error(f"❌ MySQL backup failed: {e}")
            return False

    @staticmethod
    def backup_postgresql(config: Dict, output_file: str) -> bool:
        """Backup PostgreSQL database"""
        try:
            import subprocess

            env = os.environ.copy()
            env["PGPASSWORD"] = config.get("password", "")

            cmd = [
                "pg_dump",
                f"--host={config['host']}",
                f"--port={config['port']}",
                f"--username={config['user']}",
                config["database"],
            ]

            with open(output_file, "w") as f:
                subprocess.run(cmd, stdout=f, env=env, check=True)

            logger.info(f"✅ PostgreSQL backup created: {output_file}")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL backup failed: {e}")
            return False

    @staticmethod
    def backup_redis(redis_client, output_file: str) -> bool:
        """Backup Redis database"""
        try:
            # Get all keys
            all_data = {}
            for key in redis_client.keys():
                value = redis_client.get(key)
                all_data[key] = value

            with open(output_file, "w") as f:
                json.dump(all_data, f, indent=2)

            logger.info(f"✅ Redis backup created: {output_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Redis backup failed: {e}")
            return False

    @staticmethod
    def restore_from_backup(db_type: str, config: Dict, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            if db_type == "mysql":
                import subprocess

                with open(backup_file, "r") as f:
                    subprocess.run(
                        [
                            "mysql",
                            f"--host={config['host']}",
                            f"--port={config['port']}",
                            f"--user={config['user']}",
                            f"--password={config.get('password', '')}",
                            config["database"],
                        ],
                        stdin=f,
                        check=True,
                    )

            elif db_type == "postgresql":
                import subprocess

                env = os.environ.copy()
                env["PGPASSWORD"] = config.get("password", "")

                with open(backup_file, "r") as f:
                    subprocess.run(
                        [
                            "psql",
                            f"--host={config['host']}",
                            f"--port={config['port']}",
                            f"--username={config['user']}",
                            config["database"],
                        ],
                        stdin=f,
                        env=env,
                        check=True,
                    )

            elif db_type == "redis":
                import redis

                with open(backup_file, "r") as f:
                    data = json.load(f)
                    client = redis.Redis(**config)
                    for key, value in data.items():
                        client.set(key, value)

            logger.info(f"✅ Database restored from: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False


class DatabaseMonitoring:
    """Database monitoring and performance utilities"""

    @staticmethod
    def get_database_info(manager) -> Dict:
        """Get database information and statistics"""
        info = {
            "timestamp": DatabaseUtils.get_timestamp(),
            "databases": {},
        }

        # MySQL info
        if manager.mysql:
            try:
                result = manager.mysql.execute(
                    "SELECT database() as db, "
                    "COUNT(*) as tables FROM information_schema.tables "
                    "WHERE table_schema = database()"
                )
                info["databases"]["mysql"] = result
            except:
                pass

        # PostgreSQL info
        if manager.postgresql:
            try:
                result = manager.postgresql.execute(
                    "SELECT datname, "
                    "count(*) FROM information_schema.tables "
                    "GROUP BY datname"
                )
                info["databases"]["postgresql"] = result
            except:
                pass

        # Redis info
        if manager.redis:
            try:
                info["databases"]["redis"] = manager.redis.get_stats()
            except:
                pass

        # ElasticSearch info
        if manager.elasticsearch:
            try:
                info["databases"]["elasticsearch"] = manager.elasticsearch.get_stats()
            except:
                pass

        return info

    @staticmethod
    def monitor_slow_queries(manager, threshold_ms: int = 1000) -> List[Dict]:
        """Monitor slow queries"""
        slow_queries = []

        # MySQL slow queries
        if manager.mysql:
            try:
                result = manager.mysql.execute(
                    "SELECT * FROM mysql.slow_log WHERE start_time > "
                    "DATE_SUB(NOW(), INTERVAL 1 HOUR) LIMIT 10"
                )
                for query in result:
                    slow_queries.append({"db": "mysql", "query": query})
            except:
                pass

        # PostgreSQL slow queries
        if manager.postgresql:
            try:
                result = manager.postgresql.execute(
                    "SELECT query, mean_exec_time FROM pg_stat_statements "
                    "WHERE mean_exec_time > %s ORDER BY mean_exec_time DESC LIMIT 10",
                    (threshold_ms,),
                )
                for query in result:
                    slow_queries.append({"db": "postgresql", "query": query})
            except:
                pass

        return slow_queries

    @staticmethod
    def check_database_locks(manager) -> List[Dict]:
        """Check for database locks"""
        locks = []

        # MySQL locks
        if manager.mysql:
            try:
                result = manager.mysql.execute(
                    "SELECT * FROM information_schema.processlist "
                    "WHERE state LIKE '%lock%' OR state LIKE '%wait%'"
                )
                for lock in result:
                    locks.append({"db": "mysql", "lock": lock})
            except:
                pass

        # PostgreSQL locks
        if manager.postgresql:
            try:
                result = manager.postgresql.execute(
                    "SELECT * FROM pg_locks WHERE NOT granted"
                )
                for lock in result:
                    locks.append({"db": "postgresql", "lock": lock})
            except:
                pass

        return locks


def create_env_file(output_file: str = ".env") -> bool:
    """Create a sample .env file"""
    env_template = """# ========================================
# Database Configuration - .env Template
# ========================================

# MySQL/MariaDB Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=moai_db
MYSQL_POOL_SIZE=5
MYSQL_MAX_OVERFLOW=10
MYSQL_POOL_RECYCLE=3600

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
POSTGRES_DATABASE=moai_db
POSTGRES_SSLMODE=prefer
POSTGRES_POOL_SIZE=5
POSTGRES_MAX_OVERFLOW=10
POSTGRES_POOL_RECYCLE=3600
POSTGRES_TIMEOUT=10

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_SSL_CERTFILE=
REDIS_SSL_KEYFILE=
REDIS_SSL_CA_CERTS=
REDIS_MAX_CONNECTIONS=50
REDIS_KEEPALIVE=true
REDIS_CONNECT_TIMEOUT=5
REDIS_SOCKET_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true

# ElasticSearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_SCHEME=http
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_VERIFY_CERTS=true
ELASTICSEARCH_CA_CERTS=
ELASTICSEARCH_TIMEOUT=30
ELASTICSEARCH_MAX_RETRIES=3
ELASTICSEARCH_RETRY_ON_TIMEOUT=true
ELASTICSEARCH_MIN_DELAY=0.1
ELASTICSEARCH_MAX_DELAY=10.0

# Database Selection
PRIMARY_DB=postgresql
CACHE_DB=redis
SEARCH_DB=elasticsearch

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/database.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
"""

    try:
        with open(output_file, "w") as f:
            f.write(env_template)
        logger.info(f"✅ Created {output_file}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create {output_file}: {e}")
        return False


if __name__ == "__main__":
    # Create .env file
    create_env_file()
    print("✅ Database utilities initialized")
