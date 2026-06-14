# Design Document: Student Performance Prediction System

## 1. System Overview

The Student Performance Prediction system is a Flask-based web application that uses machine learning to predict academic risk status for students. The system features dual portal architecture with role-based access control: an Admin Portal for system management and prediction execution, and a Student Portal for viewing personal prediction results. The system follows a three-tier architecture pattern with clear separation between presentation, business logic, and data persistence.

### 1.1 Architecture Style

**Monolithic Web Application** with layered architecture and role-based access control:
- **Presentation Layer**: Dual portal interface (Admin + Student) using Flask routes and Jinja2 templates with Bootstrap 5 styling
- **Authentication Layer**: Session-based authentication with role differentiation (admin vs student)
- **Business Logic Layer**: ML model integration, recommendation engine, data validation, access control
- **Data Access Layer**: SQLite database operations for student records and prediction history
- **ML Training Module**: Standalone script for model training and persistence

### 1.2 Core Components

1. **Flask Web Server** (`app.py`): HTTP request handling, routing, response rendering, and session management
2. **Authentication System**: User authentication, session management, role-based access control
3. **Admin Portal**: Full-access interface for student management, prediction execution, dashboard, and history
4. **Student Portal**: Read-only interface for students to view their own prediction results
5. **ML Training Script** (`train_model.py`): Dataset generation, model training, and serialization
6. **Prediction Engine**: Loads trained model and generates risk predictions using database-stored scores
7. **Recommendation Engine**: Rule-based logic for generating actionable feedback
8. **Database Manager**: SQLite operations for students table and predictions table with foreign key relationships
9. **Dashboard Analytics**: Statistics calculation and data preparation for visualizations

### 1.3 Technology Stack

- **Backend**: Python 3.8+ with Flask web framework
- **Authentication**: Flask sessions with werkzeug.security or Flask-Bcrypt for password hashing
- **Database**: SQLite (file-based, zero-configuration)
- **ML Library**: Scikit-learn (DecisionTreeClassifier)
- **Data Processing**: Pandas for dataset manipulation
- **Frontend**: Bootstrap 5 for responsive UI, Chart.js for visualizations
- **Model Persistence**: Pickle format for serialized ML model

### 1.4 User Roles and Access Control

**Admin User**:
- Full system access including all management and configuration features
- Can add students with credentials and performance data
- Can view all student records
- Can execute predictions by selecting students from database
- Can view dashboard with system-wide statistics
- Can view and manage prediction history
- Credentials: Hardcoded or configuration-stored

**Student User**:
- Read-only access to own data
- Can log in using matric_no and password
- Can view own prediction results, risk level, and recommendations
- Cannot run predictions
- Cannot view other students' data
- Cannot access admin functionality
- Credentials: Stored in students table

## 2. Component Design

### 2.1 Authentication System

**Responsibility**: Manage user authentication, session creation/termination, and role-based access control

**Key Functions**:

```python
def hash_password(password):
    """
    Hash password using werkzeug.security or bcrypt.
    Args: password (str)
    Returns: password_hash (str)
    """
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """
    Verify password against stored hash.
    Args: password_hash (str), password (str)
    Returns: bool
    """
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)

def login_admin(username, password):
    """
    Authenticate admin user against hardcoded/config credentials.
    Args: username (str), password (str)
    Returns: (success: bool, error_message: str)
    
    On success: Creates session with role='admin'
    On failure: Returns generic error message
    """
    # Check hardcoded admin credentials
    ADMIN_USERNAME = 'admin'  # Could be loaded from config
    ADMIN_PASSWORD = 'admin123'  # Could be loaded from config
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['role'] = 'admin'
        session['username'] = username
        return (True, None)
    else:
        return (False, "Invalid credentials. Please try again.")

def login_student(matric_no, password):
    """
    Authenticate student user against database records.
    Args: matric_no (str), password (str)
    Returns: (success: bool, student_id: int, error_message: str)
    
    On success: Creates session with role='student' and student_id
    On failure: Returns generic error message without revealing which part failed
    """
    # Query database for student record
    student = db_get_student_by_matric_no(matric_no)
    
    if student and verify_password(student['password_hash'], password):
        session['logged_in'] = True
        session['role'] = 'student'
        session['student_id'] = student['id']
        session['matric_no'] = matric_no
        return (True, student['id'], None)
    else:
        # Generic error - don't reveal if username or password was wrong
        return (False, None, "Invalid credentials. Please try again.")

def logout():
    """
    Terminate current session (admin or student).
    Clears all session data.
    """
    session.clear()

def require_admin(func):
    """
    Decorator to protect admin-only routes.
    Redirects to login if not authenticated or not admin role.
    """
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('login_page'))
        return func(*args, **kwargs)
    return wrapper

def require_student(func):
    """
    Decorator to protect student-only routes.
    Redirects to login if not authenticated or not student role.
    """
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'student':
            flash('Access denied. Please log in as a student.', 'error')
            return redirect(url_for('student_login_page'))
        return func(*args, **kwargs)
    return wrapper
```

