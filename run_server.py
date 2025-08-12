#!/usr/bin/env python3
"""
Quick server startup script for Job Application Agent
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server import main

if __name__ == "__main__":
    print("🚀 Starting Job Application Agent MCP Server...")
    asyncio.run(main())