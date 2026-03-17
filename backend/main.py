# app/main.py
import sys
import os
from dotenv import load_dotenv

# Add the project root to the Python path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file (for local development)
# On Render, env vars are set in the dashboard
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️ .env file not found at {env_path}, using environment variables")

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import prob_preview, hw_preview, ai_grading, human_edit, assignment
# from app.db import init_db
import logging

# --- 日志和应用基础设置 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting to create FastAPI app...")
    
    app = FastAPI(title="SciGrader")

    # Include routers - these might initialize database connections
    logger.info("📦 Including routers...")
    try:
        app.include_router(prob_preview.router)
        logger.info("✅ prob_preview loaded")
    except Exception as e:
        logger.error(f"❌ prob_preview failed: {e}")
    
    try:
        app.include_router(hw_preview.router)
        logger.info("✅ hw_preview loaded")
    except Exception as e:
        logger.error(f"❌ hw_preview failed: {e}")
    
    try:
        app.include_router(ai_grading.router)
        logger.info("✅ ai_grading loaded")
    except Exception as e:
        logger.error(f"❌ ai_grading failed: {e}")
    
    try:
        app.include_router(human_edit.router)
        logger.info("✅ human_edit loaded")
    except Exception as e:
        logger.error(f"❌ human_edit failed: {e}")
    
    try:
        app.include_router(assignment.router)
        logger.info("✅ assignment loaded")
    except Exception as e:
        logger.error(f"❌ assignment failed: {e}")
    # Configure CORS for deployment
    # 从 .env 文件读取 FRONTEND_URLS 配置
    frontend_origins_str = os.environ.get("FRONTEND_URLS", "http://localhost:8501")
    origins = [origin.strip() for origin in frontend_origins_str.split(",")] if frontend_origins_str else []
    
    # Add default localhost origin
    if "http://localhost:8501" not in origins:
        origins.append("http://localhost:8501")
    
    # Log the configured origins
    logger.info(f"Configured CORS origins: {origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def read_root():
        return {"message": "SciGrader Backend is running", "status": "success"}

    @app.get("/health")
    async def health_check():
        import psutil
        import os
        
        # Get memory usage
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Get CPU usage
        cpu_percent = process.cpu_percent()
        
        return {
            "status": "healthy", 
            "message": "SciGrader backend is running",
            "memory_usage_mb": round(memory_mb, 2),
            "cpu_percent": cpu_percent
        }

    return app

app = create_app()

# Load problem data on startup
# @app.on_event("startup")
# async def load_problem_data_on_startup():
#     """Load problem data from JSON files when the application starts."""
#     try:
#         import os
#         import json
#         from backend.dependencies import problem_data
        
#         # Load problem data from answer_index_by_problems.json
#         problems_file = os.path.join(os.path.dirname(__file__), 'routers', 'answer_index_by_problems.json')
        
#         if os.path.exists(problems_file):
#             with open(problems_file, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
                
#             # Convert to the expected format
#             problems = data.get('students', [])
#             for problem in problems:
#             # Store the problem data with q_id as the key
#                     problem_data[q_id] = {
#                         'q_id': q_id,
#                         'number': problem.get('number', ''),
#                         'type': problem.get('type', '概念题'),
#                         'stem': problem.get('stem', ''),
#                         'criterion': problem.get('criterion', '默认评分标准')
#                     }
            
#             logger.info(f"Loaded {len(problem_data)} problems into problem_data on startup")
#         else:
#             logger.warning(f"Problems file not found: {problems_file}")
            
#     except Exception as e:
#         logger.error(f"Error loading problem data on startup: {e}")

# # 如果需要在启动时初始化 DB 或其它资源
# @app.on_event("startup")
# async def on_startup():
#     init_db()

# --- 本地启动服务器 ---
if __name__ == "__main__":
    import uvicorn
    
    # 从 .env 文件读取配置
    host = os.environ.get("BACKEND_HOST", "0.0.0.0")
    port = int(os.environ.get("BACKEND_PORT", "8000"))
        
    logger.info(f"启动 FastAPI 后端服务，监听 http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)