### 2.2 Flask Web Application (`app.py`)

**Responsibility**: Handle HTTP requests, orchestrate business logic, render responses

**Authentication Routes**:

```python
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin login page.
    GET: Display login form
    POST: Authenticate admin and create session
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        success, error = login_admin(username, password)
        if success:
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'error')
    return render_template('admin_login.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """
    Student login page.
    GET: Display login form
    POST: Authenticate student and create session
    """
    if request.method == 'POST':
        matric_no = request.form.get('matric_no')
        password = request.form.get('password')
        success, student_id, error = login_student(matric_no, password)
        if success:
            return redirect(url_for('student_results'))
        else:
            flash(error, 'error')
    return render_template('student_login.html')

@app.route('/logout')
def logout_route():
    """
    Logout for both admin and student.
    Terminates session and redirects to appropriate login page.
    """
    role = session.get('role')
    logout()
    if role == 'admin':
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('student_login'))
```

**Admin Portal Routes**:

```python
@app.route('/admin/dashboard')
@require_admin
def dashboard():
    """
    Admin dashboard with statistics and visualizations.
    Retrieves all prediction history, calculates aggregated statistics,
    prepares chart data for pie chart and bar chart.
    """
    predictions = get_all_predictions()
    stats = calculate_statistics(predictions)
    pie_data = prepare_pie_chart_data(predictions)
    bar_data = prepare_bar_chart_data(predictions)
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         pie_data=pie_data, 
                         bar_data=bar_data)

@app.route('/admin/students/add', methods=['GET', 'POST'])
@require_admin
def add_student():
    """
    Add new student to database.
    GET: Display add student form
    POST: Validate and insert student record with hashed password
    """
    if request.method == 'POST':
        matric_no = request.form.get('matric_no')
        name = request.form.get('name')
        department = request.form.get('department')
        level = request.form.get('level')
        attendance = float(request.form.get('attendance'))
        ca_score = float(request.form.get('ca_score'))
        exam_score = float(request.form.get('exam_score'))
        password = request.form.get('password')
        
        # Validate all fields present
        if not all([matric_no, name, department, level, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('add_student'))
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert into database
        try:
            insert_student(matric_no, name, department, level, 
                         attendance, ca_score, exam_score, password_hash)
            flash('Student added successfully.', 'success')
            return redirect(url_for('view_students'))
        except sqlite3.IntegrityError:
            flash('Matric number already exists.', 'error')
            return redirect(url_for('add_student'))
    
    return render_template('add_student.html')

@app.route('/admin/students/view')
@require_admin
def view_students():
    """
    Display all student records in table (excluding password_hash).
    """
    students = get_all_students()
    return render_template('view_students.html', students=students)

@app.route('/admin/predict', methods=['GET', 'POST'])
@require_admin
def predict():
    """
    Admin prediction execution by selecting student from database.
    GET: Display student selection dropdown
    POST: Retrieve student data from database, generate prediction, store result
    """
    if request.method == 'POST':
        student_id = int(request.form.get('student_id'))
        
        # Retrieve student data from database
        student = get_student_by_id(student_id)
        if not student:
            flash('Student not found.', 'error')
            return redirect(url_for('predict'))
        
        # Extract features from database record
        attendance = student['attendance']
        ca_score = student['ca_score']
        exam_score = student['exam_score']
        
        # Load ML model
        try:
            model = load_model()
        except FileNotFoundError:
            flash('Model not found. Please run train_model.py first.', 'error')
            return redirect(url_for('predict'))
        
        # Generate prediction
        features = [[attendance, ca_score, exam_score]]
        risk_status = model.predict(features)[0]
        
        # Generate recommendations
        recommendations = generate_recommendations(attendance, ca_score, exam_score)
        recommendations_str = ', '.join(recommendations)
        
        # Store prediction in database
        prediction_id = insert_prediction(student_id, risk_status, recommendations_str)
        
        flash('Prediction completed successfully.', 'success')
        return redirect(url_for('prediction_result', prediction_id=prediction_id))
    
    # GET: Display student selection form
    students = get_all_students()
    return render_template('predict.html', students=students)

@app.route('/admin/prediction/<int:prediction_id>')
@require_admin
def prediction_result(prediction_id):
    """
    Display specific prediction result with student details.
    """
    prediction = get_prediction_with_student_by_id(prediction_id)
    if not prediction:
        flash('Prediction not found.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('prediction_result.html', prediction=prediction)

@app.route('/admin/history')
@require_admin
def history():
    """
    Display all prediction history with student information in descending chronological order.
    """
    predictions = get_all_predictions_with_students()
    return render_template('history.html', predictions=predictions)

@app.route('/admin/delete/<int:prediction_id>', methods=['POST'])
@require_admin
def delete(prediction_id):
    """
    Delete specific prediction record from database.
    """
    delete_prediction_by_id(prediction_id)
    flash('Prediction deleted successfully.', 'success')
    return redirect(url_for('history'))
```

