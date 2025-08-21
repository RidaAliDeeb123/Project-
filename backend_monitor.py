#!/usr/bin/env python3
"""
Backend Health Monitor
Monitors backend health and automatically restarts on failures
"""
import requests
import time
import subprocess
import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_monitor.log'),
        logging.StreamHandler()
    ]
)

class BackendMonitor:
    def __init__(self, api_url="http://localhost:5001", check_interval=30):
        self.api_url = api_url
        self.check_interval = check_interval
        self.failure_count = 0
        self.max_failures = 3
        self.backend_process = None
        
    def check_health(self):
        """Check if backend is responding"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('model_loaded') and data.get('status') == 'API is running':
                    logging.info("✅ Backend healthy")
                    self.failure_count = 0
                    return True
                else:
                    logging.warning("⚠️ Backend responding but model not loaded")
                    return False
            else:
                logging.error(f"❌ Backend returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Backend connection failed: {e}")
            return False
    
    def kill_existing_processes(self):
        """Kill existing backend processes"""
        try:
            if os.name == 'nt':  # Windows
                # Kill processes by name
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], check=False, capture_output=True)
                subprocess.run(["taskkill", "/f", "/im", "pythonw.exe"], check=False, capture_output=True)
            else:  # Unix/Linux/Mac
                subprocess.run(["pkill", "-f", "backend/api/app.py"], check=False)
            
            time.sleep(3)  # Wait for processes to terminate
            logging.info("✅ Existing processes terminated")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to kill existing processes: {e}")
            return False
    
    def start_backend(self):
        """Start the backend service"""
        try:
            backend_path = Path(__file__).parent / "api" / "app.py"
            
            if not backend_path.exists():
                logging.error(f"❌ Backend file not found: {backend_path}")
                return False
            
            # Start backend process
            if os.name == 'nt':  # Windows
                self.backend_process = subprocess.Popen([
                    sys.executable, str(backend_path)
                ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix/Linux/Mac
                self.backend_process = subprocess.Popen([
                    sys.executable, str(backend_path)
                ])
            
            logging.info(f"✅ Backend process started with PID: {self.backend_process.pid}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to start backend: {e}")
            return False
    
    def restart_backend(self):
        """Restart the backend service"""
        logging.info("🔄 Attempting to restart backend...")
        try:
            # Kill existing process
            if self.backend_process:
                try:
                    self.backend_process.terminate()
                    self.backend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.backend_process.kill()
                except Exception as e:
                    logging.warning(f"Could not terminate process: {e}")
            
            # Kill any other existing processes
            self.kill_existing_processes()
            
            # Start new process
            if self.start_backend():
                # Wait for startup
                time.sleep(15)
                logging.info("✅ Backend restart completed")
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to restart backend: {e}")
            return False
    
    def monitor(self):
        """Main monitoring loop"""
        logging.info("🚀 Starting backend monitor...")
        logging.info(f"📡 Monitoring backend at: {self.api_url}")
        logging.info(f"⏱️  Check interval: {self.check_interval} seconds")
        
        # Try to start backend if not running
        if not self.check_health():
            logging.info("🔄 Backend not running, attempting to start...")
            if self.start_backend():
                time.sleep(15)  # Wait for startup
            else:
                logging.error("❌ Failed to start backend initially")
        
        while True:
            try:
                if not self.check_health():
                    self.failure_count += 1
                    logging.warning(f"⚠️ Backend failure #{self.failure_count}")
                    
                    if self.failure_count >= self.max_failures:
                        logging.error("❌ Max failures reached, restarting backend...")
                        if self.restart_backend():
                            self.failure_count = 0
                        else:
                            logging.critical("💀 Failed to restart backend!")
                            break
                else:
                    # Reset failure count on success
                    if self.failure_count > 0:
                        logging.info("✅ Backend recovered, resetting failure count")
                        self.failure_count = 0
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logging.info("🛑 Monitor stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Unexpected error in monitor loop: {e}")
                time.sleep(self.check_interval)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                logging.info("✅ Backend process terminated")
            except Exception as e:
                logging.error(f"❌ Error terminating backend process: {e}")

if __name__ == "__main__":
    try:
        monitor = BackendMonitor()
        monitor.monitor()
    except KeyboardInterrupt:
        logging.info("🛑 Monitor interrupted")
    finally:
        if 'monitor' in locals():
            monitor.cleanup()
