import os
import sys
import subprocess

def print_step(step, message):
    """Print formatted step message"""
    print(f"\n Step {step}: {message}")
    print("-" * 50)

def create_directories():
    """Create necessary directories"""
    directories = [
        'modules',
        'templates', 
        'static/css',
        'static/js',
        'static/images'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory exists: {directory}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f" Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("Please upgrade to Python 3.8 or higher")
        return False

def install_dependencies():
    """Install required dependencies"""
    if not os.path.exists('requirements.txt'):
        print("requirements.txt not found")
        return False
    
    try:
        print("Installing dependencies...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True, check=True)
        
        print("All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        print("Error output:", e.stderr)
        return False

def create_init_files():
    """Create necessary __init__.py files"""
    init_files = ['modules/__init__.py']
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Package initialization file\n')
            print(f"Created {init_file}")
        else:
            print(f"{init_file} already exists")

def test_installation():
    """Test the installation"""
    try:
        # Try to import the main app
        import app
        print("Main application imports successfully")
        
        # Try to import modules
        from modules import security_checks, ai_analyzer
        print("Security modules import successfully")
        
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def start_application():
    """Start the Flask application"""
    print("\nStarting the application...")
    print("The application will start on http://localhost:5000")
    print("Press Ctrl+C to stop the application")
    print("\n" + "="*50)
    
    try:
        os.system(f"{sys.executable} app.py")
    except KeyboardInterrupt:
        print("\n\nApplication stopped")

def main():
    """Main setup function"""
    print("Website Security Checker - Quick Start Setup")
    print("=" * 60)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    if not check_python_version():
        return
    
    # Step 2: Create directories
    print_step(2, "Creating project directories")
    create_directories()
    
    # Step 3: Create init files
    print_step(3, "Creating initialization files")
    create_init_files()
    
    # Step 4: Install dependencies
    print_step(4, "Installing dependencies")
    if not install_dependencies():
        print("\nSetup failed at dependency installation")
        print("Please run manually: pip install -r requirements.txt")
        return
    
    # Step 5: Test installation
    print_step(5, "Testing installation")
    if not test_installation():
        print("\nSetup failed at testing phase")
        print("Please check the error messages above")
        return
    
    # Success message
    print("\n" + "="*60)
    print("Setup completed successfully!")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Run the application: python app.py")
    print("2. Open http://localhost:5000 in your browser")
    
    # Ask if user wants to start the app
    while True:
        start_now = input("\nWould you like to start the application now? (y/n): ").lower().strip()
        if start_now in ['y', 'yes']:
            start_application()
            break
        elif start_now in ['n', 'no']:
            print("\n👍 You can start the application later with: python app.py")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no")

if __name__ == "__main__":
    main()