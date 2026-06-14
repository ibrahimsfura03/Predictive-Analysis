"""
Student Performance Prediction System - Flask Application
A web-based system for predicting student academic risk status using machine learning.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pickle
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'  # Change this in production

# Database configuration
DATABASE = 'database.db'

# Admin credentials (hardcoded for simplicity)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# ==================== DATABASE FUNCTIONS ====================

def get_db_connection():
    """Create and return database connection with timeout handling."""
    conn = sqlite3.connect(DATABASE, timeout=10.0)  # 10 second timeout
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging for better concurrency
    return conn

def init_db():
    """Initialize database with required tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create students table
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
    except sqlite3.OperationalError as e:
        print(f"Database initialization error: {e}")
        print("Please ensure the database is accessible and try again.")
        exit(1)

# ==================== HELPER FUNCTIONS ====================

def load_model():
    """Load trained ML model from disk."""
    try:
        import sklearn  # Verify sklearn is available
    except ImportError:
        raise ImportError("sklearn not installed. Run: pip install scikit-learn")
    
    if not os.path.exists('model.pkl'):
        raise FileNotFoundError("Model file not found. Run: python train_model.py")
    
    try:
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}")

def generate_recommendations(attendance, ca_score, exam_score):
    """
    Generate recommendations based on performance thresholds.
    
    Args:
        attendance: Attendance percentage (0-100)
        ca_score: Continuous assessment score (0-100)
        exam_score: Exam score (0-100)
        
    Returns:
        String containing comma-separated recommendations
    """
    recommendations = []
    
    if attendance < 60:
        recommendations.append("Improve attendance")
    
    if ca_score < 50:
        recommendations.append("Improve continuous assessment performance")
    
    if exam_score < 50:
        recommendations.append("Improve examination preparation")
    
    if not recommendations:
        recommendations.append("Keep up the good work!")
    
    return ", ".join(recommendations)

