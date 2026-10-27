"""
CropGuard Working Model Startup Runner
Launches the FastAPI Server & PWA frontend on http://127.0.0.1:8000
"""
import sys
import io
import os

# Set UTF-8 encoding for standard output on Windows console
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load environment variables (.env) if present
env_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Check if GEMINI_API_KEY is configured
if not os.getenv("GEMINI_API_KEY"):
    print("[WARNING] GEMINI_API_KEY is not set. Please add it to your .env file.")

import uvicorn

if __name__ == "__main__":
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    masked_key = gemini_key[:6] + "..." + gemini_key[-4:] if len(gemini_key) > 10 else "Not set"

    print("=" * 65)
    print("  CropGuard: AI Crop Disease & Outbreak Prevention System")
    print("  Prototype v0.2 (Powered by Google Gemini Live)")
    print("=" * 65)
    print("  Server URL:         http://127.0.0.1:8000")
    print("  Localhost URL:      http://localhost:8000")
    print("  API Documentation:  http://127.0.0.1:8000/docs")
    print(f"  Google Gemini API:  ENABLED ({masked_key})")
    print("=" * 65)
    
    # Bind to 0.0.0.0 to support both 127.0.0.1 and localhost (IPv4 & IPv6)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