**Student Portal Routes**:

```python
@app.route('/student/results')
@require_student
def student_results():
    """
    Display logged-in student's own prediction results.
    Retrieves predictions for current student only (data isolation).
    """
    student_id = session.get('student_id')
    
    # Get student's predictions (only their own)
    predictions = get_predictions_by_student_id(student_id)
    
    # Get student info
    student = get_student_by_id(student_id)
    
    return render_template('student_results.html', 
                         student=student, 
                         predictions=predictions)
```

**Key Functions**:

```python
def load_model():
    """
    Load trained ML model from model.pkl file.
    Returns: sklearn model object
    Raises: FileNotFoundError if model.pkl does not exist
    """
    import pickle
    with open('model.pkl', 'rb') as f:
        return pickle.load(f)

def validate_form_data(form_data):
    """
    Validate that all required fields are present and contain valid numeric values.
    Args: form_data dict with keys
    Returns: (is_valid: bool, errors: list)
    """
    pass

def generate_recommendations(attendance, ca_score, exam_score):
    """
    Generate list of recommendations based on threshold rules.
    Args: attendance (float), ca_score (float), exam_score (float)
    Returns: list of recommendation strings
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
    
    return recommendations
```

### 2.3 ML Training Script (`train_model.py`)

**Responsibility**: Handle HTTP requests, orchestrate business logic, render responses

**Routes**:

```python
@app.route('/')
def dashboard():
    """
    Display dashboard with statistics and visualizations.
    Retrieves all prediction history, calculates aggregated statistics,
    prepares chart data for pie chart and bar chart.
    """
    pass

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    GET: Display prediction form
    POST: Process form submission, generate prediction, store result, redirect to result page
    """
    pass

@app.route('/result/<int:prediction_id>')
def result(prediction_id):
    """
    Display prediction result with student details, risk status, and recommendations.
    Retrieves specific prediction record from database by ID.
    """
    pass

@app.route('/history')
def history():
    """
    Display all prediction history in descending chronological order.
    Retrieves all records from database sorted by timestamp DESC.
    """
    pass

@app.route('/delete/<int:prediction_id>', methods=['POST'])
def delete(prediction_id):
    """
    Delete specific prediction record from database.
    Redirects to history page after deletion.
    """
    pass
```

**Key Functions**:

```python
def load_model():
    """
    Load trained ML model from model.pkl file.
    Returns: sklearn model object
    Raises: FileNotFoundError if model.pkl does not exist
    """
    pass

def validate_form_data(form_data):
    """
    Validate that all required fields are present and contain valid numeric values.
    Args: form_data dict with keys: name, attendance, ca_score, exam_score
    Returns: (is_valid: bool, errors: list)
    """
    pass

def generate_recommendations(attendance, ca_score, exam_score):
    """
    Generate list of recommendations based on threshold rules.
    Args: attendance (float), ca_score (float), exam_score (float)
    Returns: list of recommendation strings
    """
    pass
```

### 2.2 ML Training Script (`train_model.py`)

**Responsibility**: Generate sample dataset, train ML model, persist model to disk

**Workflow**:

```python
def generate_sample_data(num_records=200):
    """
    Generate synthetic student performance dataset.
    
    Returns: pandas DataFrame with columns:
    - attendance: float (0-100)
    - ca_score: float (0-100)
    - exam_score: float (0-100)
    - result: string ('At Risk' or 'Not At Risk')
    
    Labeling logic:
    - 'At Risk': attendance < 60 OR ca_score < 50 OR exam_score < 50
    - 'Not At Risk': attendance >= 60 AND ca_score >= 50 AND exam_score >= 50
    """
    pass

def train_model(dataset):
    """
    Train DecisionTreeClassifier on dataset.
    
    Args: pandas DataFrame with features and labels
    Returns: trained sklearn model
    """
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import train_test_split
    
    # Separate features (X) and labels (y)
    X = dataset[['attendance', 'ca_score', 'exam_score']]
    y = dataset['result']
    
    # Split dataset (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train DecisionTreeClassifier
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    return model

def save_model(model, filepath='model.pkl'):
    """
    Serialize trained model to disk using pickle.
    Args: model object, filepath string
    """
    import pickle
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)

if __name__ == '__main__':
    # Generate dataset
    data = generate_sample_data(200)
    
    # Train model
    model = train_model(data)
    
    # Save model
    save_model(model)
    print("Model trained and saved as model.pkl")
```

