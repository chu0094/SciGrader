# SciGrader 项目架构文档

## 📋 项目概述

SciGrader 是一个基于 Streamlit 和 MySQL 的理工科 AI 作业批改系统前端界面。系统采用现代化的教育平台设计风格，提供教师端和学生端两个角色，实现作业发布、提交、自动批改等核心功能。

## 🏗️ 系统架构

### 技术栈

```
┌─────────────────────────────────────┐
│     前端展示层 (Streamlit)          │
│  - 登录页面                         │
│  - 教师端 Dashboard                  │
│  - 学生端 Dashboard                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     业务逻辑层 (Python)             │
│  - 数据库管理器                     │
│  - 通用组件库                       │
│  - 工具函数                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     数据存储层 (MySQL 8.0+)         │
│  - 用户表                           │
│  - 题目表                           │
│  - 作业表                           │
│  - 提交记录表                       │
│  - 批改记录表                       │
└─────────────────────────────────────┘
```

## 📁 项目结构

```
frontend/
├── .streamlit/
│   ├── config.toml          # Streamlit 配置
│   └── secrets.toml         # 敏感信息（数据库连接）
├── components/
│   ├── __init__.py          # 组件包导出
│   └── common_components.py # 通用 UI 组件
├── pages/
│   ├── login.py             # 登录页面
│   ├── teacher_dashboard.py # 教师端仪表盘
│   └── student_dashboard.py # 学生端仪表盘
├── utils/
│   ├── __init__.py          # 工具包导出
│   ├── db_utils.py          # 数据库操作
│   └── init_database.py     # 数据库初始化脚本
├── static/
│   └── styles.css           # 自定义样式表
├── app.py                   # 主应用入口
├── start.bat                # Windows 启动脚本
├── requirements.txt         # Python 依赖
├── test_db_connection.py    # 数据库测试工具
├── README.md                # 项目说明
└── QUICKSTART.md            # 快速开始指南
```

## 🔑 核心功能模块

### 1. 用户认证模块

**文件：** `pages/login.py`

**功能：**
- 角色切换（教师/学生）
- 用户名密码验证
- Session 状态管理
- 演示账号提示

**关键函数：**
```python
def login_page():              # 渲染登录页面
def handle_login():            # 处理登录逻辑
def logout():                  # 退出登录
```

### 2. 教师端模块

**文件：** `pages/teacher_dashboard.py`

**功能：**
- 题目管理（CRUD）
- 作业发布
- 查看提交情况
- 批改结果查看

**主要组件：**
```python
render_create_problem_section()      # 创建题目表单
render_published_assignments_section() # 已发布作业列表
render_graded_work_section()          # 批改后作业
render_right_panel()                  # 快捷操作面板
```

### 3. 学生端模块

**文件：** `pages/student_dashboard.py`

**功能：**
- 查看作业列表
- 提交作业
- 查看批改结果
- 学习统计面板

**主要组件：**
```python
render_my_assignments_section()         # 我的作业
render_student_assignment_card()        # 作业卡片
render_graded_assignments_section()     # 批改后作业
render_right_panel()                    # 学习统计
```

### 4. 数据库模块

**文件：** `utils/db_utils.py`

**功能：**
- 数据库连接管理
- SQL 查询执行
- 用户验证
- 数据 CRUD 操作

**核心类：**
```python
class DatabaseManager:
    def create_connection()
    def execute_query()
    def verify_user()
    def create_problem()
    def create_assignment()
    def create_submission()
```

### 5. UI 组件模块

**文件：** `components/common_components.py`

**功能：**
- 消息提示组件
- 卡片渲染组件
- 统计卡片组件
- 文件上传组件

## 🗄️ 数据库设计

### 核心表关系

```
users (用户表)
  ├─ creator_id → problems.creator_id
  ├─ teacher_id → assignments.teacher_id
  ├─ student_id → submissions.student_id
  └─ graded_by → grading_records.graded_by

problems (题目表)
  └─ problem_ids → assignments.problem_ids (JSON)

assignments (作业表)
  └─ assignment_id → submissions.assignment_id

submissions (提交表)
  ├─ submission_id → grading_records.submission_id
  └─ student_id → users.user_id

grading_records (批改记录表)
  ├─ submission_id → submissions.submission_id
  └─ problem_id → problems.problem_id
```