def calculate_statistics():
    """Calculate dashboard statistics from students table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all students
    cursor.execute('SELECT id FROM students')
    students = cursor.fetchall()
    total_students = len(students)
    
    # Get predictions for each student
    at_risk = 0
    not_at_risk = 0
    
    for student in students:
        cursor.execute('SELECT risk_level FROM predictions WHERE student_id = ? ORDER BY prediction_date DESC LIMIT 1', 
                      (student['id'],))
        latest_pred = cursor.fetchone()
        if latest_pred:
            if latest_pred['risk_level'] == 'At Risk':
                at_risk += 1
            else:
                not_at_risk += 1
    
    conn.close()
    
    return {
        'total': total_students,
        'at_risk': at_risk,
        'not_at_risk': not_at_risk
    }

def get_risk_factor_counts():
    """Calculate frequency of each risk factor for bar chart."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Join predictions with students to get performance data
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

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login for both admin and students."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user_type = request.form.get('user_type')  # 'admin' or 'student'
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        try:
            if user_type == 'admin':
                # Admin login
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    session['user_type'] = 'admin'
                    session['username'] = username
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid credentials. Please try again.', 'error')
            
            elif user_type == 'student':
                # Student login with retry logic
                max_retries = 3
                student = None
                
                for attempt in range(max_retries):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM students WHERE matric_no = ?', (username,))
                        student = cursor.fetchone()
                        conn.close()
                        break  # Successfully retrieved
                    except sqlite3.OperationalError:
                        if attempt < max_retries - 1:
                            continue  # Retry
                        else:
                            flash('Database is temporarily busy. Please try again in a moment.', 'error')
                            return render_template('login.html')
                
                if student and check_password_hash(student['password_hash'], password):
                    session['user_type'] = 'student'
                    session['student_id'] = student['id']
                    session['student_name'] = student['name']
                    session['matric_no'] = student['matric_no']
                    flash('Login successful!', 'success')
                    return redirect(url_for('student_results'))
                else:
                    flash('Invalid credentials. Please try again.', 'error')
        
        except Exception as e:
            flash(f'Login error. Please try again. Error: {str(e)[:50]}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clear session and logout user."""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# ==================== ADMIN ROUTES ====================

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Admin dashboard with statistics and visualizations."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    try:
        stats = calculate_statistics()
        risk_factors = get_risk_factor_counts()
    except sqlite3.OperationalError:
        flash('Database is temporarily busy. Please try again in a moment.', 'error')
        stats = {'total': 0, 'at_risk': 0, 'not_at_risk': 0}
        risk_factors = {'low_attendance': 0, 'low_ca': 0, 'low_exam': 0}
    except Exception as e:
        flash(f'Error loading dashboard. Please try again. Error: {str(e)[:50]}', 'error')
        stats = {'total': 0, 'at_risk': 0, 'not_at_risk': 0}
        risk_factors = {'low_attendance': 0, 'low_ca': 0, 'low_exam': 0}
    
    return render_template('dashboard.html', stats=stats, risk_factors=risk_factors)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    """Add new student to the system."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            matric_no = request.form.get('matric_no', '').strip()
            name = request.form.get('name', '').strip()
            department = request.form.get('department', '').strip()
            level = request.form.get('level', '').strip()
            password = request.form.get('password', '').strip()
            
            # Validate required fields
            if not all([matric_no, name, department, level, password]):
                flash('All fields are required. Please fill in all information.', 'error')
                return render_template('add_student.html')
            
            # Validate numeric fields
            try:
                attendance = float(request.form.get('attendance', 0))
                ca_score = float(request.form.get('ca_score', 0))
                exam_score = float(request.form.get('exam_score', 0))
            except ValueError:
                flash('Scores must be numeric values. Please enter valid numbers.', 'error')
                return render_template('add_student.html')
            
            # Validate score ranges
            if not (0 <= attendance <= 100 and 0 <= ca_score <= 100 and 0 <= exam_score <= 100):
                flash('All scores must be between 0 and 100.', 'error')
                return render_template('add_student.html')
            
            # Hash the password
            password_hash = generate_password_hash(password)
            
            # Try to add student with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO students (matric_no, name, department, level, attendance, ca_score, exam_score, password_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (matric_no, name, department, level, attendance, ca_score, exam_score, password_hash))
                    conn.commit()
                    conn.close()
                    
                    flash(f'Student {name} added successfully!', 'success')
                    return redirect(url_for('view_students'))
                
                except sqlite3.OperationalError as e:
                    conn.close()
                    if attempt < max_retries - 1:
                        continue  # Retry
                    else:
                        flash('Database is temporarily busy. Please try again in a moment.', 'error')
                        return render_template('add_student.html')
                
                except sqlite3.IntegrityError:
                    conn.close()
                    flash(f'A student with matric number {matric_no} already exists. Please use a different matric number.', 'error')
                    return render_template('add_student.html')
        
        except Exception as e:
            flash(f'An unexpected error occurred. Please try again. Error: {str(e)[:50]}', 'error')
            return render_template('add_student.html')
    
    return render_template('add_student.html')

@app.route('/view_students')
def view_students():
    """Display all students in the system."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students ORDER BY name')
        students = cursor.fetchall()
        conn.close()
    except sqlite3.OperationalError:
        flash('Database is temporarily busy. Please try again in a moment.', 'error')
        students = []
    except Exception as e:
        flash(f'Error loading students. Please try again. Error: {str(e)[:50]}', 'error')
        students = []
    
    return render_template('view_students.html', students=students)

@app.route('/predict_performance', methods=['GET', 'POST'])
def predict_performance():
    """Run prediction for selected student."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            student_id = int(request.form.get('student_id'))
            
            # Get student data
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
            student = cursor.fetchone()
            
            if not student:
                flash('Student not found.', 'error')
                conn.close()
            else:
                # Load model and make prediction
                try:
                    model = load_model()
                    features = [[student['attendance'], student['ca_score'], student['exam_score']]]
                    prediction = model.predict(features)[0]
                    
                    # Generate recommendations
                    recommendations = generate_recommendations(
                        student['attendance'], 
                        student['ca_score'], 
                        student['exam_score']
                    )
                    
                    # Store prediction in database with retry logic
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            cursor.execute('''
                                INSERT INTO predictions (student_id, risk_level, recommendation)
                                VALUES (?, ?, ?)
                            ''', (student_id, prediction, recommendations))
                            conn.commit()
                            conn.close()
                            
                            flash(f'Prediction completed for {student["name"]}!', 'success')
                            return redirect(url_for('prediction_result', prediction_id=cursor.lastrowid))
                        
                        except sqlite3.OperationalError:
                            if attempt < max_retries - 1:
                                continue  # Retry
                            else:
                                conn.close()
                                flash('Database is temporarily busy. Please try again in a moment.', 'error')
                                break
                
                except FileNotFoundError:
                    conn.close()
                    flash('Model file not found. Please run train_model.py first to train the model.', 'error')
                except Exception as e:
                    conn.close()
                    flash(f'Prediction error: {str(e)[:50]}. Please try again.', 'error')
        
        except ValueError:
            flash('Invalid student selection. Please select a valid student.', 'error')
        except Exception as e:
            flash(f'An unexpected error occurred. Please try again. Error: {str(e)[:50]}', 'error')
    
    # Get all students for dropdown
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, matric_no, name FROM students ORDER BY name')
        students = cursor.fetchall()
        conn.close()
    except sqlite3.OperationalError:
        flash('Cannot load students. Database is busy. Please try again.', 'error')
        students = []
    
    return render_template('predict_performance.html', students=students)

@app.route('/prediction_result/<int:prediction_id>')
def prediction_result(prediction_id):
    """Display specific prediction result."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, s.name, s.matric_no, s.attendance, s.ca_score, s.exam_score
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            WHERE p.id = ?
        ''', (prediction_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            flash('Prediction not found.', 'error')
            return redirect(url_for('prediction_history'))
    
    except sqlite3.OperationalError:
        flash('Database is temporarily busy. Please try again in a moment.', 'error')
        result = None
    except Exception as e:
        flash(f'Error loading prediction. Please try again. Error: {str(e)[:50]}', 'error')
        result = None
    
    return render_template('prediction_result.html', result=result)

@app.route('/prediction_history')
def prediction_history():
    """Display all prediction history."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, s.name, s.matric_no
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            ORDER BY p.prediction_date DESC
        ''')
        history = cursor.fetchall()
        conn.close()
    except sqlite3.OperationalError:
        flash('Database is temporarily busy. Please try again in a moment.', 'error')
        history = []
    except Exception as e:
        flash(f'Error loading prediction history. Please try again. Error: {str(e)[:50]}', 'error')
        history = []
    
    return render_template('prediction_history.html', history=history)

