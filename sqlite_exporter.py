#!/usr/bin/env python3

import sqlite3
import time
import os
import logging
from prometheus_client import start_http_server, Gauge, Counter
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite Database Metrics
sqlite_db_size_bytes = Gauge('sqlite_db_size_bytes', 'SQLite database file size in bytes')
sqlite_table_count = Gauge('sqlite_table_count', 'Number of tables in database')
sqlite_total_rows = Gauge('sqlite_total_rows', 'Total number of rows across all tables')
sqlite_page_count = Gauge('sqlite_page_count', 'Number of pages in database')
sqlite_page_size = Gauge('sqlite_page_size_bytes', 'SQLite page size in bytes')
sqlite_cache_size = Gauge('sqlite_cache_size_pages', 'SQLite cache size in pages')
sqlite_schema_version = Gauge('sqlite_schema_version', 'SQLite schema version')
sqlite_journal_mode = Gauge('sqlite_journal_mode', 'SQLite journal mode (1=DELETE, 2=TRUNCATE, 3=PERSIST, 4=MEMORY, 5=WAL, 6=OFF)')

# Table-specific metrics
sqlite_table_row_count = Gauge('sqlite_table_row_count', 'Number of rows in table', ['table_name'])
sqlite_table_size_bytes = Gauge('sqlite_table_size_bytes', 'Size of table in bytes', ['table_name'])

# Query performance metrics
sqlite_query_time_seconds = Gauge('sqlite_query_time_seconds', 'SQLite query execution time', ['query_type'])
sqlite_exporter_errors_total = Counter('sqlite_exporter_errors_total', 'Total SQLite exporter errors')

class SQLiteExporter:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            sqlite_exporter_errors_total.inc()
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        """Execute SQLite query with timing"""
        start_time = time.time()
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            execution_time = time.time() - start_time
            return result, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed: {e}")
            sqlite_exporter_errors_total.inc()
            return None, execution_time

    def collect_database_info(self):
        """Collect general database information"""
        start_time = time.time()
        try:
            # Database file size
            if os.path.exists(self.db_path):
                db_size = os.path.getsize(self.db_path)
                sqlite_db_size_bytes.set(db_size)

            # Page count and page size
            result, exec_time = self.execute_query("PRAGMA page_count")
            if result:
                sqlite_page_count.set(result[0][0])
                sqlite_query_time_seconds.labels(query_type='page_count').set(exec_time)

            result, exec_time = self.execute_query("PRAGMA page_size")
            if result:
                sqlite_page_size.set(result[0][0])
                sqlite_query_time_seconds.labels(query_type='page_size').set(exec_time)

            # Cache size
            result, exec_time = self.execute_query("PRAGMA cache_size")
            if result:
                sqlite_cache_size.set(result[0][0])
                sqlite_query_time_seconds.labels(query_type='cache_size').set(exec_time)

            # Schema version
            result, exec_time = self.execute_query("PRAGMA schema_version")
            if result:
                sqlite_schema_version.set(result[0][0])
                sqlite_query_time_seconds.labels(query_type='schema_version').set(exec_time)

            # Journal mode
            result, exec_time = self.execute_query("PRAGMA journal_mode")
            if result:
                journal_mode_map = {'delete': 1, 'truncate': 2, 'persist': 3, 'memory': 4, 'wal': 5, 'off': 6}
                mode = result[0][0].lower()
                sqlite_journal_mode.set(journal_mode_map.get(mode, 0))
                sqlite_query_time_seconds.labels(query_type='journal_mode').set(exec_time)

        except Exception as e:
            logger.error(f"Error collecting database info: {e}")
            sqlite_exporter_errors_total.inc()

    def collect_table_info(self):
        """Collect table-specific information"""
        start_time = time.time()
        try:
            # Get table names
            result, exec_time = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            sqlite_query_time_seconds.labels(query_type='table_list').set(exec_time)

            if result:
                table_names = [row[0] for row in result]
                sqlite_table_count.set(len(table_names))

                total_rows = 0
                for table_name in table_names:
                    try:
                        # Get row count for each table
                        row_result, row_exec_time = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
                        if row_result:
                            row_count = row_result[0][0]
                            sqlite_table_row_count.labels(table_name=table_name).set(row_count)
                            total_rows += row_count
                            sqlite_query_time_seconds.labels(query_type='row_count').set(row_exec_time)

                        # Estimate table size (this is approximate for SQLite)
                        size_result, size_exec_time = self.execute_query(
                            f"SELECT SUM(CASE WHEN typeof(name) == 'text' THEN length(name) + 3 "
                            f"WHEN typeof(name) == 'integer' THEN 8 "
                            f"WHEN typeof(name) == 'real' THEN 8 "
                            f"ELSE 4 END) FROM {table_name}"
                        )
                        if size_result and size_result[0][0]:
                            table_size = size_result[0][0]
                            sqlite_table_size_bytes.labels(table_name=table_name).set(table_size)
                            sqlite_query_time_seconds.labels(query_type='table_size').set(size_exec_time)

                    except Exception as e:
                        logger.warning(f"Error collecting info for table {table_name}: {e}")
                        continue

                sqlite_total_rows.set(total_rows)

        except Exception as e:
            logger.error(f"Error collecting table info: {e}")
            sqlite_exporter_errors_total.inc()

    def collect_performance_metrics(self):
        """Collect performance-related metrics"""
        try:
            # Test query performance
            queries = [
                ("SELECT 1", 'test_query'),
                ("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1", 'metadata_query'),
            ]

            for query, query_type in queries:
                try:
                    _, exec_time = self.execute_query(query)
                    sqlite_query_time_seconds.labels(query_type=query_type).set(exec_time)
                except Exception as e:
                    logger.warning(f"Performance test failed for {query_type}: {e}")

        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            sqlite_exporter_errors_total.inc()

    def collect_metrics(self):
        """Main metrics collection function"""
        if not self.connect():
            return

        try:
            logger.info("Starting SQLite metrics collection...")

            # Collect different types of metrics
            self.collect_database_info()
            self.collect_table_info()
            self.collect_performance_metrics()

            logger.info("SQLite metrics collection completed")

        except Exception as e:
            logger.error(f"Error in metrics collection: {e}")
            sqlite_exporter_errors_total.inc()
        finally:
            self.disconnect()

def main():
    """Main function"""
    db_path = os.getenv('SQLITE_DB_PATH', '/app/movies.db')
    update_interval = int(os.getenv('UPDATE_INTERVAL', 15))

    logger.info(f"Starting SQLite exporter on port 9187")
    logger.info(f"Database path: {db_path}")
    logger.info(f"Update interval: {update_interval}s")

    # Create exporter instance
    exporter = SQLiteExporter(db_path)

    # Check if database exists
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        # Create a sample database for testing
        logger.info("Creating sample database for testing...")
        conn = sqlite3.connect(db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                year INTEGER,
                rating REAL
            )
        ''')

        # Insert sample data
        sample_movies = [
            (1, 'The Matrix', 1999, 8.7),
            (2, 'Inception', 2010, 8.8),
            (3, 'Interstellar', 2014, 8.6)
        ]

        conn.executemany('INSERT OR REPLACE INTO movies VALUES (?, ?, ?, ?)', sample_movies)
        conn.commit()
        conn.close()
        logger.info("Sample database created successfully")

    # Start HTTP server
    start_http_server(9187)

    # Initial collection
    exporter.collect_metrics()

    # Periodic collection
    while True:
        time.sleep(update_interval)
        exporter.collect_metrics()

if __name__ == '__main__':
    main()