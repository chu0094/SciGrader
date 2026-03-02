"""
SmarTAI学生端 - 任务列表界面
简洁的任务导向设计，提供作业提交和进度跟踪功能
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import time
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import *

# 页面配置
st.set_page_config(
    page_title="SmarTAI -学任务中心",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 加载深色主题CSS
def load_dark_theme():
    css_files = [
        'frontend/static/dark_theme.css',
        'frontend/static/glassmorphism.css', 
        'frontend/static/neon_effects.css'
    ]
    
    css_content = ""
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content += f.read() + "\n"
    
    return css_content

# 自定义CSS样式
st.markdown(f"""
<style>
{load_dark_theme()}

/*隐藏Streamlit默认元素 */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* 主容器样式 */
.main {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%) !important;
    padding: 0;
    min-height: 100vh;
}}

/*动态背景效果 */
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
}}

/*学生端容器 */
.student-container {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}}

/*头部区域 */
.student-header {{
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    padding: 1.5rem 2rem;
    margin-bottom: 2rem;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}}

.header-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.user-info {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
}}

.avatar-section {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.user-avatar {{
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(45deg, #8B5CF6, #00D4FF);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 1.5rem;
    border: 3px solid rgba(139, 92, 246, 0.3);
    box-shadow: 0 0 25px rgba(139, 92, 246, 0.4);
}}

.user-details {{
    color: #F1F5F9;
}}

.user-name {{
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}}

.user-class {{
    color: #94A3B8;
    font-size: 1rem;
}}

.status-indicators {{
    display: flex;
    gap: 2rem;
}}

.status-item {{
    text-align: center;
}}

.status-value {{
    color: #8B5CF6;
    font-size: 1.5rem;
    font-weight: 700;
    text-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
}}

.status-label {{
    color: #94A3B8;
    font-size: 0.9rem;
}}

/*任务区域标题 */
.tasks-section-title {{
    font-size: 2.2rem;
    font-weight: 800;
    color: #F1F5F9;
    margin: 2rem 0 1.5rem 0;
    text-align: center;
    background: linear-gradient(135deg, #8B5CF6, #00D4FF, #00F5D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}}

/*任务卡片网格 */
.tasks-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

/*任务卡片 */
.task-card {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.task-card:hover {{
    transform: translateY(-8px);
    border-color: rgba(139, 92, 246, 0.4);
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4);
}}

.task-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #8B5CF6, #00D4FF);
}}

.task-card.completed::before {{
    background: linear-gradient(90deg, #10B981, #34D399);
}}

.task-card.pending::before {{
    background: linear-gradient(90deg, #F59E0B, #FBBF24);
}}

.task-card.overdue::before {{
    background: linear-gradient(90deg, #EF4444, #F87171);
}}

/*任务头部信息 */
.task-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
}}

.task-title {{
    color: #F1F5F9;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}}

.task-course {{
    color: #94A3B8;
    font-size: 1rem;
}}

.task-status-badge {{
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
}}

.status-completed {{
    background: rgba(16, 185, 129, 0.2);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}}

.status-pending {{
    background: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.3);
}}

.status-overdue {{
    background: rgba(239, 68, 68, 0.2);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}}

/*任务详情 */
.task-details {{
    margin: 1.5rem 0;
}}

.detail-item {{
    display: flex;
    justify-content: space-between;
    margin: 0.8rem 0;
    color: #CBD5E1;
    font-size: 0.95rem;
}}

.detail-label {{
    color: #94A3B8;
}}

.detail-value {{
    font-weight: 500;
}}

/*进度条 */
.task-progress {{
    margin: 1.5rem 0;
}}

.progress-label {{
    display: flex;
    justify-content: space-between;
    color: #94A3B8;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}}

.progress-bar-container {{
    height: 12px;
    background: rgba(30, 41, 59, 0.5);
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid rgba(139, 92, 246, 0.2);
}}

.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #8B5CF6, #00D4FF);
    border-radius: 6px;
    transition: width 0.5s ease;
    position: relative;
}}

.progress-bar::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: progress-shine 2s infinite;
}}

@keyframes progress-shine {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}

/*操作按钮 */
.task-actions {{
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}}

.action-btn {{
    flex: 1;
    padding: 0.8rem;
    border-radius: 12px;
    font-weight: 600;
    text-align: center;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}}

.btn-primary {{
    background: linear-gradient(135deg, #8B5CF6, #00D4FF);
    color: #0F172A;
}}

.btn-secondary {{
    background: rgba(148, 163, 184, 0.2);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 0.3);
}}

.btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
}}

.btn-secondary:hover {{
    background: rgba(148, 163, 184, 0.3);
}}

/*快速上传区域 */
.quick-upload {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    text-align: center;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
}}

.upload-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #8B5CF6, #00D4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.upload-desc {{
    color: #94A3B8;
    font-size: 1.1rem;
    margin-bottom: 2rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}}

