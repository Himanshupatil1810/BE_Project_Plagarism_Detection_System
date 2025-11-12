#!/usr/bin/env python3
"""
Simple setup script for Blockchain + AI Powered Plagiarism Detection System
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = ["data", "data/raw", "data/processed", "uploads", "reports", "temp"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  📁 Created: {directory}")
    
    print("✅ Directories created successfully")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Check if virtual environment should be created
    if not os.path.exists("venv"):
        print("🔧 Creating virtual environment...")
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Determine activation command based on OS
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    print("✅ Dependencies installed successfully")
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    nltk_script = """
import nltk
try:
    nltk.download('stopwords', quiet=True)
    print('NLTK stopwords downloaded successfully')
except Exception as e:
    print(f'Error downloading NLTK data: {e}')
"""
    
    with open("temp_nltk_download.py", "w") as f:
        f.write(nltk_script)
    
    success = run_command(f"{python_cmd} temp_nltk_download.py", "Downloading NLTK data")
    os.remove("temp_nltk_download.py")
    
    return success

def create_env_file():
    """Create .env file with default configuration"""
    print("⚙️ Creating environment configuration...")
    
    env_content = """# Blockchain + AI Powered Plagiarism Detection System
# Environment Configuration

# Blockchain Configuration (Optional - set to enable blockchain features)
RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=your_contract_address_here

# IPFS Configuration (Optional - set to enable IPFS features)
IPFS_URL=/ip4/127.0.0.1/tcp/5001

# Database Configuration
DATABASE_URL=data/database.db

# API Configuration
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Environment file created: .env")
    print("⚠️ Note: Blockchain and IPFS features are optional. Update .env to enable them.")

def initialize_database():
    """Initialize database with sample data"""
    print("🗄️ Initializing database...")
    
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    # Try simple initialization first (no external APIs)
    if run_command(f"{python_cmd} init_database.py", "Initializing database with sample data"):
        print("✅ Database initialized successfully with sample data")
        print("💡 To add more data (Wikipedia, arXiv), run: python data_collector.py")
        return True
    else:
        print("⚠️ Database initialization failed, but continuing...")
        return False

def create_start_script():
    """Create start script"""
    print("🚀 Creating start script...")
    
    if platform.system() == "Windows":
        start_script = """@echo off
echo Starting Blockchain + AI Powered Plagiarism Detection System

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment and start application
call venv\\Scripts\\activate
python app.py
pause
"""
        with open("start.bat", "w", encoding='utf-8') as f:
            f.write(start_script)
        print("✅ Start script created: start.bat")
    else:
        start_script = """#!/bin/bash
echo "Starting Blockchain + AI Powered Plagiarism Detection System"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment and start application
source venv/bin/activate
python app.py
"""
        with open("start.sh", "w", encoding='utf-8') as f:
            f.write(start_script)
        os.chmod("start.sh", 0o755)
        print("✅ Start script created: start.sh")

def main():
    """Main setup function"""
    print("🚀 Setting up Blockchain + AI Powered Plagiarism Detection System")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Download NLTK data
    download_nltk_data()
    
    # Create environment file
    create_env_file()
    
    # Initialize database
    initialize_database()
    
    # Create start script
    create_start_script()
    
    print("\n" + "=" * 70)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. (Optional) Update .env file to enable blockchain/IPFS features")
    print("2. Run the application:")
    if platform.system() == "Windows":
        print("   - Double-click start.bat, or")
        print("   - Run: start.bat")
    else:
        print("   - Run: ./start.sh")
    print("3. Open your browser to: http://localhost:5000")
    print("4. Open frontend: frontend/index.html")
    print("\n🌐 API will be available at: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")

if __name__ == "__main__":
    main()
