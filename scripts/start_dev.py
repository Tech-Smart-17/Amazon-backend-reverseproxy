"""
Development Startup Script. Runs Seeding and launches Uvicorn ASGI Server.
"""
import sys
import os
import subprocess

def main():
    print("==================================================")
    print("Starting Amazon Backend System Development Server...")
    print("==================================================")

    # 1. Run Seed Script
    print("\nRunning database seed script...")
    res = subprocess.run([sys.executable, "-m", "seed.seed_data"])
    if res.returncode != 0:
        print("Warning: Seed script encountered an error or was skipped.")

    # 2. Launch Uvicorn
    print("\nLaunching Uvicorn Server at http://127.0.0.1:8000 ...")
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])

if __name__ == "__main__":
    main()
