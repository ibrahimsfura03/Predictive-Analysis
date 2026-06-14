# Implementation Plan: Student Performance Prediction System

## Overview

This implementation plan breaks down the Student Performance Prediction system into discrete coding tasks. The system is a Flask-based web application with machine learning capabilities for predicting student academic risk status. Implementation follows a bottom-up approach: starting with core infrastructure (model training, database setup), then building the web application layer (routes, templates), and finally implementing advanced features (dashboard analytics, visualizations). Each task references specific requirements for traceability.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create root directory structure: `templates/`, `static/css/`, `static/js/`
  - Create `requirements.txt` file with Flask==2.3.0, scikit-learn==1.3.0, pandas==2.0.0
  - Create `README.md` with project description, setup instructions, and execution commands
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 13.1, 13.2, 13.3, 13.4, 13.5, 13.9_

- [ ] 2. Implement machine learning model training script
  - [-] 2.1 Create `train_model.py` with dataset generation function
    - Implement `generate_sample_data()` function to create 200 synthetic student records
    - Generate columns: attendance (0-100), ca_score (0-100), exam_score (0-100)
    - Apply labeling logic: "At Risk" when attendance < 60 OR ca_score < 50 OR exam_score < 50
    - Apply labeling logic: "Not At Risk" when attendance >= 60 AND ca_score >= 50 AND exam_score >= 50
    - Return pandas DataFrame with all columns including result labels
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6_

  - [ ]* 2.2 Write property test for At-Risk labeling correctness
    - **Property 2: At-Risk Labeling Correctness**
    - **Validates: Requirements 3.5**
    - Generate test cases where attendance < 60 OR ca_score < 50 OR exam_score < 50
    - Verify all such records are labeled "At Risk"

  - [ ]* 2.3 Write property test for Not-At-Risk labeling correctness
    - **Property 3: Not-At-Risk Labeling Correctness**
    - **Validates: Requirements 3.6**
    - Generate test cases where attendance >= 60 AND ca_score >= 50 AND exam_score >= 50
    - Verify all such records are labeled "Not At Risk"

  - [~] 2.4 Add model training and persistence functions to `train_model.py`
    - Implement `train_model()` function using DecisionTreeClassifier
    - Split dataset into 80% training and 20% testing using train_test_split
    - Train model on features: attendance, ca_score, exam_score
    - Implement `save_model()` function to serialize model as `model.pkl` using pickle
    - Add main execution block to generate data, train model, and save model
    - Include code comments explaining the training process
    - _Requirements: 3.1, 3.4, 3.7, 3.8, 3.9_

  - [ ]* 2.5 Write property test for prediction output validity
    - **Property 4: Prediction Output Validity**
    - **Validates: Requirements 4.3**
    - Generate various valid input features (attendance, ca_score, exam_score)
    - Verify model predictions return exactly "At Risk" or "Not At Risk" (no other values)

- [ ] 3. Implement database layer and operations
  - [-] 3.1 Create database module with initialization and schema
    - Create database initialization function `init_db()` that creates SQLite database file
    - Define `predictions` table schema with columns: id (PRIMARY KEY), student_name (TEXT), attendance (REAL), ca_score (REAL), exam_score (REAL), risk_status (TEXT), recommendations (TEXT), timestamp (DATETIME)
    - Add auto-creation logic to create tables if they don't exist
    - _Requirements: 1.2, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [~] 3.2 Implement database CRUD operations
    - Implement `insert_prediction()` function to store new prediction records
    - Implement `get_all_predictions()` function to retrieve all records ordered by timestamp DESC
    - Implement `get_prediction_by_id()` function to retrieve specific record
    - Implement `delete_prediction_by_id()` function to remove specific record
    - _Requirements: 6.1, 7.2, 8.2_

  - [ ]* 3.3 Write property test for database persistence round-trip
    - **Property 6: Database Persistence Round-Trip**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8**
    - Generate various prediction records with different field values
    - Store each record in database and retrieve it
    - Verify all field values are preserved exactly (no data loss or corruption)

  - [ ]* 3.4 Write property test for history retrieval completeness
    - **Property 7: History Retrieval Completeness**
    - **Validates: Requirements 7.2**
    - Insert N prediction records into database
    - Retrieve all records using `get_all_predictions()`
    - Verify exactly N records are returned with no omissions or duplicates

  - [ ]* 3.5 Write property test for deletion correctness
    - **Property 9: Deletion Correctness**
    - **Validates: Requirements 8.2**
    - Insert prediction records into database
    - Delete specific record by ID
    - Verify record is removed and cannot be retrieved afterward

