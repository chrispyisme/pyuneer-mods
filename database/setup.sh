#!/bin/bash
# ============================================================================
# Database Setup Script
# Usage: bash database/setup.sh
# ============================================================================

# MySQL Credentials
MYSQL_USER="pycgi"
MYSQL_PASSWORD="bf6912"
MYSQL_DATABASE="httpstack"

# Run the SQL script
echo "Setting up database schema and test data..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < "$(dirname "$0")/schema.sql"

if [ $? -eq 0 ]; then
    echo "✓ Database setup completed successfully!"
    echo ""
    echo "Tables created:"
    mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "SHOW TABLES;"
else
    echo "✗ Database setup failed!"
    exit 1
fi
