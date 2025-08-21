from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Backend API configuration
BACKEND_URL = "http://localhost:5001"
BACKEND_TIMEOUT = 30

def check_backend_health():
    """Check if backend API is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend health check failed: {e}")
        return False

@app.route('/')
def home():
    """Simple web interface for testing"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drug Risk Prediction</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
            .high-risk { background-color: #f8d7da; border: 1px solid #f5c6cb; }
            .low-risk { background-color: #d4edda; border: 1px solid #c3e6cb; }
            .error { background-color: #fff3cd; border: 1px solid #ffeaa7; }
            .status { padding: 10px; margin-bottom: 20px; border-radius: 4px; text-align: center; }
            .status.online { background-color: #d4edda; color: #155724; }
            .status.offline { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>🏥 Drug Risk Prediction System</h1>
        
        <div id="status" class="status">
            <span id="statusText">Checking backend status...</span>
        </div>
        
        <form id="predictionForm">
            <div class="form-group">
                <label for="gender">Gender:</label>
                <select id="gender" name="gender" required>
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="age">Age:</label>
                <input type="number" id="age" name="age" min="1" max="120" required>
            </div>
            
            <div class="form-group">
                <label for="medication">Medication:</label>
                <select id="medication" name="medication" required>
                    <option value="">Select Medication</option>
                    <option value="Atorvastatin">Atorvastatin</option>
                    <option value="Metformin">Metformin</option>
                    <option value="Lisinopril">Lisinopril</option>
                    <option value="Aspirin">Aspirin</option>
                    <option value="Ibuprofen">Ibuprofen</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="dose">Dose (mg):</label>
                <input type="number" id="dose" name="dose" min="1" max="1000" required>
            </div>
            
            <div class="form-group">
                <label for="duration">Duration (days):</label>
                <input type="number" id="duration" name="duration" min="1" max="365" required>
            </div>
            
            <button type="submit" id="submitBtn">Predict Risk</button>
        </form>
        
        <div id="result"></div>
        
        <script>
            // Check backend status on page load
            async function checkBackendStatus() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    if (data.status === 'healthy') {
                        document.getElementById('status').className = 'status online';
                        document.getElementById('statusText').textContent = '✅ Backend API is online';
                        document.getElementById('submitBtn').disabled = false;
                    } else {
                        throw new Error('Backend not healthy');
                    }
                } catch (error) {
                    document.getElementById('status').className = 'status offline';
                    document.getElementById('statusText').textContent = '❌ Backend API is offline - Please start the backend service';
                    document.getElementById('submitBtn').disabled = true;
                }
            }
            
            // Check status every 30 seconds
            checkBackendStatus();
            setInterval(checkBackendStatus, 30000);
            
            document.getElementById('predictionForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData.entries());
                
                // Convert numeric fields
                data.age = parseInt(data.age);
                data.dose = parseInt(data.dose);
                data.duration = parseInt(data.duration);
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        const riskClass = result.risk_label === 'HIGH RISK' ? 'high-risk' : 'low-risk';
                        document.getElementById('result').innerHTML = `
                            <div class="result ${riskClass}">
                                <h3>Prediction Result</h3>
                                <p><strong>Risk Label:</strong> ${result.risk_label}</p>
                                <p><strong>Risk Probability:</strong> ${result.risk_probability}</p>
                                <p><strong>Confidence:</strong> ${result.confidence}</p>
                                <p><strong>Recommendation:</strong> ${result.interpretation.recommendation}</p>
                            </div>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `
                            <div class="result error">
                                <h3>Error</h3>
                                <p>${result.error}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `
                        <div class="result error">
                            <h3>Error</h3>
                            <p>Failed to connect to server: ${error.message}</p>
                        </div>
                    `;
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/predict', methods=['POST'])
def predict():
    """Proxy endpoint for risk prediction - forwards to backend API"""
    try:
        # Check backend health first
        if not check_backend_health():
            logger.error("Backend API is not responding")
            return jsonify({"error": "Backend API is not available. Please ensure the backend service is running."}), 503
        
        data = request.json
        
        # Validate required fields
        required_fields = ['gender', 'age', 'medication', 'dose', 'duration']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Forward request to backend API
        try:
            response = requests.post(
                f"{BACKEND_URL}/predict",
                json=data,
                timeout=BACKEND_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Prediction request forwarded successfully to backend")
                return jsonify(response.json())
            else:
                logger.error(f"Backend API returned error: {response.status_code}")
                return jsonify(response.json()), response.status_code
                
        except requests.exceptions.Timeout:
            logger.error("Backend API request timed out")
            return jsonify({"error": "Backend API request timed out. Please try again."}), 504
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to backend API")
            return jsonify({"error": "Cannot connect to backend API. Please ensure the service is running."}), 503
        except Exception as e:
            logger.error(f"Error forwarding request to backend: {e}")
            return jsonify({"error": f"Backend communication error: {str(e)}"}), 500
        
    except ValueError as e:
        logger.error(f"ValueError in prediction: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {e}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/medications', methods=['GET'])
def medications():
    """Proxy endpoint for medications - forwards to backend API"""
    try:
        if not check_backend_health():
            return jsonify({"error": "Backend API is not available"}), 503
            
        response = requests.get(f"{BACKEND_URL}/medications", timeout=10)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error getting medications: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint that also checks backend status"""
    try:
        backend_healthy = check_backend_health()
        return jsonify({
            "status": "healthy" if backend_healthy else "degraded",
            "service": "Drug Risk Prediction Frontend",
            "backend_status": "online" if backend_healthy else "offline",
            "backend_url": BACKEND_URL
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "service": "Drug Risk Prediction Frontend",
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Drug Risk Prediction Frontend")
    print("📊 Web interface: http://localhost:5000")
    print("🔗 API endpoint: http://localhost:5000/predict")
    print("💊 Available medications: http://localhost:5000/medications")
    print("🏥 Backend API should be running on: http://localhost:5001")
    print("=" * 60)
    
    # Check backend status on startup
    if check_backend_health():
        print("✅ Backend API is online")
    else:
        print("⚠️  Backend API is offline - Please start the backend service")
        print("   Run: python backend/api/app.py")
    
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
