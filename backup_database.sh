#!/bin/bash
# SQLite Database Backup Script
# Creates a timestamped backup of database.db

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
SOURCE_DB="database.db"
BACKUP_FILE="${BACKUP_DIR}/database_backup_${TIMESTAMP}.db"

# Create backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Copy database file
cp "$SOURCE_DB" "$BACKUP_FILE"

echo "✅ Database backed up successfully!"
echo "📁 Backup location: $BACKUP_FILE"
echo "📊 Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
