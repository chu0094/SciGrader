"""
SciGrader 数据库初始化脚本
用于快速创建数据库和插入演示数据
"""
import mysql.connector
from mysql.connector import Error
import hashlib


def hash_password(password):
    """简单的密码哈希（实际项目应使用 bcrypt）"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_database():
    """创建数据库"""
    try:
        # 连接到 MySQL 服务器（不指定数据库）
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456'
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute("""
            CREATE DATABASE IF NOT EXISTS scigrader_db 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
        
        print("✓ 数据库创建成功")
        
        # 使用该数据库
        cursor.execute("USE scigrader_db")
        
        return connection, cursor
        
    except Error as e:
        print(f"✗ 数据库创建失败：{e}")
        return None, None


def create_tables(connection, cursor):
    """创建数据表"""
    
    tables = [
        # 用户表
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('teacher', 'student') NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_username (username),
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 知识点标签表
        """
        CREATE TABLE IF NOT EXISTS knowledge_points (
            kp_id INT AUTO_INCREMENT PRIMARY KEY,
            kp_name VARCHAR(100) NOT NULL UNIQUE,
            kp_description TEXT,
            parent_kp_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_kp_id) REFERENCES knowledge_points(kp_id) ON DELETE SET NULL,
            INDEX idx_name (kp_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 题目表
        """
        CREATE TABLE IF NOT EXISTS problems (
            problem_id INT AUTO_INCREMENT PRIMARY KEY,
            problem_number VARCHAR(20) NOT NULL,
            problem_title VARCHAR(200) NOT NULL,
            problem_type ENUM('concept', 'calculation', 'programming') NOT NULL,
            difficulty_level ENUM('easy', 'medium', 'hard') NOT NULL,
            description TEXT NOT NULL,
            reference_answer TEXT,
            max_score INT NOT NULL,
            creator_id INT NOT NULL,
            knowledge_points JSON,
            attachments JSON,
            status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_problem_number (problem_number),
            INDEX idx_type (problem_type),
            INDEX idx_difficulty (difficulty_level),
            INDEX idx_status (status),
            INDEX idx_creator (creator_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 作业表
        """
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id INT AUTO_INCREMENT PRIMARY KEY,
            assignment_number VARCHAR(20) NOT NULL,
            assignment_title VARCHAR(200) NOT NULL,
            assignment_description TEXT,
            course_name VARCHAR(100),
            teacher_id INT NOT NULL,
            total_score INT NOT NULL,
            publish_date DATE NOT NULL,
            due_date DATE NOT NULL,
            status ENUM('draft', 'active', 'closed', 'graded') DEFAULT 'active',
            problem_ids JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_assignment_number (assignment_number),
            INDEX idx_teacher (teacher_id),
            INDEX idx_status (status),
            INDEX idx_due_date (due_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 学生作业提交表
        """
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id INT AUTO_INCREMENT PRIMARY KEY,
            assignment_id INT NOT NULL,
            student_id INT NOT NULL,
            submission_content TEXT NOT NULL,
            submission_files JSON,
            submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('submitted', 'late', 'graded', 'returned') DEFAULT 'submitted',
            auto_grade_score DECIMAL(5,2),
            auto_grade_comments TEXT,
            teacher_grade_score DECIMAL(5,2),
            teacher_comments TEXT,
            graded_at TIMESTAMP NULL,
            graded_by INT NULL,
            FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (graded_by) REFERENCES users(user_id) ON DELETE SET NULL,
            INDEX idx_assignment (assignment_id),
            INDEX idx_student (student_id),
            INDEX idx_status (status),
            INDEX idx_submit_time (submit_time),
            UNIQUE KEY unique_submission (assignment_id, student_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 批改记录表
        """
        CREATE TABLE IF NOT EXISTS grading_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            submission_id INT NOT NULL,
            problem_id INT,
            score DECIMAL(5,2),
            comments TEXT,
            grading_details JSON,
            graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            graded_by INT NOT NULL,
            grading_type ENUM('auto', 'manual', 'hybrid') NOT NULL,
            FOREIGN KEY (submission_id) REFERENCES submissions(submission_id) ON DELETE CASCADE,
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE SET NULL,
            FOREIGN KEY (graded_by) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_submission (submission_id),
            INDEX idx_graded_by (graded_by)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 学习统计表
        """
        CREATE TABLE IF NOT EXISTS learning_statistics (
            stat_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            total_assignments INT DEFAULT 0,
            completed_assignments INT DEFAULT 0,
            pending_assignments INT DEFAULT 0,
            overdue_assignments INT DEFAULT 0,
            average_score DECIMAL(5,2),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_student (student_id),
            INDEX idx_student (student_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """,
        
        # 系统配置表
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key VARCHAR(100) PRIMARY KEY,
            setting_value TEXT,
            setting_description VARCHAR(255),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            updated_by INT NULL,
            FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    ]
    
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            print(f"✓ 数据表创建成功")
        except Error as e:
            print(f"✗ 创建数据表失败：{e}")
            return False
    
    return True


def insert_demo_data(connection, cursor):
    """插入演示数据"""
    
    # 插入用户（密码都是 123456）
    password_hash = hash_password('123456')
    
    users = [
        ('admin', password_hash, 'teacher', 'admin@scigrader.edu'),
        ('student1', password_hash, 'student', 'student1@scigrader.edu'),
        ('student2', password_hash, 'student', 'student2@scigrader.edu')
    ]
    
    cursor.executemany("""
        INSERT INTO users (username, password_hash, role, email) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE username=username
    """, users)
    
    print("✓ 用户数据插入成功")
    
    # 插入知识点
    knowledge_points = [
        ('线性代数', '矩阵、向量空间、线性变换等'),
        ('微积分', '极限、导数、积分等'),
        ('编程基础', '变量、循环、函数等基础概念'),
        ('数据结构', '数组、链表、树、图等')
    ]
    
    cursor.executemany("""
        INSERT INTO knowledge_points (kp_name, kp_description) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE kp_name=kp_name
    """, knowledge_points)
    
    print("✓ 知识点数据插入成功")
    
    # 插入系统配置
    settings = [
        ('system_name', 'SciGrader', '系统名称'),
        ('max_file_size', '10485760', '最大上传文件大小（字节）'),
        ('allowed_extensions', '["pdf", "png", "jpg", "txt", "py", "java", "cpp"]', '允许的文件扩展名')
    ]
    
    cursor.executemany("""
        INSERT INTO system_settings (setting_key, setting_value, setting_description) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE setting_key=setting_key
    """, settings)
    
    print("✓ 系统配置插入成功")
    
    # 提交事务
    connection.commit()
    print("\n✅ 所有演示数据插入成功！")


def create_views(cursor):
    """创建视图"""
    
    views = [
        # 作业提交详情视图
        """
        CREATE OR REPLACE VIEW assignment_submission_view AS
        SELECT 
            a.assignment_id,
            a.assignment_number,
            a.assignment_title,
            a.course_name,
            a.total_score,
            a.due_date,
            a.status as assignment_status,
            s.submission_id,
            s.student_id,
            u.username as student_name,
            s.submission_content,
            s.submit_time,
            s.status as submission_status,
            s.auto_grade_score,
            s.auto_grade_comments,
            s.teacher_grade_score,
            s.teacher_comments,
            s.graded_at
        FROM assignments a
        LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
        LEFT JOIN users u ON s.student_id = u.user_id
        """,
        
        # 学生学习统计视图
        """
        CREATE OR REPLACE VIEW student_statistics_view AS
        SELECT 
            u.user_id,
            u.username,
            COUNT(DISTINCT a.assignment_id) as total_assignments,
            COUNT(DISTINCT CASE WHEN s.status IN ('graded', 'submitted') THEN s.submission_id END) as completed_assignments,
            COUNT(DISTINCT CASE WHEN s.status = 'submitted' AND s.submit_time < a.due_date THEN s.submission_id END) as pending_assignments,
            COUNT(DISTINCT CASE WHEN s.status = 'late' OR (s.submit_time > a.due_date AND s.status != 'graded') THEN s.submission_id END) as overdue_assignments,
            AVG(s.auto_grade_score) as average_score
        FROM users u
        LEFT JOIN submissions s ON u.user_id = s.student_id
        LEFT JOIN assignments a ON s.assignment_id = a.assignment_id
        WHERE u.role = 'student'
        GROUP BY u.user_id, u.username
        """
    ]
    
    for view_sql in views:
        try:
            cursor.execute(view_sql)
            print(f"✓ 视图创建成功")
        except Error as e:
            print(f"✗ 创建视图失败：{e}")


def main():
    """主函数"""
    print("=" * 50)
    print("  SciGrader 数据库初始化工具")
    print("=" * 50)
    print()
    
    # 创建数据库
    connection, cursor = create_database()
    
    if not connection:
        print("\n❌ 初始化失败，请检查 MySQL 服务是否运行")
        return
    
    try:
        # 切换到新数据库
        cursor.execute("USE scigrader_db")
        
        # 创建表
        print("\n[1/3] 创建数据表...")
        if not create_tables(connection, cursor):
            print("创建表失败")
            return
        print("✓ 所有数据表创建完成")
        
        # 创建视图
        print("\n[2/3] 创建视图...")
        create_views(cursor)
        print("✓ 所有视图创建完成")
        
        # 插入演示数据
        print("\n[3/3] 插入演示数据...")
        insert_demo_data(connection, cursor)
        
        print("\n" + "=" * 50)
        print("  ✅ 数据库初始化完成！")
        print("=" * 50)
        print("\n演示账号信息：")
        print("  👨‍🏫 教师端：admin / 123456")
        print("  👨‍🎓 学生端：student1 / 123456")
        print("\n可以开始使用系统了！")
        
    except Error as e:
        print(f"\n❌ 初始化过程中发生错误：{e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