- [ ] 4. Implement recommendation engine
  - [ ] 4.1 Create `generate_recommendations()` function with threshold logic
    - Implement rule-based logic: if attendance < 60, add "Improve attendance"
    - Implement rule-based logic: if ca_score < 50, add "Improve continuous assessment performance"
    - Implement rule-based logic: if exam_score < 50, add "Improve examination preparation"
    - Implement rule-based logic: if all thresholds met, add "Keep up the good work!"
    - Return list of recommendation strings
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [ ]* 4.2 Write property test for recommendation generation completeness
    - **Property 5: Recommendation Generation Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.6**
    - Generate test cases with various combinations of threshold violations
    - Verify recommendations match exactly: "Improve attendance" iff attendance < 60, "Improve continuous assessment performance" iff ca_score < 50, "Improve examination preparation" iff exam_score < 50
    - Verify positive feedback appears iff all thresholds are met

- [~] 5. Create base template and navigation structure
  - Create `templates/base.html` with Bootstrap 5 CDN links
  - Implement Bootstrap navbar with links to Dashboard, Predict Student, Prediction History
  - Add active page highlighting logic using Jinja2 conditionals
  - Implement responsive layout container for main content area
  - Add Flask flash message display area using Bootstrap alert components
  - _Requirements: 1.3, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

- [ ] 6. Implement Flask application core and prediction route
  - [~] 6.1 Create `app.py` with Flask initialization and helper functions
    - Initialize Flask app with secret key for session management
    - Implement `load_model()` function to load `model.pkl` using pickle
    - Implement `validate_form_data()` function to check required fields and numeric validity
    - Add database initialization call in app startup
    - _Requirements: 1.1, 4.1, 4.7, 12.1, 12.6_

  - [ ]* 6.2 Write property test for form validation completeness
    - **Property 1: Form Validation Completeness**
    - **Validates: Requirements 2.5**
    - Generate form submissions with various combinations of missing fields
    - Verify validation rejects submission and identifies all missing fields

  - [ ]* 6.3 Write property test for invalid numeric input handling
    - **Property 13: Invalid Numeric Input Handling**
    - **Validates: Requirements 12.6**
    - Submit form with non-numeric values in numeric fields
    - Verify application handles error gracefully without crashing and displays error message

  - [~] 6.4 Implement `/predict` route with GET and POST handling
    - GET request: render prediction form template
    - POST request: validate form data, extract student_name, attendance, ca_score, exam_score
    - POST request: load ML model, handle FileNotFoundError with error message
    - POST request: generate prediction using model.predict()
    - POST request: call `generate_recommendations()` to get recommendation list
    - POST request: store prediction in database using `insert_prediction()`
    - POST request: redirect to result page with prediction_id
    - Add error handling with flash messages for validation failures and model loading errors
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 4.4, 4.7, 5.5, 6.1, 12.1, 12.2, 12.3_

