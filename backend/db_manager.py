"""
SciGrader 后端数据库管理器
用于 FastAPI 后端连接 MySQL 数据库
"""
import os
import logging
from typing import Optional, List, Dict, Any
from mysql.connector import connect, Error
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类 - FastAPI 后端版本"""
    
    def __init__(self):
        self.connection = None
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'scigrader_db')
        }
    
    def create_connection(self) -> bool:
        """创建数据库连接"""
        try:
            logger.info(f"尝试连接数据库：{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
            
            self.connection = connect(**self.db_config)
            
            if self.connection.is_connected():
                logger.info("✅ 数据库连接成功")
                return True
            else:
                logger.warning("⚠️ 数据库连接失败：连接未建立")
                return False
                
        except Error as e:
            logger.error(f"❌ 数据库连接失败：{e}")
            logger.error(f"   配置：host={self.db_config['host']}, user={self.db_config['user']}, database={self.db_config['database']}")
            return False
        except Exception as e:
            logger.error(f"❌ 未知错误：{e}")
            return False
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: bool = False):
        """执行 SQL 查询"""
        # 检查数据库连接
        if not self.connection or not self.connection.is_connected():
            logger.error("❌ 数据库未连接")
            if not self.create_connection():
                return False
        
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                logger.info(f"✅ 查询成功，返回 {len(result)} 条记录")
                return result
            else:
                self.connection.commit()
                row_count = cursor.rowcount
                logger.info(f"✅ 执行成功，影响 {row_count} 行")
                return cursor.lastrowid if cursor.lastrowid else True
                
        except Error as e:
            logger.error(f"❌ 查询执行失败：{e}")
            logger.error(f"   SQL: {query[:100]}...")
            if params:
                logger.error(f"   参数：{params}")
            return False
        except Exception as e:
            logger.error(f"❌ 未知错误：{e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    # ========== 以下是具体的数据库操作方法 ==========
    
    def verify_user(self, username: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """验证用户登录"""
        query = """
            SELECT user_id, username, role, email 
            FROM users 
            WHERE username = %s AND password_hash = %s AND is_active = TRUE
        """
        result = self.execute_query(query, (username, password_hash), fetch=True)
        return result[0] if result else None
    
    def get_all_problems(self, teacher_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取所有题目"""
        if teacher_id:
            query = "SELECT * FROM problems WHERE creator_id = %s ORDER BY created_at DESC"
            return self.execute_query(query, (teacher_id,), fetch=True)
        else:
            query = "SELECT * FROM problems ORDER BY created_at DESC"
            return self.execute_query(query, fetch=True)
    
    def get_all_assignments(self, teacher_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取所有作业"""
        if teacher_id:
            query = "SELECT * FROM assignments WHERE teacher_id = %s ORDER BY created_at DESC"
            return self.execute_query(query, (teacher_id,), fetch=True)
        else:
            query = "SELECT * FROM assignments ORDER BY created_at DESC"
            return self.execute_query(query, fetch=True)
    
    def get_assignment_problems(self, assignment_id: int) -> List[Dict[str, Any]]:
        """获取作业包含的题目列表"""
        query = "SELECT problem_ids FROM assignments WHERE assignment_id = %s"
        result = self.execute_query(query, (assignment_id,), fetch=True)
        
        if not result or not result[0]['problem_ids']:
            return []
        
        import json
        problem_ids = json.loads(result[0]['problem_ids'])
        
        if not problem_ids:
            return []
        
        # 根据 ID 列表获取题目详情
        placeholders = ','.join(['%s'] * len(problem_ids))
        query = f"""
            SELECT * FROM problems 
            WHERE problem_id IN ({placeholders})
            ORDER BY FIELD(problem_id, {placeholders})
        """
        params = problem_ids + problem_ids  # 两次参数列表用于 FIELD 排序
        return self.execute_query(query, tuple(params), fetch=True)
    
    def get_student_submissions(self, student_id: int) -> List[Dict[str, Any]]:
        """获取学生提交记录"""
        query = """
            SELECT s.*, a.assignment_title, a.course_name, a.due_date
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            WHERE s.student_id = %s
            ORDER BY s.submit_time DESC
        """
        return self.execute_query(query, (student_id,), fetch=True)
    
    def create_submission(self, submission_data: tuple) -> Any:
        """创建作业提交"""
        query = """
            INSERT INTO submissions (
                assignment_id, student_id, submission_content,
                submission_files, status
            ) VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, submission_data)
    
    def update_submission(self, submission_data: tuple, submission_id: int) -> Any:
        """更新作业提交"""
        query = """
            UPDATE submissions 
            SET submission_content = %s,
                submission_files = %s,
                status = %s,
                submit_time = NOW(),
                auto_grade_score = NULL,
                auto_grade_comments = NULL,
                teacher_grade_score = NULL,
                teacher_comments = NULL,
                graded_at = NULL,
                graded_by = NULL
            WHERE submission_id = %s
        """
        return self.execute_query(query, (*submission_data, submission_id))
    
    def get_student_statistics(self, student_id: int) -> Optional[Dict[str, Any]]:
        """获取学生学习统计"""
        query = """
            SELECT * FROM student_statistics_view 
            WHERE user_id = %s
        """
        result = self.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None


# 单例模式
_db_manager_instance: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器单例"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
        _db_manager_instance.create_connection()
    return _db_manager_instance
