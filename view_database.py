#!/usr/bin/env python3
"""
SQLite Database Viewer
View all data in a formatted table (similar to phpMyAdmin)
"""

import sqlite3
from datetime import datetime

DATABASE = 'database.db'

def print_table(title, headers, rows):
    """Print data in a formatted table."""
    print("\n" + "=" * 80)
    print(f"📊 {title}")
    print("=" * 80)
    
    if not rows:
        print("⚠️  No data found")
        return
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            max_width = max(max_width, len(str(row[i])))
        col_widths.append(min(max_width + 2, 40))  # Max 40 chars per column
    
    # Print header
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(str(val)[:40].ljust(w) for val, w in zip(row, col_widths))
        print(row_line)
    
    print(f"\n📈 Total Records: {len(rows)}")

def view_students():
    """View all students."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, matric_no, name, department, level, attendance, ca_score, exam_score FROM students')
    rows = cursor.fetchall()
    conn.close()
    
    headers = ['ID', 'Matric No', 'Name', 'Department', 'Level', 'Attendance', 'CA Score', 'Exam Score']
    print_table('STUDENTS TABLE', headers, rows)

def view_predictions():
    """View all predictions with student names."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, s.matric_no, s.name, p.risk_level, p.recommendation, p.prediction_date
        FROM predictions p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.prediction_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    headers = ['ID', 'Matric No', 'Student Name', 'Risk Level', 'Recommendation', 'Prediction Date']
    print_table('PREDICTIONS TABLE', headers, rows)

def show_statistics():
    """Show database statistics."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM predictions')
    total_predictions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'At Risk'")
    at_risk_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("📊 DATABASE STATISTICS")
    print("=" * 80)
    print(f"👥 Total Students: {total_students}")
    print(f"🔮 Total Predictions: {total_predictions}")
    print(f"⚠️  Students At Risk: {at_risk_count}")
    print(f"✅ Students Not At Risk: {total_predictions - at_risk_count}")
    print("=" * 80)

def main():
    """Main viewer function."""
    print("\n" + "=" * 80)
    print("🗄️  STUDENT PERFORMANCE PREDICTION DATABASE VIEWER")
    print("=" * 80)
    print(f"📁 Database: {DATABASE}")
    print(f"🕐 Accessed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    show_statistics()
    view_students()
    view_predictions()
    
    print("\n" + "=" * 80)
    print("✅ Database view complete!")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
