"""
Database Configuration
For use with the Model/Datasource architecture
"""

import os

# MySQL Connection Settings
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'pycgi'),
    'password': os.getenv('DB_PASSWORD', 'bf6912'),
    'database': os.getenv('DB_NAME', 'httpstack'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True
}

# Connection Pool Settings
DB_POOL = {
    'pool_name': 'httpstack_pool',
    'pool_size': 5,
    'max_overflow': 10,
}

# Query timeout (seconds)
QUERY_TIMEOUT = 30

# Enable/disable query logging
DEBUG_QUERIES = os.getenv('DEBUG_QUERIES', 'False').lower() == 'true'
