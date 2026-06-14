# Requirements Document

## Introduction

The Student Performance Prediction system is a web-based machine learning application designed to predict student academic risk status and provide actionable recommendations. The system uses historical data (attendance percentage, continuous assessment scores, and exam scores) to train a Decision Tree Classifier model that identifies students who may be "At Risk" of poor academic performance.

The system consists of two distinct portals with role-based access:

**Admin Portal**: Provides full system access including dashboard statistics, student management (add students, view student list), prediction execution (admin selects student from database, system uses stored scores), and prediction history management.

**Student Portal**: Provides read-only access where students can log in using their matric number and password to view their own prediction results, risk level, and personalized recommendations. Students cannot run predictions themselves.

Students' performance data (attendance, CA scores, exam scores) are stored in the database by administrators. When predictions are run, the system fetches scores from the database rather than manual form entry, making it function like a real school system rather than a calculator. This is designed as a final year project demonstration with basic implementations suitable for academic presentation.

## Glossary

- **Web_Application**: The Flask-based web server that handles HTTP requests, serves pages, and processes form submissions
- **Admin_Portal**: Web interface accessible only to administrators with full system access
- **Student_Portal**: Web interface accessible to students with read-only access to their own data
- **Admin_User**: System user with full privileges including student management and prediction execution
- **Student_User**: System user with limited privileges to view only their own prediction results
- **Authentication_System**: Login mechanism verifying user credentials and establishing sessions
- **Students_Table**: Database table storing student records with credentials and performance data
- **Predictions_Table**: Database table storing prediction results linked to students via foreign key
- **ML_Model**: The trained DecisionTreeClassifier stored as model.pkl that predicts risk status
- **Training_Script**: The Python script (train_model.py) that generates sample data, trains the ML model, and saves model.pkl
- **Risk_Status**: Binary classification output indicating whether a student is "At Risk" or "Not At Risk"
- **Recommendation_Engine**: Rule-based logic system that generates suggestions based on performance thresholds
- **Dashboard**: Admin portal page displaying statistics and visualizations of prediction data
- **Dataset**: Collection of 200 sample records containing attendance, ca_score, exam_score, and result columns
- **Database**: SQLite database file storing students, predictions, and admin credential records
- **Bootstrap_UI**: Bootstrap 5 framework used for styling cards, tables, and responsive layout
- **At_Risk_Threshold**: Performance criteria where attendance < 60% OR ca_score < 50 OR exam_score < 50
- **Session_Management**: Flask session handling for maintaining authenticated user state

## Requirements

### Requirement 1: Web Application Setup

**User Story:** As a project demonstrator, I want a Flask web application with proper structure and dependencies, so that the system runs reliably and follows best practices.

#### Acceptance Criteria

1. THE Web_Application SHALL use Flask framework with Python
2. THE Web_Application SHALL use SQLite for database storage
3. THE Web_Application SHALL use Bootstrap 5 for user interface styling
4. THE Web_Application SHALL use Scikit-learn for machine learning functionality
5. THE Web_Application SHALL use Pandas for data manipulation
6. THE Web_Application SHALL organize code in modular structure with app/, models/, and utils/ folders
7. THE Web_Application SHALL include requirements.txt file listing all dependencies
8. THE Web_Application SHALL include README.md file with setup and execution instructions
9. THE Web_Application SHALL start successfully using "python app.py" command
10. THE Web_Application SHALL include code comments throughout implementation
11. THE Web_Application SHALL use Flask-Bcrypt or werkzeug.security for password hashing

### Requirement 2: Database Schema and Structure

**User Story:** As a system architect, I want a well-structured database schema with proper relationships, so that student data and predictions are stored reliably.

#### Acceptance Criteria

