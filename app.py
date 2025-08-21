from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS
import pandas as pd
import os
from pathlib import Path
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app, origins=['*'], methods=['GET', 'POST', 'OPTIONS'])  # Allow all origins for development

# Load trained model with better error handling
MODEL_PATH = Path(__file__).parent.parent / 'model' / 'tabpfn_gender_aware_model.pkl'
FALLBACK_MODEL_PATH = Path(__file__).parent.parent / 'model' / 'tabpfn_model.pkl'
model = None

def load_model_safely():
    """Load model with fallback options"""
    global model
    try:
        if MODEL_PATH.exists():
            model = joblib.load(MODEL_PATH)
            logger.info("✅ Primary model loaded successfully!")
            return True
        elif FALLBACK_MODEL_PATH.exists():
            model = joblib.load(FALLBACK_MODEL_PATH)
            logger.info("✅ Fallback model loaded successfully!")
            return True
        else:
            logger.error("❌ No model files found!")
            return False
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        return False

# Initialize model
model_loaded = load_model_safely()

# Load medication encoder with better error handling
ENCODER_PATH = Path(__file__).parent.parent / 'data' / 'medication_encoder.csv'
medication_map = {}

def load_encoder_safely():
    """Load encoder with fallback"""
    global medication_map
    try:
        if ENCODER_PATH.exists():
            encoder_df = pd.read_csv(ENCODER_PATH)
            medication_map = dict(zip(encoder_df['medication'], encoder_df['encoded_value']))
            logger.info("✅ Medication encoder loaded successfully!")
            logger.info(f"Available medications: {list(medication_map.keys())}")
            return True
        else:
            raise FileNotFoundError("Encoder file not found")
    except Exception as e:
        logger.error(f"❌ Error loading medication encoder: {e}")
        # Fallback medication mapping
        medication_map = {
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
        logger.info("✅ Using fallback medication mapping")
        return False

encoder_loaded = load_encoder_safely()

@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all outgoing responses"""
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    return jsonify({
        'status': 'API is running',
        'model_loaded': model is not None,
        'encoder_loaded': encoder_loaded,
        'model_path_exists': MODEL_PATH.exists(),
        'fallback_path_exists': FALLBACK_MODEL_PATH.exists(),
        'available_medications': list(medication_map.keys()),
        'medication_count': len(medication_map),
        'port': os.environ.get("PORT", 5001)
    })

@app.route('/', methods=['GET'])
def home():
    """Basic home endpoint"""
    return jsonify({'message': 'Drug Risk Prediction API', 'status': 'running', 'port': os.environ.get("PORT", 5001)})

@app.route('/predict', methods=['POST'])
def predict():
    """Predict drug risk for a patient"""
    try:
        if model is None:
            logger.error("Model not loaded for prediction request")
            return jsonify({'error': 'Model not loaded'}), 500
            
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['gender', 'age', 'medication', 'dose', 'duration']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process input data
        gender = 0 if data['gender'].lower() in ['male', 'm'] else 1
        age = int(data['age'])
        medication_name = data['medication']
        dose = int(data['dose'])
        duration = int(data['duration'])
        
        # Validate medication
        if medication_name not in medication_map:
            logger.warning(f"Invalid medication requested: {medication_name}")
            return jsonify({
                'error': f'Invalid medication: {medication_name}',
                'available_medications': list(medication_map.keys())
            }), 400
        
        med_encoded = medication_map[medication_name]
        
        # Validate ranges
        if age < 0 or age > 120:
            logger.warning(f"Invalid age: {age}")
            return jsonify({'error': 'Age must be between 0 and 120'}), 400
        if dose <= 0:
            logger.warning(f"Invalid dose: {dose}")
            return jsonify({'error': 'Dose must be positive'}), 400
        if duration <= 0:
            logger.warning(f"Invalid duration: {duration}")
            return jsonify({'error': 'Duration must be positive'}), 400
        
        # Create feature array [sex, age, med, dose, time]
        features = np.array([[gender, age, med_encoded, dose, duration]])
        
        # Make prediction with error handling
        try:
            risk_prob = model.predict_proba(features)[0][1]
            risk_prediction = model.predict(features)[0]
            risk_label = 'HIGH RISK' if risk_prediction == 1 else 'LOW RISK'
            logger.info(f"Prediction successful: {risk_label} (prob: {risk_prob:.4f})")
        except Exception as pred_error:
            logger.error(f"Model prediction failed: {pred_error}")
            return jsonify({'error': f'Model prediction failed: {str(pred_error)}'}), 500
        
        # Create response
        response = {
            'patient_info': {
                'gender': data['gender'],
                'age': age,
                'medication': medication_name,
                'dose': dose,
                'duration': duration
            },
            'prediction': {
                'risk_probability': round(float(risk_prob), 4),
                'risk_label': risk_label,
                'risk_score': int(risk_prediction),
                'confidence': round(float(max(risk_prob, 1 - risk_prob)), 4)
            },
            'interpretation': {
                'message': f"The patient has a {risk_label.lower()} of adverse drug reactions.",
                'recommendation': get_recommendation(float(risk_prob), medication_name)
            }
        }
        
        return jsonify(response)
        
    except ValueError as e:
        logger.error(f"ValueError in prediction: {e}")
        return jsonify({'error': f'Invalid input format: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {e}")
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/medications', methods=['GET'])
def get_medications():
    return jsonify({
        'medications': list(medication_map.keys()),
        'count': len(medication_map)
    })

def get_recommendation(risk_prob, medication):
    if risk_prob >= 0.7:
        return f"High risk detected. Consider alternative to {medication} or reduce dosage. Monitor closely."
    elif risk_prob >= 0.3:
        return f"Moderate risk. Monitor patient closely while on {medication}."
    else:
        return f"Low risk. {medication} appears safe for this patient profile."

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Drug Risk Prediction API")
    print("=" * 50)
    print(f"Model path: {MODEL_PATH}")
    print(f"Model loaded: {model is not None}")
    print(f"Available medications: {list(medication_map.keys())}")
    print("=" * 50)

    # Use Render-assigned port or fallback to 5001
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting Flask server on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