/*通知面板 */
.notifications-panel {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 2rem 0;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}}

.notifications-title {{
    color: #F1F5F9;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1rem;
    text-align: center;
}}

.notification-item {{
    background: rgba(15, 23, 42, 0.6);
    border-left: 3px solid #8B5CF6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}}

.notification-content {{
    color: #CBD5E1;
    font-size: 0.95rem;
    line-height: 1.4;
}}

.notification-time {{
    color: #64748B;
    font-size: 0.8rem;
    margin-top: 0.3rem;
}}

/*统计卡片 */
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

.stat-card {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}}

.stat-card:hover {{
    transform: translateY(-5px);
    border-color: rgba(139, 92, 246, 0.3);
}}

.stat-icon {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #8B5CF6;
    filter: drop-shadow(0 0 15px rgba(139, 92, 246, 0.3));
}}

.stat-value {{
    color: #8B5CF6;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
}}

.stat-label {{
    color: #94A3B8;
    font-size: 1rem;
    margin-top: 0.5rem;
}}

/*响应式设计 */
@media (max-width: 768px) {{
    .student-container {{
        padding: 1rem;
    }}
    
    .header-content {{
        flex-direction: column;
        gap: 1.5rem;
    }}
    
    .status-indicators {{
        gap: 1rem;
    }}
    
    .tasks-grid {{
        grid-template-columns: 1fr;
        gap: 1rem;
    }}
    
    .task-actions {{
        flex-direction: column;
    }}
    
    .stats-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 480px) {{
    .user-name {{
        font-size: 1.2rem;
    }}
    
    .user-avatar {{
        width: 50px;
        height: 50px;
        font-size: 1.2rem;
    }}
    
    .task-title {{
        font-size: 1.2rem;
    }}
    
    .stat-value {{
        font-size: 1.6rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

def load_mock_assignments():
    """加载模拟作业数据"""
    return [
        {
            "id": "hw001",
            "title": "数据结构期中考试",
            "course": "数据结构与算法",
            "status": "completed",
            "deadline": datetime.now() - timedelta(days=2),
            "submitted_date": datetime.now() - timedelta(days=3),
            "score": 88,
            "max_score": 100,
            "progress": 100,
            "feedback": "整体表现良好，建议加强对树结构的理解"
        },
        {
            "id": "hw002",
            "title": "算法设计作业",
            "course": "算法分析与设计",
            "status": "pending",
            "deadline": datetime.now() + timedelta(days=3),
            "progress": 65,
            "requirements": "完成第3-5章的编程题"
        },
        {
            "id": "hw003",
            "title": "操作系统实验报告",
            "course": "计算机操作系统",
            "status": "pending",
            "deadline": datetime.now() + timedelta(days=7),
            "progress": 30,
            "requirements": "完成进程调度算法实验"
        },
        {
            "id": "hw004",
            "title": "数据库课程设计",
            "course": "数据库系统原理",
            "status": "overdue",
            "deadline": datetime.now() - timedelta(days=1),
            "progress": 0,
            "requirements": "提交ER图和关系模式设计"
        }
    ]

def render_student_header():
    """渲染学生端头部信息"""
    st.markdown("""
    <div class="student-header">
        <div class="header-content">
            <div class="user-info">
                <div class="avatar-section">
                    <div class="user-avatar">李</div>
                    <div class="user-details">
                        <div class="user-name">李明同学</div>
                        <div class="user-class">计算机科学与技术 2022级</div>
                    </div>
                </div>
            </div>
            <div class="status-indicators">
                <div class="status-item">
                    <div class="status-value">4</div>
                    <div class="status-label">总任务</div>
                </div>
                <div class="status-item">
                    <div class="status-value">1</div>
                    <div class="status-label">已完成</div>
                </div>
                <div class="status-item">
                    <div class="status-value">2</div>
                    <div class="status-label">进行中</div>
                </div>
                <div class="status-item">
                    <div class="status-value">1</div>
                    <div class="status-label">已逾期</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_statistics():
    """渲染统计信息"""
    st.markdown('<div class="tasks-section-title">📊学统计</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">📚</div>
            <div class="stat-value">12</div>
            <div class="stat-label">总作业数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value">8</div>
            <div class="stat-label">已完成</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-value">85</div>
            <div class="stat-label">平均分</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <div class="stat-value">3</div>
            <div class="stat-label">优秀次数</div>
        </div>
        """, unsafe_allow_html=True)

def render_task_card(task):
    """渲染任务卡片"""
    status_class = task["status"]
    status_text = {
        "completed": "已完成",
        "pending": "进行中", 
        "overdue": "已逾期"
    }[task["status"]]
    
    status_badge_class = {
        "completed": "status-completed",
        "pending": "status-pending",
        "overdue": "status-overdue"
    }[task["status"]]
    
    st.markdown(f"""
    <div class="task-card {status_class}">
        <div class="task-header">
            <div>
                <div class="task-title">{task['title']}</div>
                <div class="task-course">{task['course']}</div>
            </div>
            <div class="task-status-badge {status_badge_class}">
                {status_text}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    #任务详情
    st.markdown('<div class="task-details">', unsafe_allow_html=True)
    
    if task["status"] == "completed":
        st.markdown(f"""
        <div class="detail-item">
            <span class="detail-label">提交时间:</span>
            <span class="detail-value">{task['submitted_date'].strftime('%Y-%m-%d %H:%M')}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">得分:</span>
            <span class="detail-value">{task['score']}/{task['max_score']}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">截止时间:</span>
            <span class="detail-value">{task['deadline'].strftime('%Y-%m-%d')}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="detail-item">
            <span class="detail-label">截止时间:</span>
            <span class="detail-value">{task['deadline'].strftime('%Y-%m-%d')}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">要求:</span>
            <span class="detail-value">{task.get('requirements', '无特殊要求')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    #进条
    if task["status"] != "completed":
        st.markdown(f"""
        <div class="task-progress">
            <div class="progress-label">
                <span>完成进度</span>
                <span>{task['progress']}%</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {task['progress']}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 操作按钮
    st.markdown('<div class="task-actions">', unsafe_allow_html=True)
    
    if task["status"] == "completed":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("查看反馈", key=f"feedback_{task['id']}", use_container_width=True):
                st.info(f"查看 {task['title']} 的详细反馈")
        with col2:
            if st.button("重新提交", key=f"resubmit_{task['id']}", use_container_width=True):
                st.info(f"重新提交 {task['title']}")
    elif task["status"] == "pending":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("开始作业", key=f"start_{task['id']}", use_container_width=True):
                st.info(f"开始 {task['title']}")
        with col2:
            if st.button("查看详情", key=f"detail_{task['id']}", use_container_width=True):
                st.info(f"查看 {task['title']} 详细要求")
    else:  # overdue
        if st.button("立即提交", key=f"submit_{task['id']}", use_container_width=True):
            st.info(f"提交逾期的 {task['title']}")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def render_task_list():
    """渲染任务列表"""
    st.markdown('<div class="tasks-section-title">📋我的任务</div>', unsafe_allow_html=True)
    
    assignments = load_mock_assignments()
    
    #按状态分组显示
    completed_tasks = [task for task in assignments if task["status"] == "completed"]
    pending_tasks = [task for task in assignments if task["status"] == "pending"]
    overdue_tasks = [task for task in assignments if task["status"] == "overdue"]
    
    #显示任务
    if overdue_tasks:
        st.markdown("### ⚠️ 逾期任务", unsafe_allow_html=True)
        for task in overdue_tasks:
            render_task_card(task)
    
    if pending_tasks:
        st.markdown("###📝进中的任务", unsafe_allow_html=True)
        for task in pending_tasks:
            render_task_card(task)
    
    if completed_tasks:
        st.markdown("###✅已完成的任务", unsafe_allow_html=True)
        for task in completed_tasks:
            render_task_card(task)

def render_quick_upload():
    """渲染快速上传区域"""
    st.markdown("""
    <div class="quick-upload">
        <div class="upload-title">📤快提交作业</div>
        <div class="upload-desc">
           拖或选择文件快速提交当前作业，支持多种文件格式
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 文件上传组件
    uploaded_file = st.file_uploader(
        "选择要提交的文件",
        type=["pdf", "docx", "txt", "zip", "py", "java"],
        key="quick_upload",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.success(f"✅ 文件已选择: {uploaded_file.name}")
        if st.button("确认提交", type="primary", use_container_width=True):
            st.success("🎉 作业提交成功！")

def render_notifications():
    """渲染通知面板"""
    st.markdown("""
    <div class="notifications-panel">
        <div class="notifications-title">🔔 最新通知</div>
    """, unsafe_allow_html=True)
    
    notifications = [
        {
            "content": "数据结构期中考试批改完成，得分88分",
            "time": "2小时前"
        },
        {
            "content": "算法设计作业截止时间延长至本周五",
            "time": "1天前"
        },
        {
            "content": "操作系统实验报告新增提交要求",
            "time": "2天前"
        }
    ]
    
    for notif in notifications:
        st.markdown(f"""
        <div class="notification-item">
            <div class="notification-content">{notif['content']}</div>
            <div class="notification-time">{notif['time']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """主函数"""
    # 初始化会话状态
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # 如果未登录，重定向到登录页面
    if not st.session_state.logged_in:
        st.switch_page("pages/login.py")
        return
    
    # 主容器
    st.markdown('<div class="student-container">', unsafe_allow_html=True)
    
    #渲各部分
    render_student_header()
    render_statistics()
    render_task_list()
    
    # 侧边栏布局
    col1, col2 = st.columns([3, 1])
    with col1:
        render_quick_upload()
    with col2:
        render_notifications()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()