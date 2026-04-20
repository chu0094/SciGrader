"""
SciGrader 数据库工具类
用于连接和操作 MySQL 数据库
"""
import streamlit as st
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime, date


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.connection = None
    
    def create_connection(self):
        """创建数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=st.secrets["database"]["host"],
                port=st.secrets["database"]["port"],
                user=st.secrets["database"]["user"],
                password=st.secrets["database"]["password"],
                database=st.secrets["database"]["database"]
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            st.error(f"数据库连接失败：{e}")
            return False
        return False
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """执行 SQL 查询"""
        # 检查数据库连接
        if not self.connection or not self.connection.is_connected():
            st.error("❌ 数据库未连接，请检查配置并重新加载页面")
            return False
        
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                return cursor.lastrowid if cursor.lastrowid else True
                
        except Error as e:
            st.error(f"查询执行失败：{e}")
            return False
        finally:
            if cursor:
                cursor.close()
    
    def verify_user(self, username, password_hash):
        """验证用户登录"""
        query = """
            SELECT user_id, username, role, email 
            FROM users 
            WHERE username = %s AND password_hash = %s AND is_active = TRUE
        """
        result = self.execute_query(query, (username, password_hash), fetch=True)
        return result[0] if result else None
    
    def get_all_problems(self, teacher_id=None):
        """获取所有题目"""
        if teacher_id:
            query = "SELECT * FROM problems WHERE creator_id = %s ORDER BY created_at DESC"
            return self.execute_query(query, (teacher_id,), fetch=True)
        else:
            query = "SELECT * FROM problems ORDER BY created_at DESC"
            return self.execute_query(query, fetch=True)
    
    def get_all_assignments(self, teacher_id=None):
        """获取所有作业"""
        if teacher_id:
            query = "SELECT * FROM assignments WHERE teacher_id = %s ORDER BY created_at DESC"
            return self.execute_query(query, (teacher_id,), fetch=True)
        else:
            query = "SELECT * FROM assignments ORDER BY created_at DESC"
            return self.execute_query(query, fetch=True)
    
    def get_assignment_problems(self, assignment_id):
        """获取作业包含的题目列表"""
        # 先获取作业的 problem_ids
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
    
    def get_student_submissions(self, student_id):
        """获取学生提交记录"""
        query = """
            SELECT s.*, a.assignment_title, a.course_name, a.due_date
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            WHERE s.student_id = %s
            ORDER BY s.submit_time DESC
        """
        return self.execute_query(query, (student_id,), fetch=True)
    
    def get_assignment_submissions(self, assignment_id):
        """获取作业的提交情况"""
        query = """
            SELECT s.*, u.username as student_name
            FROM submissions s
            JOIN users u ON s.student_id = u.user_id
            WHERE s.assignment_id = %s
            ORDER BY s.submit_time DESC
        """
        return self.execute_query(query, (assignment_id,), fetch=True)
    
    def create_problem(self, problem_data):
        """创建新题目"""
        query = """
            INSERT INTO problems (
                problem_number, problem_title, problem_type, difficulty_level,
                description, reference_answer, max_score, creator_id,
                knowledge_points, attachments, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, problem_data)
    
    def create_assignment(self, assignment_data):
        """创建新作业"""
        query = """
            INSERT INTO assignments (
                assignment_number, assignment_title, assignment_description,
                course_name, teacher_id, total_score, publish_date, due_date,
                status, problem_ids
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, assignment_data)
    
    def create_submission(self, submission_data):
        """创建作业提交"""
        query = """
            INSERT INTO submissions (
                assignment_id, student_id, submission_content,
                submission_files, status
            ) VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, submission_data)
    
    def update_submission(self, submission_data, submission_id):
        """更新作业提交 ⭐
        
        Args:
            submission_data: tuple (submission_content, submission_files, status)
            submission_id: 提交记录的 ID
        """
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
    
    def update_submission_grade(self, submission_id, grade_data):
        """更新批改成绩"""
        query = """
            UPDATE submissions 
            SET auto_grade_score = %s, auto_grade_comments = %s,
                teacher_grade_score = %s, teacher_comments = %s,
                status = 'graded', graded_at = %s, graded_by = %s
            WHERE submission_id = %s
        """
        return self.execute_query(query, (*grade_data, submission_id))
    
    def get_knowledge_points(self):
        """获取所有知识点"""
        query = "SELECT * FROM knowledge_points ORDER BY kp_name"
        return self.execute_query(query, fetch=True)
    
    def insert_knowledge_point(self, kp_name, kp_description=None):
        """插入新知识点"""
        query = "INSERT INTO knowledge_points (kp_name, kp_description) VALUES (%s, %s)"
        return self.execute_query(query, (kp_name, kp_description))
    
    def get_student_statistics(self, student_id):
        """获取学生学习统计"""
        query = """
            SELECT * FROM student_statistics_view 
            WHERE user_id = %s
        """
        result = self.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None
    
    def get_graded_assignments(self, student_id):
        """获取已批改的作业"""
        query = """
            SELECT s.*, a.assignment_title, a.assignment_number, u.username as student_name
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            JOIN users u ON s.student_id = u.user_id
            WHERE s.student_id = %s AND s.status = 'graded'
            ORDER BY s.graded_at DESC
        """
        return self.execute_query(query, (student_id,), fetch=True)
    
    def get_teacher_graded_work(self, teacher_id):
        """获取教师批改后的作业"""
        query = """
            SELECT s.*, a.assignment_title, a.assignment_number, 
                   u.username as student_name
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.assignment_id
            JOIN users u ON s.student_id = u.user_id
            WHERE a.teacher_id = %s AND s.status = 'graded'
            ORDER BY s.graded_at DESC
        """
        return self.execute_query(query, (teacher_id,), fetch=True)
    
    def delete_assignment(self, assignment_id, teacher_id):
        """删除作业（只能删除自己创建的作业）
        
        Args:
            assignment_id: 作业ID
            teacher_id: 教师ID（用于验证权限）
            
        Returns:
            bool: 删除是否成功
        """
        # 先验证作业是否属于该教师
        check_query = "SELECT assignment_id FROM assignments WHERE assignment_id = %s AND teacher_id = %s"
        check_result = self.execute_query(check_query, (assignment_id, teacher_id), fetch=True)
        
        if not check_result:
            st.warning(f"⚠️ 作业不存在或无权删除")
            return False
        
        # 删除作业（由于设置了 ON DELETE CASCADE，相关的 submissions 和 grading_records 会自动删除）
        delete_query = "DELETE FROM assignments WHERE assignment_id = %s AND teacher_id = %s"
        result = self.execute_query(delete_query, (assignment_id, teacher_id))
        
        return bool(result)
    
    def update_assignment(self, update_data):
        """更新作业信息
        
        Args:
            update_data: tuple (title, description, course_name, total_score, due_date, assignment_id, teacher_id)
            
        Returns:
            bool: 更新是否成功
        """
        query = """
            UPDATE assignments 
            SET assignment_title = %s,
                assignment_description = %s,
                course_name = %s,
                total_score = %s,
                due_date = %s
            WHERE assignment_id = %s AND teacher_id = %s
        """
        return self.execute_query(query, update_data)


@st.cache_resource
def get_db_manager():
    """获取数据库管理器单例"""
    db = DatabaseManager()
    success = db.create_connection()
    
    if not success:
        st.error("""
        ### ❌ 数据库连接失败
        
        请检查以下配置：
        
        1. **MySQL 服务是否运行**
           - Windows: 运行 `net start MySQL80`
           - Linux: 运行 `sudo systemctl start mysql`
        
        2. **数据库配置文件**
           - 检查 `.streamlit/secrets.toml` 是否存在
           - 确认数据库连接信息正确
        
        3. **数据库是否已初始化**
           ```bash
           python utils/init_database.py
           ```
        
        配置完成后请刷新页面重试。
        """)
    
    return db


def hash_password(password):
    """简单的密码哈希（实际项目应使用 bcrypt）"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def check_session_state():
    """检查会话状态"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'role' not in st.session_state:
        st.session_state.role = None


def logout():
    """退出登录"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.role = None
    st.rerun()