@app.route('/delete_prediction/<int:prediction_id>', methods=['POST'])
def delete_prediction(prediction_id):
    """Delete specific prediction record."""
    if session.get('user_type') != 'admin':
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Try to delete with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Verify prediction exists first
                cursor.execute('SELECT id FROM predictions WHERE id = ?', (prediction_id,))
                if not cursor.fetchone():
                    conn.close()
                    flash('Prediction not found.', 'error')
                    return redirect(url_for('prediction_history'))
                
                # Delete the prediction
                cursor.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
                conn.commit()
                conn.close()
                
                flash('Prediction deleted successfully!', 'success')
                return redirect(url_for('prediction_history'))
            
            except sqlite3.OperationalError:
                if attempt < max_retries - 1:
                    continue  # Retry
                else:
                    flash('Database is temporarily busy. Please try again in a moment.', 'error')
                    return redirect(url_for('prediction_history'))
    
    except Exception as e:
        flash(f'Error deleting prediction. Please try again. Error: {str(e)[:50]}', 'error')
        return redirect(url_for('prediction_history'))

# ==================== STUDENT ROUTES ====================

@app.route('/student/results')
def student_results():
    """Display student's own prediction results."""
    if session.get('user_type') != 'student':
        flash('Access denied. Student access required.', 'error')
        return redirect(url_for('login'))
    
    student_id = session.get('student_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, s.name, s.matric_no, s.attendance, s.ca_score, s.exam_score
            FROM predictions p
            JOIN students s ON p.student_id = s.id
            WHERE p.student_id = ?
            ORDER BY p.prediction_date DESC
            LIMIT 1
        ''', (student_id,))
        result = cursor.fetchone()
        conn.close()
    except sqlite3.OperationalError:
        flash('Database is temporarily busy. Please try again in a moment.', 'error')
        result = None
    except Exception as e:
        flash(f'Error loading results. Please try again. Error: {str(e)[:50]}', 'error')
        result = None
    
    return render_template('student_results.html', result=result)

# ==================== APPLICATION STARTUP ====================

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    
    # Verify sklearn is available
    try:
        import sklearn
        print("✓ sklearn available")
    except ImportError:
        print("ERROR: sklearn not installed!")
        print("Run: pip install scikit-learn")
        exit(1)
    
    print("=" * 60)
    print("Student Performance Prediction System")
    print("=" * 60)
    print("Access the application at: http://localhost:5001")
    print("\nDefault Admin Credentials:")
    print(f"  Username: {ADMIN_USERNAME}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print("=" * 60)
    
    # Run Flask development server
    app.run(debug=True, host='0.0.0.0', port=5001)
