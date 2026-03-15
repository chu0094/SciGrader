#!/usr/bin/env python3
"""
Startup script for the SciGrader backend.
This script ensures the correct Python path is set before starting the application.
"""
import sys
import os
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 加载 .env 文件中的环境变量
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Now import and run the main application
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 从 .env 文件读取配置
    host = os.environ.get("BACKEND_HOST", "localhost")
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    
    logger.info(f"Starting FastAPI backend service on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, log_level="info")