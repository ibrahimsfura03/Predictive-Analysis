#!/usr/bin/env python3
"""
SQLite Database Export Utility
Exports all tables to CSV files for viewing in Excel/Sheets
"""

import sqlite3
import csv
import os
from datetime import datetime

DATABASE = 'database.db'
EXPORT_DIR = 'exports'

def export_table_to_csv(table_name):
    """Export a specific table to CSV format."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all data from table
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    
    if not rows:
        print(f"⚠️  Table '{table_name}' is empty")
        conn.close()
        return
    
    # Create exports directory
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{EXPORT_DIR}/{table_name}_{timestamp}.csv'
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write headers
        headers = rows[0].keys()
        writer.writerow(headers)
        
        # Write data
        for row in rows:
            writer.writerow(row)
    
    conn.close()
    print(f"✅ Exported {len(rows)} rows from '{table_name}' to {filename}")

def main():
    """Export all tables to CSV."""
    print("=" * 60)
    print("SQLite Database Export Utility")
    print("=" * 60)
    
    if not os.path.exists(DATABASE):
        print(f"❌ Database file '{DATABASE}' not found!")
        return
    
    # Get all table names
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"\n📊 Found {len(tables)} tables: {', '.join(tables)}\n")
    
    # Export each table
    for table in tables:
        export_table_to_csv(table)
    
    print("\n" + "=" * 60)
    print(f"✅ Export complete! Files saved to '{EXPORT_DIR}/' directory")
    print("=" * 60)

if __name__ == '__main__':
    main()
