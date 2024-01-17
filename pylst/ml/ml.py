# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_regression_model(X_train, y_train, n_estimators=100):
    """
    Trains a Random Forest Regressor model.

    Parameters:
    - X_train: Training features
    - y_train: Training labels
    - n_estimators: Number of trees in the forest (default is 100)

    Returns:
    - Trained Random Forest Regressor model
    """
    # Initialize the Random Forest Regressor with the specified number of trees
    regressor = RandomForestRegressor(n_estimators=n_estimators)
    
    # Train the model using the training data
    regressor.fit(X_train, y_train)
    
    return regressor  # Return the trained model

def train_classification_model(X_train, y_train, n_estimators=100):
    """
    Trains a Random Forest Classifier model.

    Parameters:
    - X_train: Training features
    - y_train: Training labels
    - n_estimators: Number of trees in the forest (default is 100)

    Returns:
    - Trained Random Forest Classifier model
    """
    # Initialize the Random Forest Classifier with the specified number of trees
    classifier = RandomForestClassifier(n_estimators=n_estimators)
    
    # Train the classifier using the training data
    classifier.fit(X_train, y_train)
    
    return classifier  # Return the trained model

# Importing functions from sklearn for further use
# train_test_split: Function to split data into training and testing sets
# predict: Function to make predictions using RandomForestClassifier
# accuracy_score: Function to calculate the accuracy of classification models
train_test_split = train_test_split
predict = RandomForestClassifier().predict
accuracy_score = accuracy_score