1. THE Database SHALL include a Students_Table with columns: id (INTEGER PRIMARY KEY), matric_no (TEXT UNIQUE), name (TEXT), department (TEXT), level (TEXT), attendance (REAL), ca_score (REAL), exam_score (REAL), password_hash (TEXT)
2. THE Database SHALL include a Predictions_Table with columns: id (INTEGER PRIMARY KEY), student_id (INTEGER FOREIGN KEY), risk_level (TEXT), recommendation (TEXT), prediction_date (DATETIME)
3. THE Predictions_Table SHALL link to Students_Table via student_id foreign key relationship
4. THE Database SHALL create tables automatically if they do not exist on application startup
5. THE Database SHALL use SQLite as the database engine
6. THE Students_Table matric_no column SHALL enforce uniqueness constraint
7. THE Predictions_Table student_id column SHALL reference Students_Table id column with proper foreign key constraint

### Requirement 3: Authentication System

**User Story:** As a system administrator, I want secure authentication for both admin and student users, so that access is properly controlled.

#### Acceptance Criteria

1. THE Authentication_System SHALL support two user roles: Admin_User and Student_User
2. THE Authentication_System SHALL provide login functionality accepting username and password
3. WHEN Admin_User logs in, THE Authentication_System SHALL verify credentials against hardcoded or configuration-stored admin credentials
4. WHEN Student_User logs in, THE Authentication_System SHALL verify matric_no and password against Students_Table records
5. THE Authentication_System SHALL hash student passwords before storing in database
6. THE Authentication_System SHALL create session after successful login
7. THE Authentication_System SHALL provide logout functionality to terminate sessions
8. THE Web_Application SHALL redirect unauthenticated users to login page when accessing protected routes
9. THE Authentication_System SHALL distinguish between admin and student sessions
10. WHEN invalid credentials are provided, THE Authentication_System SHALL display error message without revealing which credential component failed

### Requirement 4: Admin Portal - Student Management

**User Story:** As an administrator, I want to add and view student records, so that I can maintain the student database.

#### Acceptance Criteria

1. THE Admin_Portal SHALL provide "Add Student" functionality accessible only to Admin_User
2. THE Admin_Portal SHALL provide form accepting matric_no, name, department, level, attendance, ca_score, exam_score, and password
3. WHEN Admin_User submits add student form, THE Web_Application SHALL validate all required fields are completed
4. WHEN Admin_User submits add student form, THE Web_Application SHALL validate matric_no is unique
5. WHEN Admin_User submits add student form, THE Web_Application SHALL hash the password before storage
6. WHEN Admin_User submits add student form, THE Web_Application SHALL insert record into Students_Table
7. THE Admin_Portal SHALL provide "View Students" page displaying all student records in a table
8. THE Admin_Portal SHALL display matric_no, name, department, level, attendance, ca_score, and exam_score in the students table
9. THE Admin_Portal SHALL NOT display password_hash in the students table
10. THE Admin_Portal SHALL use Bootstrap 5 styling for forms and tables

### Requirement 5: Admin Portal - Prediction Execution

**User Story:** As an administrator, I want to run predictions by selecting students from the database, so that the system uses their stored performance data.

#### Acceptance Criteria

1. THE Admin_Portal SHALL provide "Predict Performance" functionality accessible only to Admin_User
2. THE Admin_Portal SHALL display dropdown or selection interface listing all students from Students_Table
3. WHEN Admin_User selects a student, THE Web_Application SHALL retrieve the student's attendance, ca_score, and exam_score from Students_Table
4. WHEN Admin_User initiates prediction, THE Web_Application SHALL load the ML_Model from model.pkl file
5. THE ML_Model SHALL predict Risk_Status using the student's stored performance data
6. THE Recommendation_Engine SHALL generate recommendations based on the student's performance thresholds
7. WHEN prediction completes, THE Web_Application SHALL store result in Predictions_Table with student_id foreign key reference
8. WHEN prediction completes, THE Web_Application SHALL display prediction result to Admin_User
9. IF model.pkl file does not exist, THEN THE Web_Application SHALL display error message instructing admin to run training script
10. THE Admin_Portal SHALL NOT require manual entry of student performance scores during prediction

### Requirement 6: Admin Portal - Dashboard and Statistics

**User Story:** As an administrator, I want to see statistics and visualizations on the dashboard, so that I can understand overall risk distribution.

#### Acceptance Criteria

