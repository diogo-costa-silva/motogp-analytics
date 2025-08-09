"""
MotoGP Analytics Streamlit App Launcher
=======================================
Purpose: Launch script for the Streamlit demo application
Usage: python apps/streamlit_demo/run_app.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application"""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    # Set the Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root)
    
    print("🏁 Starting MotoGP Analytics Demo Application...")
    print(f"📁 Working directory: {project_root}")
    print(f"🌐 App will be available at: http://localhost:8501")
    print("=" * 60)
    
    # Launch Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "apps/streamlit_demo/main.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--theme.base=light",
            "--theme.primaryColor=#1f77b4"
        ]
        
        subprocess.run(cmd, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()