### 2.4 Database Schema

**Table: students**

```sql
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
);
```

**Table: predictions**

```sql
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    recommendation TEXT,
    prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
);
```

**Database Operations**:

```python
def init_db():
    """
    Initialize database and create tables if they don't exist.
    Called on application startup.
    """
    conn = sqlite3.connect('database.db')
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
    
    # Create predictions table with foreign key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            recommendation TEXT,
            prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_student(matric_no, name, department, level, attendance, ca_score, exam_score, password_hash):
    """
    Insert new student record into database.
    Args: all student fields including password_hash
    Returns: student_id (int)
    Raises: sqlite3.IntegrityError if matric_no already exists
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (matric_no, name, department, level, attendance, ca_score, exam_score, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (matric_no, name, department, level, attendance, ca_score, exam_score, password_hash))
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return student_id

def get_all_students():
    """
    Retrieve all student records (excluding password_hash for security).
    Returns: list of dict records
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, matric_no, name, department, level, attendance, ca_score, exam_score FROM students')
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_by_id(student_id):
    """
    Retrieve specific student record by ID.
    Args: student_id (int)
    Returns: dict record or None
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = cursor.fetchone()
    conn.close()
    return dict(student) if student else None

def get_student_by_matric_no(matric_no):
    """
    Retrieve specific student record by matric number (for authentication).
    Args: matric_no (str)
    Returns: dict record or None
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE matric_no = ?', (matric_no,))
    student = cursor.fetchone()
    conn.close()
    return dict(student) if student else None

def insert_prediction(student_id, risk_level, recommendation):
    """
    Insert new prediction record into database with foreign key reference.
    Args: student_id (int), risk_level (str), recommendation (str)
    Returns: prediction_id (int)
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (student_id, risk_level, recommendation)
        VALUES (?, ?, ?)
    ''', (student_id, risk_level, recommendation))
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prediction_id

def get_all_predictions():
    """
    Retrieve all prediction records ordered by prediction_date DESC.
    Returns: list of dict records
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY prediction_date DESC')
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return predictions

def get_all_predictions_with_students():
    """
    Retrieve all prediction records with joined student information.
    Returns: list of dict records with student details
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
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

def get_prediction_with_student_by_id(prediction_id):
    """
    Retrieve specific prediction record with joined student information.
    Args: prediction_id (int)
    Returns: dict record or None
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
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

def get_predictions_by_student_id(student_id):
    """
    Retrieve all prediction records for a specific student (data isolation).
    Args: student_id (int)
    Returns: list of dict records
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE student_id = ? ORDER BY prediction_date DESC', 
                   (student_id,))
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return predictions

def delete_prediction_by_id(prediction_id):
    """
    Delete specific prediction record from database.
    Args: prediction_id (int)
    Returns: bool success status
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
```

### 2.5 Recommendation Engine

**Logic**: Rule-based threshold evaluation

```python
def generate_recommendations(attendance, ca_score, exam_score):
    """
    Generate actionable recommendations based on performance thresholds.
    
    Threshold Rules:
    - attendance < 60: "Improve attendance"
    - ca_score < 50: "Improve continuous assessment performance"
    - exam_score < 50: "Improve examination preparation"
    - All thresholds met: "Keep up the good work!"
    
    Args:
        attendance (float): Attendance percentage (0-100)
        ca_score (float): Continuous assessment score (0-100)
        exam_score (float): Exam score (0-100)
    
    Returns:
        list: List of recommendation strings
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
    
    return recommendations
```

### 2.6 Dashboard Analytics

**Statistics Calculations**:

