-- SciGrader 系统数据库架构设计
-- 用于连接教师端与学生端的数据关联

-- 创建数据库
CREATE DATABASE IF NOT EXISTS scigrader_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scigrader_db;

-- ===========================================
-- 删除现有表（如果存在）- 确保干净重建
-- ===========================================
-- 注意：这将删除所有现有数据！请谨慎使用！

DROP VIEW IF EXISTS student_statistics_view;
DROP VIEW IF EXISTS assignment_submission_view;
DROP TABLE IF EXISTS grading_records;
DROP TABLE IF EXISTS learning_statistics;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS assignments;
DROP TABLE IF EXISTS problems;
DROP TABLE IF EXISTS knowledge_points;
DROP TABLE IF EXISTS system_settings;
DROP TABLE IF EXISTS users;

-- ===========================================
-- 创建新表
-- ===========================================
-- 用户表（支持教师和学生两种角色）
CREATE TABLE users (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 知识点标签表
CREATE TABLE knowledge_points (
    kp_id INT AUTO_INCREMENT PRIMARY KEY,
    kp_name VARCHAR(100) NOT NULL UNIQUE,
    kp_description TEXT,
    parent_kp_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_kp_id) REFERENCES knowledge_points(kp_id) ON DELETE SET NULL,
    INDEX idx_name (kp_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 题目表（教师创建的题目）
CREATE TABLE problems (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 作业表（发布的作业任务）
CREATE TABLE assignments (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学生作业提交表
CREATE TABLE submissions (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 批改记录表（详细批改信息）
CREATE TABLE grading_records (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学习统计表（用于学生端统计）
CREATE TABLE learning_statistics (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 系统配置表
CREATE TABLE system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT,
    setting_description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT NULL,
    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入演示数据
-- 默认教师账号：admin / 123456
-- 默认学生账号：student1 / 123456, student2 / 123456
INSERT INTO users (username, password_hash, role, email) VALUES 
('admin', '123456', 'teacher', 'admin@scigrader.edu'),
('student1', '123456', 'student', 'student1@scigrader.edu'),
('student2', '123456', 'student', 'student2@scigrader.edu');

-- 插入知识点示例
INSERT INTO knowledge_points (kp_name, kp_description) VALUES
('线性代数', '矩阵、向量空间、线性变换等'),
('微积分', '极限、导数、积分等'),
('编程基础', '变量、循环、函数等基础概念'),
('数据结构', '数组、链表、树、图等');

-- 插入系统配置
INSERT INTO system_settings (setting_key, setting_value, setting_description) VALUES
('system_name', 'SciGrader', '系统名称'),
('max_file_size', '10485760', '最大上传文件大小（字节）'),
('allowed_extensions', '["pdf", "png", "jpg", "txt", "py", "java", "cpp"]', '允许的文件扩展名');

-- 创建视图：作业提交详情（用于双端显示）
CREATE VIEW assignment_submission_view AS
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
LEFT JOIN users u ON s.student_id = u.user_id;

-- 创建视图：学习统计视图
CREATE VIEW student_statistics_view AS
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
GROUP BY u.user_id, u.username;
