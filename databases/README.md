# Database Management System

Complete database management system for MySQL/MariaDB, PostgreSQL, Redis, and ElasticSearch.

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [API Reference](#api-reference)
5. [Backup & Recovery](#backup--recovery)
6. [Monitoring](#monitoring)
7. [Performance Tuning](#performance-tuning)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# MySQL/MariaDB
mysql --version

# PostgreSQL
psql --version

# Redis
redis-cli --version

# ElasticSearch
curl http://localhost:9200
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
mysql-connector-python==8.0.33
psycopg2-binary==2.9.9
redis==5.0.1
elasticsearch==8.10.0
python-dotenv==1.0.0
SQLAlchemy==2.0.23
```

### Docker Setup (Optional)

```bash
docker-compose up -d
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: moai_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: moai_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  mysql_data:
  postgres_data:
  redis_data:
  elasticsearch_data:
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and update:

```bash
cp databases/.env.example .env
```

### MySQL Configuration

```python
from databases.db_config import DatabaseConfig

config = DatabaseConfig.get_mysql_config()
# {
#     "host": "localhost",
#     "port": 3306,
#     "user": "root",
#     "password": "password",
#     "database": "moai_db",
#     ...
# }
```

### PostgreSQL Configuration

```python
config = DatabaseConfig.get_postgresql_config()
```

### Redis Configuration

```python
config = DatabaseConfig.get_redis_config()
```

### ElasticSearch Configuration

```python
config = DatabaseConfig.get_elasticsearch_config()
```

---

## 💻 Usage

### MySQL Operations

```python
from databases.db_manager import MySQLManager

# Create connection
mysql = MySQLManager()
mysql.connect()

# Execute query
result = mysql.execute("SELECT * FROM users WHERE id = %s", (1,))

# Insert/Update
rows_affected = mysql.execute_update(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ("John", "john@example.com")
)

# Close connection
mysql.close()
```

### PostgreSQL Operations

```python
from databases.db_manager import PostgreSQLManager

# Create connection
postgres = PostgreSQLManager()
postgres.connect()

# Execute query
result = postgres.execute(
    "SELECT * FROM users WHERE id = %s",
    (1,)
)

# Context manager
with PostgreSQLManager() as pg:
    result = pg.execute("SELECT * FROM users")
    print(result)
```

### Redis Operations

```python
from databases.db_manager import RedisManager

redis = RedisManager()
redis.connect()

# Set value
redis.set("user:1", {"name": "John", "email": "john@example.com"}, ttl=3600)

# Get value
user = redis.get("user:1")

# Delete key
redis.delete("user:1")

# Clear all
redis.clear_all()

# Get stats
stats = redis.get_stats()
print(f"Memory used: {stats['memory_used']}")
print(f"Connected clients: {stats['connected_clients']}")

redis.close()
```

### ElasticSearch Operations

```python
from databases.db_manager import ElasticsearchManager

es = ElasticsearchManager()
es.connect()

# Create index
es.create_index("products", {
    "mappings": {
        "properties": {
            "name": {"type": "text"},
            "price": {"type": "float"},
            "description": {"type": "text"}
        }
    }
})

# Index document
es.index_document("products", "1", {
    "name": "Product 1",
    "price": 99.99,
    "description": "High quality product"
})

# Search
results = es.search("products", {
    "query": {
        "match": {"name": "product"}
    }
})

# Get stats
stats = es.get_stats()
print(f"Status: {stats['status']}")
print(f"Active shards: {stats['active_shards']}")

es.close()
```

### Universal Database Manager

```python
from databases.db_manager import DatabaseManager

# Initialize all databases
with DatabaseManager() as db:
    db.init_mysql()
    db.init_postgresql()
    db.init_redis()
    db.init_elasticsearch()
    
    # Check health
    status = db.health_check()
    print(status)
    # {
    #     "mysql": True,
    #     "postgresql": True,
    #     "redis": True,
    #     "elasticsearch": True
    # }
```

---

## 📚 API Reference

### MySQLManager

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect()` | - | bool | Connect to database |
| `execute()` | query, params | List[Dict] | Execute SELECT query |
| `execute_update()` | query, params | int | Execute INSERT/UPDATE/DELETE |
| `close()` | - | - | Close connection |

### PostgreSQLManager

Same as MySQLManager

### RedisManager

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect()` | - | bool | Connect to Redis |
| `set()` | key, value, ttl | bool | Set value |
| `get()` | key | Any | Get value |
| `delete()` | key | bool | Delete key |
| `clear_all()` | - | bool | Clear all keys |
| `get_stats()` | - | Dict | Get statistics |
| `close()` | - | - | Close connection |

### ElasticsearchManager

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `connect()` | - | bool | Connect to ES |
| `create_index()` | index_name, mapping | bool | Create index |
| `delete_index()` | index_name | bool | Delete index |
| `index_document()` | index, doc_id, doc | bool | Index document |
| `search()` | index, query | List | Search documents |
| `get_stats()` | - | Dict | Get statistics |
| `close()` | - | - | Close connection |

---

## 💾 Backup & Recovery

### MySQL Backup

```python
from databases.db_utils import DatabaseBackup
from databases.db_config import DatabaseConfig

config = DatabaseConfig.get_mysql_config()
DatabaseBackup.backup_mysql(config, "backup.sql")
```

### PostgreSQL Backup

```python
config = DatabaseConfig.get_postgresql_config()
DatabaseBackup.backup_postgresql(config, "backup.sql")
```

### Redis Backup

```python
from databases.db_manager import RedisManager

redis = RedisManager()
redis.connect()
DatabaseBackup.backup_redis(redis.client, "redis_backup.json")
```

### Restore from Backup

```python
# MySQL
DatabaseBackup.restore_from_backup("mysql", config, "backup.sql")

# PostgreSQL
DatabaseBackup.restore_from_backup("postgresql", config, "backup.sql")

# Redis
DatabaseBackup.restore_from_backup("redis", config, "backup.json")
```

---

## 📊 Monitoring

### Health Check

```python
from databases.db_manager import DatabaseManager

manager = DatabaseManager()
status = manager.health_check()
# {
#     "mysql": True,
#     "postgresql": True,
#     "redis": True,
#     "elasticsearch": True
# }
```

### Get Database Info

```python
from databases.db_utils import DatabaseMonitoring

info = DatabaseMonitoring.get_database_info(manager)
print(info)
```

### Monitor Slow Queries

```python
slow_queries = DatabaseMonitoring.monitor_slow_queries(manager, threshold_ms=1000)
for query in slow_queries:
    print(f"DB: {query['db']}")
    print(f"Query: {query['query']}")
```

### Check Locks

```python
locks = DatabaseMonitoring.check_database_locks(manager)
for lock in locks:
    print(f"Database: {lock['db']}")
    print(f"Lock info: {lock['lock']}")
```

---

## ⚙️ Performance Tuning

### MySQL Optimization

```sql
-- Enable query cache
SET GLOBAL query_cache_size = 268435456;
SET GLOBAL query_cache_type = 1;

-- Optimize tables
OPTIMIZE TABLE users;

-- Check index usage
SELECT * FROM sys.statements_with_full_table_scans;

-- Create index
CREATE INDEX idx_user_email ON users(email);
```

### PostgreSQL Optimization

```sql
-- Analyze tables
ANALYZE;

-- Vacuum
VACUUM ANALYZE;

-- Check index usage
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname != 'pg_catalog';

-- Create index
CREATE INDEX idx_user_email ON users(email);

-- View query plans
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'john@example.com';
```

### Redis Optimization

```python
# Use pipelining
with redis.pipeline() as pipe:
    pipe.set('key1', 'value1')
    pipe.set('key2', 'value2')
    pipe.execute()

# Use appropriate data types
redis.set('string_key', 'value')
redis.lpush('list_key', 'item1', 'item2')
redis.sadd('set_key', 'member1', 'member2')
redis.hset('hash_key', mapping={'field1': 'value1'})

# Monitor performance
info = redis.get_stats()
```

### ElasticSearch Optimization

```python
# Use bulk operations
from elasticsearch.helpers import bulk

docs = [
    {"_index": "products", "_id": "1", "_source": {"name": "Product 1"}},
    {"_index": "products", "_id": "2", "_source": {"name": "Product 2"}},
]
bulk(es.client, docs)

# Optimize index
es.client.indices.forcemerge(index="products")

# Set replicas and shards
es.client.indices.put_settings(
    index="products",
    body={"settings": {"number_of_replicas": 1, "number_of_shards": 5}}
)
```

---

## 🔧 Troubleshooting

### Connection Issues

```python
# Test connection
from databases.db_manager import DatabaseManager

manager = DatabaseManager()
status = manager.health_check()

if not status['mysql']:
    print("❌ MySQL connection failed")
    # Check credentials, host, port
    # Verify MySQL service is running
```

### Performance Issues

```python
# Monitor slow queries
from databases.db_utils import DatabaseMonitoring

slow = DatabaseMonitoring.monitor_slow_queries(manager)
print(f"Found {len(slow)} slow queries")

# Check for locks
locks = DatabaseMonitoring.check_database_locks(manager)
print(f"Found {len(locks)} locks")

# Review indexes
# Use EXPLAIN to analyze queries
# Consider adding indexes for frequently queried columns
```

### Memory Issues

```python
# Redis memory usage
stats = redis.get_stats()
print(f"Memory: {stats['memory_used']}")

# Set max memory policy
redis.client.config_set('maxmemory-policy', 'allkeys-lru')

# Monitor ElasticSearch memory
es_stats = elasticsearch.get_stats()
print(f"Cluster status: {es_stats['status']}")
```

---

## 📁 File Structure

```
databases/
├── db_config.py          # Configuration manager
├── db_manager.py         # Connection managers
├── db_utils.py           # Utilities and helpers
├── .env.example          # Environment template
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── migrations/           # Migration files
│   └── 001_initial.sql   # Initial schema
├── backups/              # Database backups
│   ├── mysql/
│   ├── postgresql/
│   ├── redis/
│   └── elasticsearch/
└── logs/                 # Database logs
    └── database.log
```

---

## 🔒 Security Best Practices

1. **Never commit .env files**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables for credentials**
   ```python
   from databases.db_config import DatabaseConfig
   # Credentials loaded from .env
   ```

3. **Enable SSL/TLS connections**
   ```
   POSTGRES_SSLMODE=require
   REDIS_SSL=true
   ELASTICSEARCH_SCHEME=https
   ```

4. **Implement connection pooling**
   - MySQL: `pool_size=5`
   - PostgreSQL: `pool_size=5`
   - Redis: `max_connections=50`

5. **Regular backups**
   ```python
   DatabaseBackup.backup_mysql(config, f"backup_{date}.sql")
   ```

---

## 📞 Support

For issues or questions:
- Check error logs in `logs/database.log`
- Review configuration in `.env`
- Test connections individually
- Check database service status
- Review performance metrics

---

**Database Management System Ready! 🎉**