```python
def calculate_statistics(predictions):
    """
    Calculate aggregate statistics from prediction history.
    
    Args: predictions (list of dict)
    Returns: dict with keys:
        - total_predictions: int
        - at_risk_count: int
        - not_at_risk_count: int
    """
    total = len(predictions)
    at_risk = sum(1 for p in predictions if p['risk_level'] == 'At Risk')
    not_at_risk = total - at_risk
    
    return {
        'total_predictions': total,
        'at_risk_count': at_risk,
        'not_at_risk_count': not_at_risk
    }

def prepare_pie_chart_data(predictions):
    """
    Prepare data for pie chart showing risk distribution.
    
    Args: predictions (list of dict)
    Returns: dict with keys:
        - labels: ['At Risk', 'Not At Risk']
        - values: [count_at_risk, count_not_at_risk]
    """
    at_risk = sum(1 for p in predictions if p['risk_level'] == 'At Risk')
    not_at_risk = len(predictions) - at_risk
    return {
        'labels': ['At Risk', 'Not At Risk'],
        'values': [at_risk, not_at_risk]
    }

def prepare_bar_chart_data(predictions):
    """
    Calculate frequency of each risk factor from predictions joined with student data.
    
    Args: predictions (list of dict with joined student data)
    Returns: dict with keys:
        - labels: ['Low Attendance', 'Low CA Score', 'Low Exam Score']
        - values: [count_attendance, count_ca, count_exam]
    
    Logic:
    - Low Attendance: attendance < 60
    - Low CA Score: ca_score < 50
    - Low Exam Score: exam_score < 50
    """
    low_attendance = sum(1 for p in predictions if p['attendance'] < 60)
    low_ca = sum(1 for p in predictions if p['ca_score'] < 50)
    low_exam = sum(1 for p in predictions if p['exam_score'] < 50)
    
    return {
        'labels': ['Low Attendance', 'Low CA Score', 'Low Exam Score'],
        'values': [low_attendance, low_ca, low_exam]
    }
```

## 3. User Interface Design

### 3.1 Layout Structure

**Admin Portal Layout**:
- **Navigation Bar**: Bootstrap navbar with links to Dashboard, Add Student, View Students, Predict Performance, Prediction History, Logout
- **Main Content Area**: Page-specific content in Bootstrap container
- **Active Page Highlighting**: Current page link highlighted in navigation
- **Role Badge**: Display "Admin" badge in navbar

**Student Portal Layout**:
- **Navigation Bar**: Simplified Bootstrap navbar with links to My Results, Logout
- **Main Content Area**: Page-specific content in Bootstrap container
- **Role Badge**: Display "Student: [Matric No]" in navbar

### 3.2 Page Designs

#### 3.2.1 Admin Login Page (`/admin/login`)

**Form**:
```html
<form method="POST">
    <div class="mb-3">
        <label>Username</label>
        <input type="text" name="username" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Login as Admin</button>
</form>
```

#### 3.2.2 Student Login Page (`/student/login`)

**Form**:
```html
<form method="POST">
    <div class="mb-3">
        <label>Matric Number</label>
        <input type="text" name="matric_no" class="form-control" required>
    </div>
    <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Login as Student</button>
</form>
<p class="mt-3">
    <a href="/admin/login">Login as Administrator instead</a>
</p>
```

#### 3.2.3 Admin Dashboard (`/admin/dashboard`)

**Layout**:
- **Statistics Cards**: Three Bootstrap cards displaying:
  - Total Predictions count
  - At Risk count
  - Not At Risk count
- **Pie Chart**: Visual distribution of risk status
- **Bar Chart**: Frequency of risk factors

**Empty State**: When no predictions exist, display message "No data available. Make predictions to see statistics."

#### 3.2.4 Add Student Form (`/admin/students/add`)

**Form Fields**:
```html
<form method="POST">
    <div class="mb-3">
        <label>Matric Number</label>
        <input type="text" name="matric_no" class="form-control" required>
    </div>
    
    <div class="mb-3">
        <label>Student Name</label>
        <input type="text" name="name" class="form-control" required>
    </div>
    
    <div class="mb-3">
        <label>Department</label>
        <input type="text" name="department" class="form-control" required>
    </div>
    
    <div class="mb-3">
        <label>Level</label>
        <input type="text" name="level" class="form-control" required>
    </div>
    
    <div class="mb-3">
        <label>Attendance Percentage (0-100)</label>
        <input type="number" name="attendance" class="form-control" 
               min="0" max="100" step="0.01" required>
    </div>
    
    <div class="mb-3">
        <label>CA Score (0-100)</label>
        <input type="number" name="ca_score" class="form-control" 
               min="0" max="100" step="0.01" required>
    </div>
    
    <div class="mb-3">
        <label>Exam Score (0-100)</label>
        <input type="number" name="exam_score" class="form-control" 
               min="0" max="100" step="0.01" required>
    </div>
    
    <div class="mb-3">
        <label>Password (for student login)</label>
        <input type="password" name="password" class="form-control" required>
    </div>
    
    <button type="submit" class="btn btn-primary">Add Student</button>
</form>
```

#### 3.2.5 View Students (`/admin/students/view`)

