"""
Convenience launcher that starts the Phase 2 API backend and Phase 3 Streamlit UI.

Usage:
    python scripts/run_app.py

This will:
1. Start the FastAPI backend (uvicorn) on port 8000.
2. Start the Streamlit frontend (phase3_frontend/streamlit_app.py).
3. Handle Ctrl+C to stop both processes cleanly.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run() -> None:
    env = os.environ.copy()
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.phase2_agents.api.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]
    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/phase3_frontend/streamlit_app.py",
        "--server.headless",
        "true",
    ]

    processes: list[subprocess.Popen] = []

    def stop_processes() -> None:
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()

    try:
        print("=" * 70)
        print("🚀 Starting LexRAG - Legal Document Analyzer")
        print("=" * 70)
        print()
        
        print("📡 Starting FastAPI backend...")
        print(f"   Command: {' '.join(backend_cmd)}")
        backend = subprocess.Popen(
            backend_cmd, 
            cwd=ROOT, 
            env=env
            # No stdout/stderr capture - let logs show in terminal
        )
        processes.append(backend)
        print("   ✓ Backend process started (PID: {})".format(backend.pid))
        print("   ⏳ Waiting for backend to initialize...")
        time.sleep(3)
        
        if backend.poll() is not None:
            print("   ❌ Backend failed to start!")
            print("   Check logs above for errors.")
            return

        print()
        print("🎨 Starting Streamlit frontend...")
        print(f"   Command: {' '.join(frontend_cmd)}")
        frontend = subprocess.Popen(
            frontend_cmd, 
            cwd=ROOT, 
            env=env
            # No stdout/stderr capture - let logs show in terminal
        )
        processes.append(frontend)
        print("   ✓ Frontend process started (PID: {})".format(frontend.pid))
        print("   ⏳ Waiting for Streamlit to initialize...")
        time.sleep(5)
        
        if frontend.poll() is not None:
            print("   ❌ Frontend failed to start!")
            print("   Check logs above for errors.")
            return

        print()
        print("=" * 70)
        print("✅ LexRAG is running successfully!")
        print("=" * 70)
        print()
        print("📍 Access the application:")
        print("   • Streamlit UI:  http://localhost:8501")
        print("   • Backend API:   http://localhost:8000")
        print("   • API Docs:      http://localhost:8000/docs")
        print()
        print("💡 Tips:")
        print("   • Upload a PDF contract in the Streamlit UI")
        print("   • Click 'Extract & Analyze' to process the document")
        print("   • Use the Q&A tab to ask questions about the contract")
        print()
        print("⚠️  Press Ctrl+C to stop both services")
        print("=" * 70)
        print()
        print("📋 BACKEND LOGS (live):")
        print("=" * 70)
        print()

        while True:
            time.sleep(1)
            if backend.poll() is not None:
                print("\n❌ Backend process exited unexpectedly. Stopping frontend...")
                break
            if frontend.poll() is not None:
                print("\n❌ Frontend process exited unexpectedly. Stopping backend...")
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down LexRAG...")
        print("   Stopping backend and frontend processes...")
    finally:
        stop_processes()
        print("   ✓ All processes stopped")
        print("   👋 Goodbye!")


if __name__ == "__main__":
    run()

