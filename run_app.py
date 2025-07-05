import subprocess
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.resolve()))

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    """Main function to run the application"""
    # Install requirements if not already installed
    if not Path("venv").exists():
        install_requirements()
    
    # Run the FastAPI application
    print("Starting the application...")
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--app-dir=."])

if __name__ == "__main__":
    main()