**Table Structure**:
```html
<table class="table table-striped">
    <thead>
        <tr>
            <th>Matric No</th>
            <th>Name</th>
            <th>Department</th>
            <th>Level</th>
            <th>Attendance %</th>
            <th>CA Score</th>
            <th>Exam Score</th>
        </tr>
    </thead>
    <tbody>
        <!-- Note: password_hash is excluded for security -->
        <tr>
            <td>{{ student.matric_no }}</td>
            <td>{{ student.name }}</td>
            <td>{{ student.department }}</td>
            <td>{{ student.level }}</td>
            <td>{{ student.attendance }}</td>
            <td>{{ student.ca_score }}</td>
            <td>{{ student.exam_score }}</td>
        </tr>
    </tbody>
</table>
```

#### 3.2.6 Prediction Form (`/admin/predict`)

**Form Fields**:
```html
<form method="POST">
    <div class="mb-3">
        <label>Select Student</label>
        <select name="student_id" class="form-control" required>
            <option value="">-- Select a student --</option>
            {% for student in students %}
            <option value="{{ student.id }}">
                {{ student.matric_no }} - {{ student.name }} 
                (Att: {{ student.attendance }}%, CA: {{ student.ca_score }}, Exam: {{ student.exam_score }})
            </option>
            {% endfor %}
        </select>
    </div>
    
    <button type="submit" class="btn btn-primary">Run Prediction</button>
</form>
```

**Note**: Scores are fetched from database, not manually entered

#### 3.2.7 Prediction Result (`/admin/prediction/<id>`)

**Content**:
- Student Name and Matric No display
- Risk Status badge (red for "At Risk", green for "Not At Risk")
- List of recommendations
- Prediction date
- Link back to prediction form

#### 3.2.8 Prediction History (`/admin/history`)

**Table Structure**:
```html
<table class="table table-striped">
    <thead>
        <tr>
            <th>Matric No</th>
            <th>Student Name</th>
            <th>Department</th>
            <th>Attendance %</th>
            <th>CA Score</th>
            <th>Exam Score</th>
            <th>Risk Level</th>
            <th>Recommendations</th>
            <th>Date</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>{{ record.matric_no }}</td>
            <td>{{ record.name }}</td>
            <td>{{ record.department }}</td>
            <td>{{ record.attendance }}</td>
            <td>{{ record.ca_score }}</td>
            <td>{{ record.exam_score }}</td>
            <td>{{ record.risk_level }}</td>
            <td>{{ record.recommendation }}</td>
            <td>{{ record.prediction_date }}</td>
            <td>
                <form method="POST" action="/admin/delete/{{ record.id }}">
                    <button type="submit" class="btn btn-danger btn-sm">Delete</button>
                </form>
            </td>
        </tr>
    </tbody>
</table>
```

**Empty State**: Display "No prediction history available" when table is empty

#### 3.2.9 Student Results Page (`/student/results`)

**Content**:
- Welcome message with student name
- Student information card (matric no, department, level)
- Student's performance data (attendance, CA score, exam score)
- Risk Level display with color-coded badge
- Personalized recommendations list
- Prediction date

**Empty State**: When no prediction exists, display "No prediction available yet. Please contact your administrator."

**Security Note**: Student can only see their own data, enforced by session student_id

## 4. Data Flow

### 4.1 Authentication Workflows

#### 4.1.1 Admin Login Flow

```
1. Admin visits /admin/login
2. Admin enters username and password
3. Server validates against hardcoded/config credentials
4. If valid:
   a. Create session with role='admin'
   b. Redirect to admin dashboard
5. If invalid:
   a. Display generic error message
   b. Remain on login page
```

#### 4.1.2 Student Login Flow

```
1. Student visits /student/login
2. Student enters matric_no and password
3. Server queries students table for matric_no
4. Server verifies password against stored hash
5. If valid:
   a. Create session with role='student' and student_id
   b. Redirect to student results page
6. If invalid:
   a. Display generic error message (don't reveal which part failed)
   b. Remain on login page
```

#### 4.1.3 Logout Flow

```
1. User clicks logout link
2. Server clears session data
3. Redirect to appropriate login page based on previous role
```

### 4.2 Admin Portal Workflows

#### 4.2.1 Add Student Workflow

```
1. Admin navigates to Add Student page (protected by @require_admin)
2. Admin fills form with student details and password
3. Form submitted (POST /admin/students/add)
4. Server validates all required fields present
5. Server hashes password
6. Server attempts to insert into students table
7. If matric_no is unique:
   a. Record inserted successfully
   b. Flash success message
   c. Redirect to View Students page
8. If matric_no already exists:
   a. Database raises IntegrityError
   b. Flash error message
   c. Redirect back to Add Student form
```

#### 4.2.2 Prediction Workflow (Database-Driven)

