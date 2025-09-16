#!/usr/bin/env python3
"""
Startup script for the MCP server that ensures environment variables are properly loaded.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file first
project_root = Path(__file__).resolve().parent
dotenv_path = project_root / '.env'
load_dotenv(dotenv_path, override=True)

# Set environment variables from command line args or defaults
env_vars = {
    'ENABLE_HUGGINGFACE': 'true',
    'HUGGINGFACE_EMBEDDING_MODEL': 'sentence-transformers/all-MiniLM-L6-v2',
    'HUGGINGFACE_USE_API': 'true',
    'HUGGINGFACE_API_TOKEN': os.getenv('HUGGINGFACE_API_TOKEN', ''),
    'HUGGINGFACE_DEVICE': 'cpu',
    'EMBEDDING_PROVIDER': 'auto',
    'TRANSPORT': 'stdio'
}

# Override environment variables
for key, value in env_vars.items():
    if not os.getenv(key):
        os.environ[key] = value

# Now import and run the main MCP server
sys.path.insert(0, str(project_root / 'src'))
from crawl4ai_mcp import *

if __name__ == "__main__":
    # The main MCP server code will run when this module is imported
    pass