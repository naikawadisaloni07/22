"""
MediSmart AI — Development Server Launcher
Run this file to start the Flask development server.
"""
from app import app

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  MediSmart AI — Starting Server")
    print("  Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