- [ ] 7. Create prediction form and result templates
  - [~] 7.1 Create `templates/predict.html` with Bootstrap form
    - Extend base template
    - Create form with fields: student_name (text), attendance (number 0-100), ca_score (number 0-100), exam_score (number 0-100)
    - Add HTML5 validation attributes: required, min, max, step
    - Style form using Bootstrap 5 form classes (form-control, mb-3)
    - Add submit button with Bootstrap btn-primary styling
    - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [~] 7.2 Create `templates/result.html` to display prediction results
    - Extend base template
    - Display student name prominently
    - Display risk status with Bootstrap badge (red for "At Risk", green for "Not At Risk")
    - Display list of recommendations using Bootstrap list group
    - Add link back to prediction form
    - _Requirements: 4.4, 4.5, 4.6, 5.5, 12.5_

- [ ] 8. Implement prediction history route and template
  - [~] 8.1 Create `/history` route to display prediction history
    - Retrieve all predictions using `get_all_predictions()`
    - Pass records to template sorted by timestamp DESC
    - Handle empty state (no predictions)
    - _Requirements: 7.1, 7.2, 7.9, 7.10_

  - [~] 8.2 Create `templates/history.html` with prediction table
    - Extend base template
    - Create Bootstrap striped table with columns: Student Name, Attendance %, CA Score, Exam Score, Risk Status, Recommendations, Timestamp, Actions
    - Add delete button for each row using Bootstrap btn-danger btn-sm styling
    - Each delete button submits POST form to `/delete/<id>`
    - Display "No prediction history available" message when table is empty
    - _Requirements: 1.3, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 8.1, 8.5_

  - [ ]* 8.3 Write property test for timestamp ordering correctness
    - **Property 8: Timestamp Ordering Correctness**
    - **Validates: Requirements 7.9**
    - Insert multiple prediction records with different timestamps
    - Retrieve history and verify records are ordered by timestamp descending (newest first)

- [~] 9. Implement delete functionality
  - Create `/delete/<int:prediction_id>` route accepting POST requests
  - Call `delete_prediction_by_id()` to remove record from database
  - Redirect to history page after deletion
  - Add error handling for database failures with flash messages
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 12.3_

- [~] 10. Checkpoint - Ensure core functionality works
  - Run `python train_model.py` to generate model.pkl
  - Start Flask application with `python app.py`
  - Test prediction form submission and result display
  - Test prediction history display and delete functionality
  - Ensure all tests pass, ask the user if questions arise

- [ ] 11. Implement dashboard analytics and statistics
  - [~] 11.1 Create dashboard calculation functions
    - Implement `calculate_statistics()` function to compute total, at_risk_count, not_at_risk_count
    - Implement `prepare_pie_chart_data()` function to format risk distribution data
    - Implement `prepare_bar_chart_data()` function to count risk factors (low attendance, low CA, low exam)
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 11.2 Write property test for statistics calculation accuracy
    - **Property 10: Statistics Calculation Accuracy**
    - **Validates: Requirements 9.3, 9.4, 9.5**
    - Create various sets of prediction records with different risk statuses
    - Calculate statistics and verify: total equals actual count, at-risk count is accurate, not-at-risk count is accurate, total equals sum of at-risk and not-at-risk

  - [ ]* 11.3 Write property test for risk factor counting accuracy
    - **Property 11: Risk Factor Counting Accuracy**
    - **Validates: Requirements 10.4, 10.5, 10.6**
    - Create prediction records with various performance metrics
    - Calculate bar chart data and verify counts match: low attendance (< 60), low CA score (< 50), low exam score (< 50)

  - [~] 11.4 Create `/` (dashboard) route with statistics and chart data
    - Retrieve all predictions from database
    - Call `calculate_statistics()` to get aggregate counts
    - Call `prepare_pie_chart_data()` and `prepare_bar_chart_data()` for visualizations
    - Pass all data to dashboard template
    - Handle empty state (no predictions)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.1, 10.2, 10.3, 10.7, 10.8_

