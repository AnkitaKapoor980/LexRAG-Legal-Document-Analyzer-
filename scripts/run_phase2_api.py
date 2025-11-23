"""
Quick script to run Phase 2 API server.
"""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("Starting Phase 2 API server...")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "src.phase2_agents.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