1. THE Admin_Portal SHALL provide "Dashboard" page accessible only to Admin_User
2. THE Dashboard SHALL retrieve all records from Predictions_Table
3. THE Dashboard SHALL calculate total number of predictions
4. THE Dashboard SHALL calculate number of "At Risk" predictions
5. THE Dashboard SHALL calculate number of "Not At Risk" predictions
6. THE Dashboard SHALL display statistics using Bootstrap 5 card components
7. THE Dashboard SHALL display pie chart showing distribution of "At Risk" vs "Not At Risk" students
8. THE Dashboard SHALL display bar chart showing frequency of risk factors (low attendance, low CA score, low exam score)
9. THE Dashboard SHALL render charts using client-side JavaScript charting library
10. WHEN no predictions exist, THE Dashboard SHALL display zero values for all statistics

### Requirement 7: Admin Portal - Prediction History Management

**User Story:** As an administrator, I want to view and manage prediction history, so that I can track all predictions made in the system.

#### Acceptance Criteria

1. THE Admin_Portal SHALL provide "Prediction History" page accessible only to Admin_User
2. THE Admin_Portal SHALL retrieve all records from Predictions_Table with joined student information
3. THE Admin_Portal SHALL display prediction history in a Bootstrap 5 styled table
4. THE Admin_Portal SHALL display student name, matric_no, risk_level, recommendation, and prediction_date in the table
5. THE Admin_Portal SHALL sort records by prediction_date in descending order
6. THE Admin_Portal SHALL provide delete button for each prediction record
7. WHEN Admin_User clicks delete button, THE Web_Application SHALL remove the corresponding record from Predictions_Table
8. WHEN deletion completes, THE Web_Application SHALL redirect Admin_User back to Prediction History page
9. WHEN no predictions exist, THE Admin_Portal SHALL display message "No prediction history available"

### Requirement 8: Student Portal - Authentication and Access Control

**User Story:** As a student, I want to log in using my matric number and password, so that I can access my prediction results securely.

#### Acceptance Criteria

1. THE Student_Portal SHALL provide login page accepting matric_no and password
2. WHEN Student_User submits login form, THE Authentication_System SHALL query Students_Table for matching matric_no
3. WHEN Student_User submits login form, THE Authentication_System SHALL verify password against stored password_hash
4. WHEN credentials are valid, THE Authentication_System SHALL create student session
5. WHEN credentials are invalid, THE Authentication_System SHALL display error message and remain on login page
6. THE Student_Portal SHALL restrict access to only logged-in Student_User
7. THE Student_Portal SHALL prevent Student_User from accessing Admin_Portal routes
8. THE Student_Portal SHALL provide logout functionality
9. WHEN Student_User logs out, THE Authentication_System SHALL terminate session and redirect to login page

### Requirement 9: Student Portal - View Own Prediction Results

**User Story:** As a student, I want to view my own prediction results, so that I know my academic risk status.

#### Acceptance Criteria

1. THE Student_Portal SHALL provide page displaying the student's own prediction results
2. THE Student_Portal SHALL query Predictions_Table for records matching the logged-in student's student_id
3. THE Student_Portal SHALL display the student's risk_level prominently
4. THE Student_Portal SHALL display the student's risk_level using color-coded badge (red for "At Risk", green for "Not At Risk")
5. THE Student_Portal SHALL display the student's personalized recommendations
6. THE Student_Portal SHALL display prediction_date timestamp
7. WHEN no prediction exists for the student, THE Student_Portal SHALL display message "No prediction available yet"
8. THE Student_Portal SHALL use Bootstrap 5 styling for layout and components
9. THE Student_Portal SHALL NOT allow Student_User to view other students' prediction results
10. THE Student_Portal SHALL NOT provide prediction execution functionality to Student_User

### Requirement 10: Machine Learning Model Training

**User Story:** As a system administrator, I want to train a machine learning model using sample data, so that the system can make predictions.

#### Acceptance Criteria