```
1. Admin navigates to Predict Performance page (protected by @require_admin)
2. Server loads all students and displays in dropdown
3. Admin selects a student from dropdown
4. Form submitted (POST /admin/predict)
5. Server retrieves student record by student_id
6. Server extracts attendance, ca_score, exam_score from database record
7. Server loads ML model from model.pkl
8. If model not found:
   a. Flash error message with instructions
   b. Redirect back to prediction form
9. If model loaded:
   a. Generate prediction using database scores
   b. Generate recommendations based on thresholds
   c. Store prediction in predictions table with student_id foreign key
   d. Flash success message
   e. Redirect to prediction result page
```

#### 4.2.3 Dashboard Data Flow

```
1. Admin navigates to dashboard (protected by @require_admin)
2. Server retrieves all predictions with joined student data
3. Calculate statistics: total, at_risk_count, not_at_risk_count
4. Prepare pie chart data: risk distribution
5. Prepare bar chart data: risk factor frequencies (from joined student data)
6. Render dashboard template with data
7. Client-side JavaScript renders charts using Chart.js
```

#### 4.2.4 History Management Flow

```
1. Admin visits history page (protected by @require_admin)
2. Server retrieves all predictions with joined student information
3. Server sorts by prediction_date DESC
4. Render table with all records

DELETE FLOW:
1. Admin clicks delete button on specific record
2. Form submitted (POST /admin/delete/<id>)
3. Server deletes record from predictions table
4. Flash success message
5. Redirect to history page (GET /admin/history)
6. Updated history displayed
```

### 4.3 Student Portal Workflows

#### 4.3.1 View Own Results Workflow

```
1. Student navigates to results page (protected by @require_student)
2. Server extracts student_id from session
3. Server queries predictions table WHERE student_id = session['student_id']
4. Server retrieves student information
5. Render results page with:
   a. Student information
   b. Own prediction results only (data isolation)
   c. Risk level with color-coded badge
   d. Personalized recommendations
6. If no prediction exists:
   a. Display "No prediction available yet" message
```

### 4.5 Prediction Workflow

```
1. User fills prediction form
2. Form submitted (POST /predict)
3. Server validates form data
4. If invalid: Display error messages, re-render form
5. If valid:
   a. Extract features: attendance, ca_score, exam_score
   b. Load ML model from model.pkl
   c. Generate prediction: model.predict([[attendance, ca_score, exam_score]])
   d. Generate recommendations based on thresholds
   e. Store prediction in database
   f. Redirect to result page with prediction_id
6. Result page displays risk status and recommendations
```

### 4.2 Dashboard Data Flow

```
1. User visits dashboard (GET /)
2. Server retrieves all predictions from database
3. Calculate statistics: total, at_risk_count, not_at_risk_count
4. Prepare pie chart data: risk distribution
5. Prepare bar chart data: risk factor frequencies
6. Render dashboard template with data
7. Client-side JavaScript renders charts using Chart.js
```

### 4.3 History Management Flow

```
1. User visits history page (GET /history)
2. Server retrieves all predictions ordered by timestamp DESC
3. Render table with all records

DELETE FLOW:
1. User clicks delete button on specific record
2. Form submitted (POST /delete/<id>)
3. Server deletes record from database
4. Redirect to history page (GET /history)
5. Updated history displayed
```

## 5. Error Handling

### 5.1 Authentication Errors

**Scenario**: Invalid credentials (admin or student)

**Handling**:
```python
# Generic error message - don't reveal which part failed
flash('Invalid credentials. Please try again.', 'error')
return redirect(url_for('login_page'))
```

**Scenario**: Unauthenticated access to protected routes

**Handling**:
```python
@require_admin or @require_student decorators:
if not authenticated:
    flash('Please log in to access this page.', 'error')
    return redirect(url_for('login_page'))
```

**Scenario**: Role mismatch (student trying to access admin routes)

**Handling**:
```python
if session.get('role') != 'admin':
    flash('Access denied. Admin privileges required.', 'error')
    return redirect(url_for('student_login'))
```

### 5.2 Model Loading Errors

**Scenario**: `model.pkl` file does not exist

**Handling**:
```python
try:
    model = load_model()
except FileNotFoundError:
    flash('Model not found. Please run train_model.py first.', 'error')
    return redirect(url_for('predict'))
```

### 5.3 Form Validation Errors

**Invalid Input Types**: Non-numeric values for numeric fields

**Handling**:
```python
try:
    attendance = float(request.form['attendance'])
    ca_score = float(request.form['ca_score'])
    exam_score = float(request.form['exam_score'])
except ValueError:
    flash('Please enter valid numeric values for all score fields.', 'error')
    return redirect(url_for('predict'))
```

**Missing Required Fields**: Empty form submissions

**Handling**:
```python
if not all([student_name, attendance, ca_score, exam_score]):
    flash('All fields are required.', 'error')
    return redirect(url_for('predict'))
```

### 5.4 Database Errors

