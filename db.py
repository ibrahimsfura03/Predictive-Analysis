"""
Database Module for Student Performance Prediction System
Handles all SQLite database operations, schema definitions, and initialization.
"""

import sqlite3
from datetime import datetime
import os

# Database configuration
DATABASE = 'database.db'


def get_db_connection():
    """
    Create and return a database connection.
    Configures row factory to access columns by name.
    
    Returns:
        sqlite3.Connection: Database connection object with row factory set
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """
    Initialize database with required tables.
    Creates students and predictions tables if they don't exist.
    
    Schema:
    - students: Stores student records with credentials and performance data
    - predictions: Stores prediction results linked to students via foreign key
    
    Constraints:
    - students.matric_no: UNIQUE constraint
    - predictions.student_id: FOREIGN KEY reference to students.id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign key support
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Create students table
    # Stores student credentials and performance metrics used for predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            level TEXT NOT NULL,
            attendance REAL NOT NULL,
            ca_score REAL NOT NULL,
            exam_score REAL NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create predictions table
    # Stores prediction results linked to students via foreign key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")


# ==================== STUDENT OPERATIONS ====================

def insert_student(matric_no, name, department, level, attendance, ca_score, exam_score, password_hash):
    """
    Insert new student record into database.
    
    Args:
        matric_no (str): Unique student matric number
        name (str): Student's full name
        department (str): Department name
        level (str): Academic level (e.g., "100", "200", "300", "400")
        attendance (float): Attendance percentage (0-100)
        ca_score (float): Continuous assessment score (0-100)
        exam_score (float): Exam score (0-100)
        password_hash (str): Hashed password
    
    Returns:
        int: ID of newly inserted student record
    
    Raises:
        sqlite3.IntegrityError: If matric_no already exists (uniqueness constraint)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO students (matric_no, name, department, level, attendance, ca_score, exam_score, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (matric_no, name, department, level, attendance, ca_score, exam_score, password_hash))
        
        student_id = cursor.lastrowid
        conn.commit()
        return student_id
    
    finally:
        conn.close()


def get_student_by_id(student_id):
    """
    Retrieve specific student record by ID.
    
    Args:
        student_id (int): Student ID (primary key)
    
    Returns:
        dict: Student record with all columns, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    conn.close()
    
    return dict(student) if student else None


def get_student_by_matric_no(matric_no):
    """
    Retrieve specific student record by matric number.
    Used for student authentication and login.
    
    Args:
        matric_no (str): Student's matric number
    
    Returns:
        dict: Student record with all columns, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students WHERE matric_no = ?', (matric_no,))
    student = cursor.fetchone()
    conn.close()
    
    return dict(student) if student else None


def get_all_students():
    """
    Retrieve all student records (excluding password_hash for security).
    
    Returns:
        list: List of dict records with student information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, matric_no, name, department, level, attendance, ca_score, exam_score
        FROM students
        ORDER BY name
    ''')
    
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return students


def update_student(student_id, matric_no=None, name=None, department=None, level=None, 
                   attendance=None, ca_score=None, exam_score=None):
    """
    Update student record with provided fields.
    Only updates fields that are not None.
    
    Args:
        student_id (int): Student ID to update
        matric_no (str, optional): Updated matric number
        name (str, optional): Updated student name
        department (str, optional): Updated department
        level (str, optional): Updated academic level
        attendance (float, optional): Updated attendance percentage
        ca_score (float, optional): Updated CA score
        exam_score (float, optional): Updated exam score
    
    Returns:
        bool: True if update was successful, False if student not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    updates = []
    values = []
    
    if matric_no is not None:
        updates.append('matric_no = ?')
        values.append(matric_no)
    if name is not None:
        updates.append('name = ?')
        values.append(name)
    if department is not None:
        updates.append('department = ?')
        values.append(department)
    if level is not None:
        updates.append('level = ?')
        values.append(level)
    if attendance is not None:
        updates.append('attendance = ?')
        values.append(attendance)
    if ca_score is not None:
        updates.append('ca_score = ?')
        values.append(ca_score)
    if exam_score is not None:
        updates.append('exam_score = ?')
        values.append(exam_score)
    
    if not updates:
        conn.close()
        return True  # No updates requested
    
    values.append(student_id)
    query = f"UPDATE students SET {', '.join(updates)} WHERE id = ?"
    
    cursor.execute(query, values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success


def delete_student(student_id):
    """
    Delete student record and associated predictions.
    Cascades to delete related prediction records.
    
    Args:
        student_id (int): Student ID to delete
    
    Returns:
        bool: True if deletion was successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete associated predictions first
    cursor.execute('DELETE FROM predictions WHERE student_id = ?', (student_id,))
    
    # Delete student record
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success


# ==================== PREDICTION OPERATIONS ====================

def insert_prediction(student_id, risk_level, recommendation):
    """
    Insert new prediction record into database with foreign key reference.
    
    Args:
        student_id (int): Reference to student ID (foreign key)
        risk_level (str): Predicted risk status ("At Risk" or "Not At Risk")
        recommendation (str): Comma-separated recommendations for student
    
    Returns:
        int: ID of newly inserted prediction record
    
    Raises:
        sqlite3.IntegrityError: If student_id doesn't exist (foreign key constraint)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO predictions (student_id, risk_level, recommendation)
            VALUES (?, ?, ?)
        ''', (student_id, risk_level, recommendation))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        return prediction_id
    
    finally:
        conn.close()