1. THE Training_Script SHALL be named train_model.py
2. WHEN train_model.py is executed, THE Training_Script SHALL generate a Dataset with 200 sample records if dataset is missing
3. THE Dataset SHALL contain columns: attendance, ca_score, exam_score, result
4. THE Training_Script SHALL use DecisionTreeClassifier from scikit-learn library
5. THE Training_Script SHALL label records as "At Risk" when attendance < 60 OR ca_score < 50 OR exam_score < 50
6. THE Training_Script SHALL label records as "Not At Risk" when attendance >= 60 AND ca_score >= 50 AND exam_score >= 50
7. WHEN training completes, THE Training_Script SHALL save the trained model as model.pkl file
8. THE Training_Script SHALL execute successfully using "python train_model.py" command
9. THE Training_Script SHALL include code comments explaining the training process

### Requirement 11: Recommendation Engine

**User Story:** As a system component, I want to generate specific recommendations based on student performance thresholds, so that users receive actionable feedback.

#### Acceptance Criteria

1. WHEN attendance percentage is below 60, THE Recommendation_Engine SHALL generate recommendation "Improve attendance"
2. WHEN ca_score is below 50, THE Recommendation_Engine SHALL generate recommendation "Improve continuous assessment performance"
3. WHEN exam_score is below 50, THE Recommendation_Engine SHALL generate recommendation "Improve examination preparation"
4. THE Recommendation_Engine SHALL generate multiple recommendations when multiple thresholds are not met
5. WHEN all scores meet or exceed thresholds, THE Recommendation_Engine SHALL generate positive feedback message "Keep up the good work!"
6. THE Recommendation_Engine SHALL use simple rule-based logic without machine learning
7. THE Recommendation_Engine SHALL return recommendations as a list or comma-separated string

### Requirement 12: Navigation and User Interface

**User Story:** As a user, I want consistent navigation appropriate to my role, so that I can easily access the features available to me.

#### Acceptance Criteria

1. THE Admin_Portal SHALL provide navigation menu with links to Dashboard, Add Student, View Students, Predict Performance, and Prediction History
2. THE Student_Portal SHALL provide simplified navigation menu with links to My Results and Logout
3. THE Web_Application SHALL use Bootstrap 5 navbar component for navigation
4. THE Web_Application SHALL highlight the currently active page in navigation menu
5. THE Web_Application SHALL use responsive Bootstrap 5 layout that works on different screen sizes
6. THE Web_Application SHALL display different navigation menus based on user role (Admin_User vs Student_User)
7. THE Web_Application SHALL include logout link in navigation menu for authenticated users

### Requirement 13: Error Handling and User Feedback

**User Story:** As a user, I want clear feedback when errors occur, so that I know what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN form validation fails, THE Web_Application SHALL display error message indicating which fields are invalid
2. WHEN model.pkl cannot be loaded, THE Web_Application SHALL display error message with instructions to run training script
3. WHEN database operations fail, THE Web_Application SHALL display user-friendly error message
4. THE Web_Application SHALL use Bootstrap 5 alert components for displaying error messages
5. WHEN operations complete successfully, THE Web_Application SHALL display success confirmation message
6. THE Web_Application SHALL handle invalid numeric inputs gracefully without crashing
7. WHEN Student_User attempts to access Admin_Portal routes, THE Web_Application SHALL display access denied message
8. WHEN matric_no uniqueness constraint is violated during student creation, THE Web_Application SHALL display error message

### Requirement 14: Project Documentation

**User Story:** As a project evaluator, I want clear documentation explaining how to set up and run the application, so that I can easily test and evaluate the project.

#### Acceptance Criteria

1. THE README.md file SHALL include project title and description
2. THE README.md file SHALL include technology stack listing
3. THE README.md file SHALL include installation instructions for dependencies
4. THE README.md file SHALL include step-by-step instructions to run training script
5. THE README.md file SHALL include step-by-step instructions to run web application
6. THE README.md file SHALL include description of both Admin_Portal and Student_Portal features
7. THE README.md file SHALL include folder structure explanation
8. THE README.md file SHALL specify Python version compatibility
9. THE requirements.txt file SHALL list all Python dependencies with version numbers
10. THE README.md file SHALL include default admin credentials for initial login
11. THE README.md file SHALL include instructions for adding students and running predictions