**Connection Failures**: SQLite file access issues

**Handling**:
```python
try:
    # database operation
    pass
except sqlite3.Error as e:
    flash('Database error occurred. Please try again.', 'error')
    return redirect(url_for('dashboard'))
```

## 6. File Structure

```
project_root/
│
├── app.py                      # Flask application entry point
├── train_model.py              # ML model training script
├── model.pkl                   # Trained model (generated by train_model.py)
├── database.db                 # SQLite database (auto-created)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template with navigation
│   ├── dashboard.html         # Dashboard page
│   ├── predict.html           # Prediction form page
│   ├── result.html            # Prediction result page
│   └── history.html           # Prediction history page
│
└── static/                     # Static assets
    ├── css/
    │   └── style.css          # Custom CSS (optional)
    └── js/
        └── charts.js          # Chart.js initialization
```

## 7. Dependencies

**requirements.txt**:
```
Flask==2.3.0
scikit-learn==1.3.0
pandas==2.0.0
```

**Note**: Bootstrap 5 and Chart.js loaded via CDN in templates

## 8. Deployment Instructions

### 8.1 Initial Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train ML model
python train_model.py

# 3. Start Flask application
python app.py

# 4. Access application
# Navigate to http://localhost:5000 in browser
```

### 8.2 Development Mode

```python
# app.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 9. Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Form Validation Completeness

*For any* form submission with one or more missing required fields (student_name, attendance, ca_score, exam_score), the validation SHALL reject the submission and identify all missing fields.

**Validates: Requirements 2.5**

### Property 2: At-Risk Labeling Correctness

*For any* student record where attendance < 60 OR ca_score < 50 OR exam_score < 50, the training script SHALL label the record as "At Risk".

**Validates: Requirements 3.5**

### Property 3: Not-At-Risk Labeling Correctness

*For any* student record where attendance >= 60 AND ca_score >= 50 AND exam_score >= 50, the training script SHALL label the record as "Not At Risk".

**Validates: Requirements 3.6**

### Property 4: Prediction Output Validity

*For any* valid input features (attendance, ca_score, exam_score), the ML model prediction SHALL produce exactly one of two values: "At Risk" or "Not At Risk".

**Validates: Requirements 4.3**

### Property 5: Recommendation Generation Completeness

*For any* student performance input (attendance, ca_score, exam_score), the recommendation engine SHALL generate exactly the recommendations corresponding to threshold violations:
- "Improve attendance" if and only if attendance < 60
- "Improve continuous assessment performance" if and only if ca_score < 50
- "Improve examination preparation" if and only if exam_score < 50
- Positive feedback message if and only if all thresholds are met

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.6**

### Property 6: Database Persistence Round-Trip

*For any* prediction record (student_name, attendance, ca_score, exam_score, risk_status, recommendations, timestamp), storing the record in the database and then retrieving it SHALL preserve all field values exactly.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8**

### Property 7: History Retrieval Completeness

*For any* set of N prediction records stored in the database, retrieving the prediction history SHALL return exactly N records with no omissions or duplicates.

**Validates: Requirements 7.2**

### Property 8: Timestamp Ordering Correctness

*For any* set of prediction records with different timestamps, the history display SHALL order records in descending chronological order (newest first).

**Validates: Requirements 7.9**

### Property 9: Deletion Correctness

*For any* valid prediction record ID, executing the delete operation SHALL remove exactly that record from the database, and subsequent retrieval operations SHALL not return the deleted record.

**Validates: Requirements 8.2**

### Property 10: Statistics Calculation Accuracy

*For any* set of prediction records in the database, the dashboard statistics SHALL accurately calculate:
- Total predictions count equals the actual number of records
- At-risk count equals the number of records with risk_status = "At Risk"
- Not-at-risk count equals the number of records with risk_status = "Not At Risk"
- Total equals at-risk count plus not-at-risk count

**Validates: Requirements 9.3, 9.4, 9.5**

### Property 11: Risk Factor Counting Accuracy

*For any* set of prediction records in the database, the dashboard SHALL accurately count risk factors:
- Low attendance count equals records where attendance < 60
- Low CA score count equals records where ca_score < 50
- Low exam score count equals records where exam_score < 50

**Validates: Requirements 10.4, 10.5, 10.6**

### Property 12: Validation Error Messaging

*For any* form submission that fails validation due to invalid field values, the application SHALL display an error message that clearly indicates which specific fields are invalid.

**Validates: Requirements 12.1**

### Property 13: Invalid Numeric Input Handling

*For any* form submission containing non-numeric values in numeric fields (attendance, ca_score, exam_score), the application SHALL handle the error gracefully without crashing and display an appropriate error message.

**Validates: Requirements 12.6**

