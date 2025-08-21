#!/usr/bin/env python3
"""
Startup script for Drug Risk Prediction System
Launches both backend API and frontend services
"""
import subprocess
import time
import sys
import os
from pathlib import Path

def start_backend():
    """Start the backend API service"""
    print("🚀 Starting Backend API...")
    backend_path = Path(__file__).parent / "backend" / "api" / "app.py"
    
    if not backend_path.exists():
        print(f"❌ Backend file not found: {backend_path}")
        return None
    
    try:
        # Start backend in a new console window on Windows
        if os.name == 'nt':  # Windows
            process = subprocess.Popen([
                sys.executable, str(backend_path)
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            process = subprocess.Popen([
                sys.executable, str(backend_path)
            ])
        
        print(f"✅ Backend started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend service"""
    print("🌐 Starting Frontend...")
    frontend_path = Path(__file__).parent / "app.py"
    
    if not frontend_path.exists():
        print(f"❌ Frontend file not found: {frontend_path}")
        return None
    
    try:
        # Start frontend in a new console window on Windows
        if os.name == 'nt':  # Windows
            process = subprocess.Popen([
                sys.executable, str(frontend_path)
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            process = subprocess.Popen([
                sys.executable, str(frontend_path)
            ])
        
        print(f"✅ Frontend started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🏥 Drug Risk Prediction System Startup")
    print("=" * 50)
    
    # Start backend first
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot continue without backend")
        return
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(10)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return
    
    print("\n🎉 Services started successfully!")
    print("=" * 50)
    print("📊 Frontend: http://localhost:5000")
    print("🏥 Backend API: http://localhost:5001")
    print("📈 Health Check: http://localhost:5000/health")
    print("=" * 50)
    print("💡 Keep this window open to monitor services")
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep running and monitor processes
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process has stopped")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend process has stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
            
        print("👋 All services stopped")

if __name__ == "__main__":
    main()
