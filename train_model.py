"""
Machine Learning Model Training Script
Generates synthetic student performance data and trains a Decision Tree Classifier
to predict student academic risk status.
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

def generate_sample_data(num_records=200):
    """
    Generate synthetic student performance dataset with 200 records.
    
    Returns:
        pandas DataFrame with columns: attendance, ca_score, exam_score, result
        
    Labeling Logic:
        - "At Risk": attendance < 60 OR ca_score < 50 OR exam_score < 50
        - "Not At Risk": attendance >= 60 AND ca_score >= 50 AND exam_score >= 50
    """
    np.random.seed(42)  # For reproducibility
    
    # Generate random performance data
    data = {
        'attendance': np.random.uniform(30, 100, num_records),
        'ca_score': np.random.uniform(20, 100, num_records),
        'exam_score': np.random.uniform(25, 100, num_records)
    }
    
    df = pd.DataFrame(data)
    
    # Apply labeling logic based on risk thresholds
    def label_risk(row):
        if row['attendance'] < 60 or row['ca_score'] < 50 or row['exam_score'] < 50:
            return 'At Risk'
        else:
            return 'Not At Risk'
    
    df['result'] = df.apply(label_risk, axis=1)
    
    print(f"Generated {num_records} student records")
    print(f"At Risk: {len(df[df['result'] == 'At Risk'])}")
    print(f"Not At Risk: {len(df[df['result'] == 'Not At Risk'])}")
    
    return df

def train_model(dataset):
    """
    Train DecisionTreeClassifier on student performance dataset.
    
    Args:
        dataset: pandas DataFrame with features and labels
        
    Returns:
        Trained sklearn DecisionTreeClassifier model
    """
    # Separate features (X) and labels (y)
    X = dataset[['attendance', 'ca_score', 'exam_score']]
    y = dataset['result']
    
    # Split dataset into training (80%) and testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Initialize and train Decision Tree Classifier
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model accuracy on test set
    accuracy = model.score(X_test, y_test)
    print(f"\nModel trained successfully!")
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    print(f"Model accuracy on test set: {accuracy * 100:.2f}%")
    
    return model

def save_model(model, filepath='model.pkl'):
    """
    Serialize trained model to disk using pickle.
    
    Args:
        model: Trained sklearn model object
        filepath: Path where model will be saved (default: model.pkl)
    """
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nModel saved as {filepath}")

if __name__ == '__main__':
    print("=" * 60)
    print("Student Performance Prediction - Model Training")
    print("=" * 60)
    
    # Step 1: Generate synthetic dataset
    print("\n[Step 1] Generating sample dataset...")
    data = generate_sample_data(200)
    
    # Step 2: Train the machine learning model
    print("\n[Step 2] Training Decision Tree Classifier...")
    model = train_model(data)
    
    # Step 3: Save the trained model
    print("\n[Step 3] Saving model to disk...")
    save_model(model)
    
    print("\n" + "=" * 60)
    print("Training complete! You can now run 'python app.py'")
    print("=" * 60)
