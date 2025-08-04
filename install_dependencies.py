import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Installed: {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        return False

def main():
    """Install all required packages."""
    
    print("Installing iFood Data Governance Dependencies")
    print("=" * 50)
    
    core_packages = [
        "streamlit==1.28.2",
        "plotly==5.17.0",
        "pandas==2.1.4",
        "numpy==1.24.3",
        "pydantic==2.5.0",
        "email-validator==2.1.0",
        "pyyaml==6.0.1",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ]
    
    optional_packages = [
        "great-expectations==0.17.23",
        "apache-airflow==2.7.3",
        "dbt-core==1.6.0",
        "pytest==7.4.3",
        "black==23.11.0"
    ]
    
    print("Installing core packages...")
    failed_core = []
    for package in core_packages:
        if not install_package(package):
            failed_core.append(package)
    
    print("\nInstalling optional packages...")
    failed_optional = []
    for package in optional_packages:
        if not install_package(package):
            failed_optional.append(package)
    
    print("\n" + "=" * 50)
    print("Installation Summary")
    print("=" * 50)
    
    if not failed_core:
        print("All core packages installed successfully!")
        print("You can now run: streamlit run dashboards/simple_dashboard.py")
    else:
        print("Some core packages failed to install:")
        for package in failed_core:
            print(f"   - {package}")
    
    if failed_optional:
        print("\n Some optional packages failed to install:")
        for package in failed_optional:
            print(f"   - {package}")
        print("   (These are not required for basic functionality)")
    
    print(f"\n Next steps:")
    print("1. Run: streamlit run dashboards/simple_dashboard.py")
    print("2. Open browser to: http://localhost:8501")
    print("3. Explore the dashboard!")

if __name__ == "__main__":
    main()
