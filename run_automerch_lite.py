#!/usr/bin/env python3
"""Unified entry point for AutoMerch Lite.

This script can run:
- New AutoMerch Lite API only
- Existing app with integrated routes
- Both side by side
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="Run AutoMerch Lite")
    parser.add_argument(
        "--mode",
        choices=["lite", "existing", "both"],
        default="lite",
        help="Which app to run (default: lite)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for main app (default: 8000)"
    )
    parser.add_argument(
        "--lite-port",
        type=int,
        default=8001,
        help="Port for lite app when mode=both (default: 8001)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload"
    )
    
    args = parser.parse_args()
    
    if args.mode == "lite":
        print(f"🚀 Starting AutoMerch Lite on port {args.port}")
        print("📖 API docs: http://localhost:{}/docs".format(args.port))
        print("📋 Drafts UI: http://localhost:{}/drafts".format(args.port))
        
        import uvicorn
        uvicorn.run(
            "automerch.api.app:app",
            host="0.0.0.0",
            port=args.port,
            reload=args.reload
        )
    
    elif args.mode == "existing":
        print(f"🚀 Starting existing app on port {args.port}")
        
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=args.port,
            reload=args.reload
        )
    
    elif args.mode == "both":
        print(f"🚀 Starting both apps:")
        print(f"   - Existing: http://localhost:{args.port}")
        print(f"   - Lite API: http://localhost:{args.lite_port}")
        
        import uvicorn
        import threading
        
        def run_lite():
            uvicorn.run(
                "automerch.api.app:app",
                host="0.0.0.0",
                port=args.lite_port,
                log_level="info"
            )
        
        def run_existing():
            uvicorn.run(
                "app:app",
                host="0.0.0.0",
                port=args.port,
                log_level="info"
            )
        
        # Run both in separate threads
        thread1 = threading.Thread(target=run_lite, daemon=True)
        thread2 = threading.Thread(target=run_existing, daemon=True)
        
        thread1.start()
        thread2.start()
        
        try:
            thread1.join()
            thread2.join()
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")


if __name__ == "__main__":
    main()


