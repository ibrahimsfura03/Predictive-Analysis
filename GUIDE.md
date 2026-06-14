# Student Performance Prediction System - Setup Guide

## Quick Start (3 Steps)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
./run.sh  # Use this script to ensure correct Python environment
```

**OR simply run:**
```bash
./run.sh
```

Access: http://localhost:5001 | Login: admin / admin123

---

## Project Architecture

### Backend Engine
- **app.py** (500+ lines) - Flask application with routes, authentication, predictions, database operations
- **train_model.py** - Generates 200 synthetic records and trains Decision Tree Classifier (97.5% accuracy)

### Frontend (9 HTML Templates)
- **base.html** - Layout with LinkedIn blue sidebar, flat navigation
- **login.html** - Tab-based login (Admin/Student switching)
- **dashboard.html** - Admin dashboard with statistics and charts
- **add_student.html, view_students.html** - Student management
- **predict_performance.html, prediction_result.html** - ML predictions with visualizations
- **prediction_history.html, student_results.html** - Data views

### ML Module
- **model.pkl** - Trained Decision Tree model
- **train_model.py** - Training code

### Dataset
- **database.db** - SQLite with 2 tables: students, predictions (with foreign keys)

### Configuration
- **requirements.txt** - Dependencies (Flask 3.0.0, scikit-learn 1.5.2, pandas 2.2.0)

---

## Folder Structure

```
Predictive Analysis/
├── app.py                 # Flask engine - main application
├── train_model.py         # ML training module
├── model.pkl              # Trained ML model
├── database.db            # SQLite database
├── requirements.txt       # Python dependencies
│
├── templates/             # 9 HTML pages
│   ├── base.html         # Base layout (sidebar + styling)
│   ├── login.html        # Tab-based login
│   ├── dashboard.html    # Admin dashboard
│   └── ...
│
├── venv/                 # Python virtual environment
│
└── Utilities
    ├── view_database.py  # View data in terminal
    ├── export_data.py    # Export to CSV
    └── backup_database.sh # Backup database
```

---

## Installation Steps

### Just do this: './run.sh'

### 1. Check Python (3.8+)
```bash
python3 --version
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment
**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Train ML Model
```bash
python train_model.py
# Output: Accuracy: 97.5%, Model saved as model.pkl
```

### 6. Run Application
```bash
python app.py
# Output: Access at http://localhost:5001
```

---

## Running the Application

### Simple Method (Recommended)
```bash
./run.sh
```
This script automatically:
- Activates virtual environment
- Checks dependencies
- Verifies sklearn is installed
- Starts Flask on port 5001

### Manual Method
```bash
source venv/bin/activate  # Activate venv first!
python app.py
```

### Access Application
- URL: http://localhost:5001
- Admin Tab: username=`admin`, password=`admin123`
- Student Tab: matric number (existing student)

### Stop Server
Press `CTRL + C`

---

## Design Highlights

✅ **Professional LinkedIn Style**
- Solid LinkedIn blue (#0A66C2) - no gradients
- Flat design - no shadows, no rounded corners
- Font Awesome icons - no emojis
- Tab-based login for Admin/Student switching

✅ **Color Palette**
- Primary: #0A66C2 (LinkedIn Blue)
- Success: #0A8D5C (Green)
- Danger: #D93026 (Red)
- Background: #F5F5F5 (Gray)
- Text: #000000 (Black)

---

## Database Management

### View Database
```bash
python view_database.py
```

### Export to CSV
```bash
python export_data.py
# Creates: exports/students_[timestamp].csv, exports/predictions_[timestamp].csv
```

### Backup Database
```bash
./backup_database.sh
# Creates: backups/database_backup_[timestamp].db
```

---

## Features

### Admin Portal
- Dashboard with statistics
- Add students
- View all students
- Run ML predictions
- View prediction history
- Professional analytics with charts

### Student Portal
- View personal performance
- Risk level assessment
- AI-generated recommendations
- Performance visualizations

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Python not found | Use `python3` instead of `python` |
| Port 5001 in use | Kill process: `lsof -ti:5001 \| xargs kill -9` |
| Dependencies fail | Upgrade pip: `pip install --upgrade pip` |
| Model not found | Run: `python train_model.py` |
| Database error | Delete database.db and restart app |

---

## Deploy on Different Machine

1. Copy entire "Predictive Analysis" folder to USB/drive
2. On new machine:
```bash
cd "Predictive Analysis"
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

**Note:** database.db and model.pkl transfer automatically - no additional setup needed.

---

## Project Stats

- Code: ~500 lines (app.py)
- ML Training: ~200 lines (train_model.py)
- Templates: 9 HTML pages
- Accuracy: 97.5%
- Database: SQLite with foreign keys
- Design: LinkedIn professional (flat, no gradients)

---

## Key Talking Points for Defense

✓ "Professional LinkedIn-style flat design (no shadows/gradients)"
✓ "Decision Tree Classifier with 97.5% accuracy"
✓ "SQLite for portability and efficiency"
✓ "Role-based authentication (Admin/Student)"
✓ "Real-time ML predictions with visualizations"
✓ "Completely portable - works on any machine"

---

**Ready to demo?** Open http://localhost:5001 and start exploring! 🚀