def get_prediction_by_id(prediction_id):
    """
    Retrieve specific prediction record by ID.
    
    Args:
        prediction_id (int): Prediction ID (primary key)
    
    Returns:
        dict: Prediction record with all columns, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))
    prediction = cursor.fetchone()
    conn.close()
    
    return dict(prediction) if prediction else None


def get_prediction_with_student_by_id(prediction_id):
    """
    Retrieve specific prediction record with joined student information.
    Used to display full prediction details to admin.
    
    Args:
        prediction_id (int): Prediction ID (primary key)
    
    Returns:
        dict: Prediction record with joined student data, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, s.matric_no, s.name, s.department, s.level,
               s.attendance, s.ca_score, s.exam_score
        FROM predictions p
        JOIN students s ON p.student_id = s.id
        WHERE p.id = ?
    ''', (prediction_id,))
    
    prediction = cursor.fetchone()
    conn.close()
    
    return dict(prediction) if prediction else None


def get_all_predictions():
    """
    Retrieve all prediction records ordered by prediction_date descending.
    
    Returns:
        list: List of dict records with all prediction data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM predictions
        ORDER BY prediction_date DESC
    ''')
    
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return predictions


def get_all_predictions_with_students():
    """
    Retrieve all prediction records with joined student information.
    Used to display prediction history with student details to admin.
    
    Returns:
        list: List of dict records with prediction and student data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, s.matric_no, s.name, s.department, s.level,
               s.attendance, s.ca_score, s.exam_score
        FROM predictions p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.prediction_date DESC
    ''')
    
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return predictions


def get_predictions_by_student_id(student_id):
    """
    Retrieve all prediction records for a specific student.
    Implements data isolation - students can only view their own predictions.
    
    Args:
        student_id (int): Student ID to filter predictions
    
    Returns:
        list: List of dict records with predictions for this student
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM predictions
        WHERE student_id = ?
        ORDER BY prediction_date DESC
    ''', (student_id,))
    
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return predictions


def get_latest_prediction_by_student_id(student_id):
    """
    Retrieve most recent prediction for a specific student.
    Used for student portal to show latest prediction result.
    
    Args:
        student_id (int): Student ID to retrieve latest prediction
    
    Returns:
        dict: Latest prediction record, or None if no predictions exist
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM predictions
        WHERE student_id = ?
        ORDER BY prediction_date DESC
        LIMIT 1
    ''', (student_id,))
    
    prediction = cursor.fetchone()
    conn.close()
    
    return dict(prediction) if prediction else None


def delete_prediction(prediction_id):
    """
    Delete specific prediction record from database.
    
    Args:
        prediction_id (int): Prediction ID to delete
    
    Returns:
        bool: True if deletion was successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success


# ==================== STATISTICS AND ANALYTICS ====================

def get_statistics():
    """
    Calculate dashboard statistics from predictions and students tables.
    
    Returns:
        dict: Statistics with keys:
            - total_students: Total number of students in system
            - total_predictions: Total predictions made
            - at_risk_count: Number of "At Risk" predictions
            - not_at_risk_count: Number of "Not At Risk" predictions
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count total students
    cursor.execute('SELECT COUNT(*) as count FROM students')
    total_students = cursor.fetchone()['count']
    
    # Count total predictions and group by risk level
    cursor.execute('''
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN risk_level = 'At Risk' THEN 1 ELSE 0 END) as at_risk,
               SUM(CASE WHEN risk_level = 'Not At Risk' THEN 1 ELSE 0 END) as not_at_risk
        FROM predictions
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'total_students': total_students,
        'total_predictions': result['total'] or 0,
        'at_risk_count': result['at_risk'] or 0,
        'not_at_risk_count': result['not_at_risk'] or 0
    }


def get_risk_factor_counts():
    """
    Calculate frequency of each risk factor from prediction records.
    Used for bar chart visualization in dashboard.
    
    Risk factors:
    - Low attendance: attendance < 60
    - Low CA score: ca_score < 50
    - Low exam score: exam_score < 50
    
    Returns:
        dict: Risk factor counts with keys:
            - low_attendance: Count of students with attendance < 60
            - low_ca: Count of students with ca_score < 50
            - low_exam: Count of students with exam_score < 50
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Join predictions with students to access performance data
    cursor.execute('''
        SELECT s.attendance, s.ca_score, s.exam_score
        FROM predictions p
        JOIN students s ON p.student_id = s.id
    ''')
    
    records = cursor.fetchall()
    conn.close()
    
    low_attendance = sum(1 for r in records if r['attendance'] < 60)
    low_ca = sum(1 for r in records if r['ca_score'] < 50)
    low_exam = sum(1 for r in records if r['exam_score'] < 50)
    
    return {
        'low_attendance': low_attendance,
        'low_ca': low_ca,
        'low_exam': low_exam
    }


# ==================== DATABASE MAINTENANCE ====================

def clear_all_data():
    """
    Clear all data from students and predictions tables.
    WARNING: This is destructive and cannot be undone without backup.
    
    Returns:
        bool: True if operation was successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM predictions')
        cursor.execute('DELETE FROM students')
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_database_info():
    """
    Get information about database tables and record counts.
    
    Returns:
        dict: Database information with keys:
            - students_count: Number of student records
            - predictions_count: Number of prediction records
            - database_size: Size of database file in bytes
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get record counts
    cursor.execute('SELECT COUNT(*) as count FROM students')
    students_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM predictions')
    predictions_count = cursor.fetchone()['count']
    
    conn.close()
    
    # Get database file size
    if os.path.exists(DATABASE):
        db_size = os.path.getsize(DATABASE)
    else:
        db_size = 0
    
    return {
        'students_count': students_count,
        'predictions_count': predictions_count,
        'database_size': db_size
    }