- [ ] 12. Create dashboard template with visualizations
  - [~] 12.1 Create `templates/dashboard.html` with statistics cards
    - Extend base template
    - Create three Bootstrap card components displaying Total Predictions, At Risk count, Not At Risk count
    - Add canvas elements for pie chart and bar chart
    - Display "No data available. Make predictions to see statistics." when no predictions exist
    - _Requirements: 1.3, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.8_

  - [~] 12.2 Create `static/js/charts.js` with Chart.js initialization
    - Add Chart.js CDN link to base template
    - Implement pie chart rendering for risk status distribution
    - Implement bar chart rendering for risk factor frequencies
    - Pass data from Flask template to JavaScript using Jinja2 data attributes
    - Handle empty state (no charts when insufficient data)
    - _Requirements: 10.1, 10.2, 10.3, 10.7, 10.8_

- [~] 13. Implement `/result/<int:prediction_id>` route
  - Retrieve specific prediction record using `get_prediction_by_id()`
  - Pass record data to result template
  - Handle case where prediction_id does not exist (display error)
  - _Requirements: 4.5, 4.6_

- [~] 14. Add comprehensive error handling and user feedback
  - Add try-except blocks around model loading with FileNotFoundError handling
  - Add try-except blocks around database operations with sqlite3.Error handling
  - Implement form validation error messages for missing and invalid fields
  - Add success flash messages for completed predictions
  - Style all messages using Bootstrap alert components (alert-danger for errors, alert-success for success)
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [ ]* 15. Write integration tests for end-to-end workflows
  - Test complete prediction workflow: form submission → prediction → storage → result display
  - Test history workflow: multiple predictions → history display → deletion → updated history
  - Test dashboard workflow: predictions exist → statistics calculation → chart data preparation
  - Test error workflows: model missing, invalid form data, database errors

- [~] 16. Update README.md with comprehensive documentation
  - Add project title "Student Performance Prediction System"
  - Add technology stack section listing Flask, scikit-learn, pandas, Bootstrap 5, Chart.js
  - Add detailed installation instructions: pip install, train model, run app
  - Add feature description covering prediction, history, dashboard, visualizations
  - Add folder structure explanation with file descriptions
  - Specify Python 3.8+ version compatibility
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9_

- [~] 17. Final checkpoint - Complete system validation
  - Verify all routes are accessible and functional
  - Verify all templates render correctly with proper styling
  - Verify model training script works independently
  - Verify database operations persist correctly
  - Verify error handling displays appropriate messages
  - Test responsive layout on different screen sizes
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for complete traceability
- Property-based tests validate universal correctness properties from the design document
- Checkpoints ensure incremental validation at key milestones
- Implementation follows bottom-up approach: infrastructure first, then web layer, then advanced features
- All database operations use SQLite with auto-creation of tables
- All UI components use Bootstrap 5 for consistent styling
- Chart.js is loaded via CDN for dashboard visualizations
- Model persistence uses pickle format for simplicity
- Error handling covers model loading failures, form validation errors, and database errors

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1"]
    },
    {
      "id": 1,
      "tasks": ["2.1", "3.1", "4.1"]
    },
    {
      "id": 2,
      "tasks": ["2.2", "2.3", "3.2", "3.3", "4.2"]
    },
    {
      "id": 3,
      "tasks": ["2.4", "3.4", "3.5"]
    },
    {
      "id": 4,
      "tasks": ["2.5", "5"]
    },
    {
      "id": 5,
      "tasks": ["6.1", "11.1"]
    },
    {
      "id": 6,
      "tasks": ["6.2", "6.3", "11.2", "11.3"]
    },
    {
      "id": 7,
      "tasks": ["6.4", "7.1", "11.4"]
    },
    {
      "id": 8,
      "tasks": ["7.2", "8.1", "13"]
    },
    {
      "id": 9,
      "tasks": ["8.2", "9", "12.1"]
    },
    {
      "id": 10,
      "tasks": ["8.3", "12.2"]
    },
    {
      "id": 11,
      "tasks": ["14"]
    },
    {
      "id": 12,
      "tasks": ["15"]
    },
    {
      "id": 13,
      "tasks": ["16"]
    }
  ]
}
```
