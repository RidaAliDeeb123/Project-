# Drug Risk Prediction System

A machine learning system that predicts adverse drug reaction risks based on patient demographics and medication information.

## 🚀 Quick Start

### Option 1: Windows (Recommended)
1. Double-click `start_services.bat`
2. This will automatically:
   - Install required dependencies
   - Start the backend API service
   - Start the frontend web interface

### Option 2: Manual Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend API (in one terminal):
   ```bash
   python backend/api/app.py
   ```

3. Start the frontend (in another terminal):
   ```bash
   python app.py
   ```

## 🏗️ Architecture

The system now uses a **two-service architecture** to prevent disconnection issues:

- **Frontend Service** (Port 5000): Web interface and API proxy
- **Backend API Service** (Port 5001): Machine learning model and prediction logic

### Why This Fixes Disconnections

1. **Port Separation**: Each service runs on its own port, preventing conflicts
2. **Proxy Pattern**: Frontend forwards requests to backend, providing a stable interface
3. **Health Monitoring**: Built-in health checks and automatic recovery
4. **Better Error Handling**: Comprehensive logging and error management

## 📊 Services

### Frontend (Port 5000)
- **Web Interface**: http://localhost:5000
- **Health Check**: http://localhost:5000/health
- **API Endpoints**: 
  - `POST /predict` - Make predictions
  - `GET /medications` - Get available medications

### Backend API (Port 5001)
- **API Health**: http://localhost:5001/health
- **Direct API**: http://localhost:5001/predict
- **Model Management**: Automatic model loading with fallbacks

## 🔧 Monitoring & Recovery

### Backend Monitor
Run the monitor to automatically restart failed services:
```bash
python backend_monitor.py
```

### Health Checks
- Frontend automatically checks backend status every 30 seconds
- Visual indicators show service status
- Automatic error handling and user feedback

## 📁 File Structure

```
combinedproject-main/
├── app.py                          # Frontend service (Port 5000)
├── backend/
│   ├── api/
│   │   └── app.py                 # Backend API (Port 5001)
│   ├── data/                      # Data files and encoders
│   └── model/                     # Trained ML models
├── start_services.py              # Service launcher
├── start_services.bat             # Windows batch file
├── backend_monitor.py             # Health monitoring
└── requirements.txt               # Python dependencies
```

## 🚨 Troubleshooting

### Backend Won't Start
1. Check if port 5001 is available
2. Ensure model files exist in `backend/model/`
3. Check Python dependencies are installed

### Frontend Can't Connect
1. Verify backend is running on port 5001
2. Check firewall settings
3. Look for error messages in the web interface

### Port Already in Use
1. Kill existing processes:
   ```bash
   # Windows
   taskkill /f /im python.exe
   
   # Linux/Mac
   pkill -f "app.py"
   ```
2. Restart services

## 📈 Features

- **Gender-Aware Predictions**: Separate models for male/female patients
- **Real-time Health Monitoring**: Automatic service recovery
- **Comprehensive Logging**: Detailed request/response tracking
- **Fallback Systems**: Multiple model and encoder fallbacks
- **Cross-Platform**: Works on Windows, Linux, and macOS

## 🔒 Security Notes

- CORS is enabled for development (allows all origins)
- For production, restrict CORS origins appropriately
- Consider adding authentication for production use

## 📝 Logs

- **Frontend logs**: Console output
- **Backend logs**: Console output + file logging
- **Monitor logs**: `backend_monitor.log`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both services
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.