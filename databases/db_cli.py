#!/usr/bin/env python3
"""
Database Management CLI Tool
Command-line interface for managing all databases
"""

import sys
import argparse
import json
from typing import Optional
from datetime import datetime
import logging

from db_config import DatabaseConfig, DatabaseURLBuilder
from db_manager import DatabaseManager
from db_utils import (
    DatabaseUtils,
    DatabaseBackup,
    DatabaseMonitoring,
    DatabaseMigration,
    create_env_file,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_header(text: str) -> None:
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def cmd_status(args) -> None:
    """Check database connection status"""
    print_header("Database Status Check")

    manager = DatabaseManager()
    status = manager.health_check()

    for db, is_connected in status.items():
        symbol = "✅" if is_connected else "❌"
        print(f"{symbol} {db.upper()}: {'Connected' if is_connected else 'Failed'}")

    # Print detailed info
    if any(status.values()):
        print("\n📊 Configuration:")
        if status.get("mysql"):
            print(f"  MySQL: {DatabaseURLBuilder.build_mysql_url()}")
        if status.get("postgresql"):
            print(f"  PostgreSQL: {DatabaseURLBuilder.build_postgresql_url()}")
        if status.get("redis"):
            print(f"  Redis: {DatabaseURLBuilder.build_redis_url()}")
        if status.get("elasticsearch"):
            print(f"  ElasticSearch: {DatabaseURLBuilder.build_elasticsearch_url()}")


def cmd_config(args) -> None:
    """Display current configuration"""
    print_header("Database Configuration")

    show_passwords = args.show_passwords if hasattr(args, "show_passwords") else False
    DatabaseConfig.print_config(show_passwords=show_passwords)


def cmd_backup(args) -> None:
    """Create database backup"""
    print_header(f"Backing up {args.database}")

    db_type = args.database
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backups/{db_type}/{db_type}_backup_{timestamp}.sql"

    if db_type == "mysql":
        config = DatabaseConfig.get_mysql_config()
        success = DatabaseBackup.backup_mysql(config, output_file)
    elif db_type == "postgresql":
        config = DatabaseConfig.get_postgresql_config()
        success = DatabaseBackup.backup_postgresql(config, output_file)
    elif db_type == "redis":
        redis_mgr = DatabaseManager().init_redis()
        success = DatabaseBackup.backup_redis(redis_mgr.client, output_file)
    else:
        print(f"❌ Unsupported database: {db_type}")
        return

    if success:
        print(f"✅ Backup created: {output_file}")
    else:
        print(f"❌ Backup failed")


def cmd_restore(args) -> None:
    """Restore database from backup"""
    print_header(f"Restoring {args.database}")

    db_type = args.database
    backup_file = args.file

    if db_type == "mysql":
        config = DatabaseConfig.get_mysql_config()
        success = DatabaseBackup.restore_from_backup(db_type, config, backup_file)
    elif db_type == "postgresql":
        config = DatabaseConfig.get_postgresql_config()
        success = DatabaseBackup.restore_from_backup(db_type, config, backup_file)
    elif db_type == "redis":
        config = DatabaseConfig.get_redis_config()
        success = DatabaseBackup.restore_from_backup(db_type, config, backup_file)
    else:
        print(f"❌ Unsupported database: {db_type}")
        return

    if success:
        print(f"✅ Database restored from: {backup_file}")
    else:
        print(f"❌ Restore failed")


def cmd_info(args) -> None:
    """Display database information"""
    print_header("Database Information")

    manager = DatabaseManager()
    manager.init_mysql()
    manager.init_postgresql()
    manager.init_redis()
    manager.init_elasticsearch()

    info = DatabaseMonitoring.get_database_info(manager)
    print(json.dumps(info, indent=2))


def cmd_monitor(args) -> None:
    """Monitor database performance"""
    print_header("Database Monitoring")

    manager = DatabaseManager()
    manager.init_mysql()
    manager.init_postgresql()
    manager.init_redis()
    manager.init_elasticsearch()

    # Show slow queries
    print("\n⏱️  Slow Queries (threshold: 1000ms):")
    slow_queries = DatabaseMonitoring.monitor_slow_queries(manager)
    if slow_queries:
        for query in slow_queries[:5]:
            print(f"  - {query['db']}: {query}")
    else:
        print("  ✅ No slow queries found")

    # Show locks
    print("\n🔒 Database Locks:")
    locks = DatabaseMonitoring.check_database_locks(manager)
    if locks:
        for lock in locks[:5]:
            print(f"  - {lock['db']}: {lock}")
    else:
        print("  ✅ No locks found")

    # Show stats
    print("\n📊 Statistics:")
    if manager.redis:
        stats = manager.redis.get_stats()
        print(f"  Redis Memory: {stats.get('memory_used')}")
        print(f"  Redis Clients: {stats.get('connected_clients')}")

    if manager.elasticsearch:
        stats = manager.elasticsearch.get_stats()
        print(f"  ES Status: {stats.get('status')}")
        print(f"  ES Nodes: {stats.get('nodes')}")


def cmd_migrate(args) -> None:
    """Create or run migrations"""
    print_header("Database Migrations")

    migration = DatabaseMigration()

    if args.action == "create":
        if migration.create_migration(args.name, args.database_type):
            print(f"✅ Migration created: {args.name}")
        else:
            print(f"❌ Failed to create migration")

    elif args.action == "list":
        migrations = migration.get_migrations()
        print(f"Found {len(migrations)} migrations:")
        for m in migrations:
            print(f"  - {m}")

    elif args.action == "run":
        print("⚠️  Migration execution not yet implemented")
        print("Use migration files with database CLI tools")


def cmd_init(args) -> None:
    """Initialize database environment"""
    print_header("Initializing Database Environment")

    # Create .env file
    create_env_file(".env")
    print("✅ Created .env file")

    # Create directories
    import os

    dirs = ["backups/mysql", "backups/postgresql", "backups/redis", "logs", "migrations"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

    print("\n📝 Next steps:")
    print("  1. Edit .env file with your database credentials")
    print("  2. Run 'python db_cli.py status' to verify connections")
    print("  3. Use other commands to manage your databases")


def cmd_test_connection(args) -> None:
    """Test connection to specific database"""
    print_header(f"Testing {args.database} Connection")

    try:
        if args.database == "mysql":
            from db_manager import MySQLManager

            mgr = MySQLManager()
            if mgr.connect():
                result = mgr.execute("SELECT 1 as test")
                print(f"✅ MySQL connection successful")
                print(f"   Result: {result}")
                mgr.close()
            else:
                print(f"❌ MySQL connection failed")

        elif args.database == "postgresql":
            from db_manager import PostgreSQLManager

            mgr = PostgreSQLManager()
            if mgr.connect():
                result = mgr.execute("SELECT 1 as test")
                print(f"✅ PostgreSQL connection successful")
                print(f"   Result: {result}")
                mgr.close()
            else:
                print(f"❌ PostgreSQL connection failed")

        elif args.database == "redis":
            from db_manager import RedisManager

            mgr = RedisManager()
            if mgr.connect():
                mgr.set("test_key", "test_value")
                value = mgr.get("test_key")
                mgr.delete("test_key")
                print(f"✅ Redis connection successful")
                print(f"   Value: {value}")
                mgr.close()
            else:
                print(f"❌ Redis connection failed")

        elif args.database == "elasticsearch":
            from db_manager import ElasticsearchManager

            mgr = ElasticsearchManager()
            if mgr.connect():
                stats = mgr.get_stats()
                print(f"✅ ElasticSearch connection successful")
                print(f"   Status: {stats}")
                mgr.close()
            else:
                print(f"❌ ElasticSearch connection failed")

    except Exception as e:
        print(f"❌ Error: {e}")


def main() -> None:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Database Management CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check connection status
  python db_cli.py status
  
  # Create backup
  python db_cli.py backup --database mysql
  
  # Display configuration
  python db_cli.py config
  
  # Monitor databases
  python db_cli.py monitor
  
  # Test connection
  python db_cli.py test --database postgresql
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    subparsers.add_parser("status", help="Check database status")

    # Config command
    config_parser = subparsers.add_parser("config", help="Display configuration")
    config_parser.add_argument(
        "--show-passwords", action="store_true", help="Show passwords in config"
    )

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument(
        "--database",
        choices=["mysql", "postgresql", "redis"],
        required=True,
        help="Database to backup",
    )

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument(
        "--database",
        choices=["mysql", "postgresql", "redis"],
        required=True,
        help="Database to restore",
    )
    restore_parser.add_argument("--file", required=True, help="Backup file path")

    # Info command
    subparsers.add_parser("info", help="Display database information")

    # Monitor command
    subparsers.add_parser("monitor", help="Monitor database performance")

    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Manage migrations")
    migrate_parser.add_argument(
        "action",
        choices=["create", "list", "run"],
        help="Migration action",
    )
    migrate_parser.add_argument("--name", help="Migration name")
    migrate_parser.add_argument("--database-type", default="postgresql", help="Database type")

    # Init command
    subparsers.add_parser("init", help="Initialize database environment")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test database connection")
    test_parser.add_argument(
        "--database",
        choices=["mysql", "postgresql", "redis", "elasticsearch"],
        required=True,
        help="Database to test",
    )

    args = parser.parse_args()

    # Execute commands
    if args.command == "status":
        cmd_status(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "backup":
        cmd_backup(args)
    elif args.command == "restore":
        cmd_restore(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "migrate":
        cmd_migrate(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "test":
        cmd_test_connection(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