### 视图设计

**assignment_submission_view:**
- 联合作业和提交表
- 用于双端显示作业详情

**student_statistics_view:**
- 自动统计学生作业情况
- 实时更新统计数据

## 🎨 UI 设计规范

### 配色方案

```css
/* 主色调 */
Primary Green: #2E7D32
Dark Green: #1B5E20
Light Green: #E8F5E9

/* 登录页渐变 */
Purple Gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)

/* 状态色 */
Pending: #FFA000 (黄色)
Submitted: #2E7D32 (绿色)
Overdue: #D32F2F (红色)

/* 背景色 */
Background: #F5F5F5
Card Background: #FFFFFF
Text Color: #212121
```

### 组件样式

**卡片组件：**
- 圆角：12px
- 阴影：0 2px 8px rgba(0,0,0,0.08)
- 悬停效果：transform translateY(-2px)

**按钮：**
- 圆角：8px
- 过渡动画：0.3s cubic-bezier(0.4, 0, 0.2, 1)
- 悬停阴影：0 4px 12px rgba()

### 响应式设计

```css
/* 桌面端 */
.main-content {
  grid-template-columns: 70% 30%;
}

/* 平板端 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

/* 移动端 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
```

## 🔐 安全机制

### 会话管理
- Streamlit session_state 存储登录状态
- 退出时清除所有会话数据
- 基于角色的访问控制

### 密码安全
- 当前使用 SHA-256 哈希（演示）
- **生产环境需升级为 bcrypt**

### SQL 注入防护
- 使用参数化查询
- 所有输入参数绑定

## 🚀 部署流程

### 本地开发
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python utils/init_database.py

# 3. 启动应用
streamlit run app.py
```

### 生产环境

**要求：**
- Python 3.8+
- MySQL 8.0+
- Nginx（反向代理）
- Supervisor（进程管理）

**步骤：**
1. 配置 MySQL 远程访问
2. 修改 secrets.toml 数据库配置
3. 使用 Gunicorn 运行 Streamlit
4. 配置 Nginx SSL 证书

## 📊 性能优化

### 数据库优化
- 为常用查询字段添加索引
- 使用视图简化复杂查询
- JSON 字段存储非结构化数据

### 前端优化
- Streamlit 缓存机制 (@st.cache_resource)
- 按需加载数据
- 减少重复渲染

### 建议的优化方向
- 添加 Redis 缓存层
- 实现分页加载
- 异步处理文件上传

## 🔄 扩展性设计

### 模块化设计
- 各功能模块独立
- 清晰的接口定义
- 易于添加新功能

### 可扩展的数据模型
- JSON 字段支持灵活数据结构
- 外键约束保证数据完整性
- 视图抽象便于查询扩展

### API 预留
- 后端服务接口预留
- AI 评分模块接口
- 批量导入导出接口

## 📝 开发规范

### 代码风格
- PEP 8 规范
- 类型注解（Type Hints）
- 详细的文档字符串

### 命名规范
- 变量：snake_case
- 函数：snake_case
- 类：PascalCase
- 常量：UPPER_CASE

### Git 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 🧪 测试策略

### 单元测试
- 数据库连接测试
- 工具函数测试
- 组件渲染测试

### 集成测试
- 登录流程测试
- 作业提交流程测试
- 批改流程测试

### E2E 测试
- 完整用户旅程测试
- 多角色交互测试

## 📖 相关资源

- [Streamlit 官方文档](https://docs.streamlit.io/)
- [MySQL 8.0 文档](https://dev.mysql.com/doc/refman/8.0/en/)
- [Python 最佳实践](https://docs.python-guide.org/)

---

**版本：** 1.0.0  
**最后更新：** 2026 年 3 月 11 日  
**维护者：** SciGrader Team
