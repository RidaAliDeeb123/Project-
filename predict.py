import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Load trained model with consistent paths
MODEL_PATH = "backend/model/tabpfn_gender_aware_model.pkl"
FALLBACK_MODEL_PATH = "backend/model/tabpfn_model.pkl"
ENCODER_PATH = "backend/data/medication_encoder.csv"

def load_model():
    """Load the trained TabPFN model with fallback"""
    try:
        if Path(MODEL_PATH).exists():
            model = joblib.load(MODEL_PATH)
            print("✅ Primary model loaded successfully!")
            return model
        elif Path(FALLBACK_MODEL_PATH).exists():
            model = joblib.load(FALLBACK_MODEL_PATH)
            print("✅ Fallback model loaded successfully!")
            return model
        else:
            raise FileNotFoundError("No model files found")
    except Exception as e:
        raise Exception(f"Error loading model: {e}")

def load_medication_encoder():
    """Load medication encoding mapping"""
    try:
        encoder_df = pd.read_csv(ENCODER_PATH)
        return dict(zip(encoder_df['medication'], encoder_df['encoded_value']))
    except Exception as e:
        # Fallback encoding if file not found
        print("⚠️ Using fallback medication encoding")
        return {
            "Sertraline": 0,
            "Warfarin": 1,
            "Digoxin": 2,
            "Propranolol": 3,
            "Acetaminophen": 4,
            "Zolpidem": 5,
            "Aspirin": 6,
            "Ibuprofen": 7,
            "Metformin": 8,
            "Lisinopril": 9,
            "Atorvastatin": 10
        }

# Global variables for model and encoder
model = None
medication_encoding = None

def initialize():
    """Initialize model and encoder"""
    global model, medication_encoding
    if model is None:
        model = load_model()
    if medication_encoding is None:
        medication_encoding = load_medication_encoder()

def predict_risk(gender, age, medication, dose, duration):
    """
    Predict drug risk for a patient
    
    Args:
        gender (str): 'Male' or 'Female'
        age (int): Patient age
        medication (str): Medication name
        dose (int): Dose in mg
        duration (int): Duration in days
    
    Returns:
        dict: Risk probability and label
    """
    try:
        # Initialize if needed
        initialize()
        
        # Encode gender (1 for Female, 0 for Male)
        gender_encoded = 1 if gender.lower() in ['female', 'f'] else 0
        
        # Encode medication
        med_encoded = medication_encoding.get(medication, -1)
        if med_encoded == -1:
            available_meds = list(medication_encoding.keys())
            raise ValueError(f"Invalid medication. Available: {available_meds}")
        
        # Create feature array
        features = np.array([[gender_encoded, age, med_encoded, dose, duration]])
        
        # Make prediction
        prob = model.predict_proba(features)[0][1]
        prediction = model.predict(features)[0]
        
        # Determine risk label
        label = "HIGH RISK" if prediction == 1 else "LOW RISK"
        
        return {
            "risk_probability": round(float(prob), 3),
            "risk_label": label,
            "confidence": "High" if abs(prob - 0.5) > 0.3 else "Medium"
        }
        
    except Exception as e:
        raise Exception(f"Prediction error: {e}")

def get_available_medications():
    """Get list of available medications"""
    initialize()
    return list(medication_encoding.keys())

# Test function
if __name__ == "__main__":
    try:
        # Test prediction
        result = predict_risk("Female", 45, "Metformin", 50, 15)
        print("Test Prediction:")
        print(f"Risk Probability: {result['risk_probability']}")
        print(f"Risk Label: {result['risk_label']}")
        print(f"Confidence: {result['confidence']}")
        
        print(f"\nAvailable medications: {get_available_medications()}")
        
    except Exception as e:
        print(f"Error: {e}")
