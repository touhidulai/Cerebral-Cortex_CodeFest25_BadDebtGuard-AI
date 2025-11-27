"""
XGBoost Loan Risk Predictor
Trains on historical loan data and predicts loan approval risk
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, classification_report
import pickle
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "loan-data.csv"
MODEL_PATH = BASE_DIR / "models" / "xgboost_loan_model.pkl"
ENCODER_PATH = BASE_DIR / "models" / "label_encoders.pkl"

class XGBoostLoanPredictor:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.feature_columns = ['Income', 'Credit_Score', 'Loan_Amount', 'DTI_Ratio', 'Employment_Status']
        self.target_column = 'Approval'
        
    def load_data(self):
        """Load and preprocess the loan dataset"""
        print(f"Loading data from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH, encoding='latin-1')
        
        # Keep only essential columns
        columns_to_keep = self.feature_columns + [self.target_column]
        df = df[columns_to_keep]
        
        # Handle missing values
        df = df.dropna()
        
        print(f"Loaded {len(df)} records")
        print(f"Approval distribution:\n{df['Approval'].value_counts()}")
        
        return df
    
    def preprocess_data(self, df, fit=True):
        """Encode categorical variables"""
        df = df.copy()
        
        # Encode Employment_Status
        if fit:
            self.label_encoders['Employment_Status'] = LabelEncoder()
            df['Employment_Status'] = self.label_encoders['Employment_Status'].fit_transform(df['Employment_Status'])
        else:
            df['Employment_Status'] = self.label_encoders['Employment_Status'].transform(df['Employment_Status'])
        
        # Encode target (Approval: Approved=1, Rejected=0)
        if self.target_column in df.columns:
            if fit:
                self.label_encoders['Approval'] = LabelEncoder()
                df[self.target_column] = self.label_encoders['Approval'].fit_transform(df[self.target_column])
            else:
                df[self.target_column] = self.label_encoders['Approval'].transform(df[self.target_column])
        
        return df
    
    def train_model(self, test_size=0.2, random_state=42):
        """Train the XGBoost model"""
        # Load data
        df = self.load_data()
        
        # Preprocess
        df = self.preprocess_data(df, fit=True)
        
        # Split features and target
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"\nTraining set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # XGBoost parameters optimized for banking/finance
        params = {
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,  # L1 regularization
            'reg_lambda': 1.0,  # L2 regularization
            'scale_pos_weight': 1,  # Adjust if classes imbalanced
            'random_state': random_state,
            'use_label_encoder': False
        }
        
        # Train model
        print("\nTraining XGBoost model...")
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        print("\n=== Model Performance ===")
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"AUC-ROC:   {auc:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                    target_names=['Rejected', 'Approved']))
        
        # Feature importance
        print("\n=== Feature Importance ===")
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print(feature_importance)
        
        # Save model
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'auc': auc
        }
    
    def save_model(self):
        """Save trained model and encoders"""
        os.makedirs(MODEL_PATH.parent, exist_ok=True)
        
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(ENCODER_PATH, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        
        print(f"\nModel saved to {MODEL_PATH}")
        print(f"Encoders saved to {ENCODER_PATH}")
    
    def load_model(self):
        """Load trained model and encoders"""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train the model first.")
        
        with open(MODEL_PATH, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(ENCODER_PATH, 'rb') as f:
            self.label_encoders = pickle.load(f)
        
        print("Model and encoders loaded successfully")
    
    def predict_risk(self, income, credit_score, loan_amount, dti_ratio, employment_status):
        """
        Predict loan approval risk for a single applicant
        
        Args:
            income: Annual income
            credit_score: Credit score (300-850)
            loan_amount: Requested loan amount
            dti_ratio: Debt-to-income ratio (%)
            employment_status: 'employed' or 'unemployed'
        
        Returns:
            dict with approval_probability, risk_score, and recommendation
        """
        if self.model is None:
            self.load_model()
        
        # Prepare input
        employment_encoded = self.label_encoders['Employment_Status'].transform([employment_status])[0]
        
        input_data = pd.DataFrame({
            'Income': [income],
            'Credit_Score': [credit_score],
            'Loan_Amount': [loan_amount],
            'DTI_Ratio': [dti_ratio],
            'Employment_Status': [employment_encoded]
        })
        
        # Predict
        approval_proba = self.model.predict_proba(input_data)[0][1]  # Probability of approval
        rejection_proba = 1 - approval_proba
        
        # Calculate risk score (0-100, where 100 is highest risk)
        risk_score = rejection_proba * 100
        
        # Recommendation
        if approval_proba >= 0.7:
            recommendation = "LOW RISK - Approve"
            risk_level = "LOW"
        elif approval_proba >= 0.5:
            recommendation = "MEDIUM RISK - Review Required"
            risk_level = "MEDIUM"
        else:
            recommendation = "HIGH RISK - Reject"
            risk_level = "HIGH"
        
        return {
            'approval_probability': round(approval_proba * 100, 2),
            'rejection_probability': round(rejection_proba * 100, 2),
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'model_confidence': round(max(approval_proba, rejection_proba) * 100, 2)
        }
    
    def predict_from_document_data(self, document_data):
        """
        Extract features from document analysis and predict risk
        
        Args:
            document_data: Dict containing extracted financial information
        
        Returns:
            XGBoost prediction results or None if insufficient data
        """
        # Extract features with proper key mapping
        monthly_income = document_data.get('monthly_income', 0)
        monthly_debt = document_data.get('monthly_debt', 0)
        loan_amount = document_data.get('loan_amount', 0)
        employment_years = document_data.get('employment_years', 0)
        
        # Calculate annual income (XGBoost was trained on annual)
        income = monthly_income * 12
        
        # Calculate DTI ratio if we have income
        if monthly_income > 0:
            dti_ratio = (monthly_debt / monthly_income) * 100
        else:
            dti_ratio = 0
        
        # Estimate credit score based on DTI (since we don't extract it from documents)
        # This is a rough approximation aligned with the training data
        if dti_ratio == 0:
            credit_score = 650  # Neutral default when no data
        elif dti_ratio <= 20:
            credit_score = 750  # Excellent
        elif dti_ratio <= 35:
            credit_score = 700  # Good
        elif dti_ratio <= 50:
            credit_score = 650  # Fair
        elif dti_ratio <= 70:
            credit_score = 600  # Below average
        else:
            credit_score = 550  # Poor
        
        # Determine employment status
        employment_status = 'employed' if employment_years > 0 else 'unemployed'
        
        # Check if we have sufficient data for meaningful prediction
        if income == 0 or loan_amount == 0:
            # Return conservative estimate when data is missing
            return {
                'approval_probability': 50.0,
                'rejection_probability': 50.0,
                'risk_score': 50.0,
                'risk_level': 'MEDIUM',
                'recommendation': 'MEDIUM RISK - Insufficient data for accurate prediction',
                'model_confidence': 30.0,
                'data_quality': 'INSUFFICIENT'
            }
        
        result = self.predict_risk(
            income=income,
            credit_score=credit_score,
            loan_amount=loan_amount,
            dti_ratio=dti_ratio,
            employment_status=employment_status
        )
        
        # Add data quality indicator
        result['data_quality'] = 'GOOD' if monthly_income > 0 and loan_amount > 0 else 'LIMITED'
        
        return result


def train_model_cli():
    """CLI function to train the model"""
    predictor = XGBoostLoanPredictor()
    metrics = predictor.train_model()
    print("\n✅ Training complete!")
    return metrics


if __name__ == "__main__":
    # Train the model
    train_model_cli()
