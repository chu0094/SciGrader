"""
SmarTAI项目 -风主应用入口文件
智能评估平台的主界面，提供导航和核心功能入口
采用深色科技风设计，融合AI控制台和数据分析平台风格
"""
import streamlit as st
import sys
import os
import json
import requests
from datetime import datetime
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from utils.py (the file, not the folder)
from utils import *
# Import from frontend_utils (the folder we renamed)
from frontend_utils.data_loader import load_ai_grading_data, StudentScore, QuestionAnalysis, AssignmentStats
from frontend_utils.chart_components import create_score_distribution_chart, create_grade_pie_chart

# Get backend URL - from environment variable or hardcoded default
BACKEND_URL = os.environ.get("BACKEND_URL", UTILS_BACKEND_URL)

# 页面配置
st.set_page_config(
    page_title="SmarTAI - Intelligent Assessment Platform",
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

/* 主导航栏 */
.dashboard-header {{
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}}

.header-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
}}

.logo-section {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.logo-icon {{
    font-size: 2.5rem;
    color: #00D4FF;
    filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.5));
}}

.logo-text {{
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.user-section {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
}}

.user-info {{
    text-align: right;
}}

.user-name {{
    color: #F1F5F9;
    font-weight: 600;
    font-size: 1.1rem;
}}

.user-role {{
    color: #94A3B8;
    font-size: 0.9rem;
}}

.user-avatar {{
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: linear-gradient(45deg, #00D4FF, #8B5CF6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 1.2rem;
    border: 2px solid rgba(0, 212, 255, 0.3);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}}

/* 主内容区域 */
.main-content {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}}

/*仪表板网格布局 */
.dashboard-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

/*状态卡片 */
.status-card {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}}

.status-card:hover {{
    transform: translateY(-5px);
    border-color: rgba(0, 212, 255, 0.4);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}}

.status-title {{
    color: #94A3B8;
    font-size: 1rem;
    margin-bottom: 0.5rem;
    font-weight: 500;
}}

.status-value {{
    color: #00D4FF;
    font-size: 2rem;
    font-weight: 700;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
}}

.status-trend {{
    color: #10B981;
    font-size: 0.9rem;
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}}

/*快速操作区域 */
.quick-actions {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
    margin: 2rem 0;
}}

.quick-actions-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1.5rem;
    text-align: center;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.actions-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}}

.action-card {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    backdrop-filter: blur(10px);
}}

.action-card:hover {{
    transform: translateY(-8px);
    border-color: rgba(0, 212, 255, 0.4);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
    background: rgba(0, 212, 255, 0.1);
}}

.action-icon {{
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #00D4FF;
    filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.4));
}}

.action-title {{
    font-size: 1.2rem;
    font-weight: 600;
    color: #F1F5F9;
    margin-bottom: 0.5rem;
}}

.action-desc {{
    color: #94A3B8;
    font-size: 0.95rem;
    line-height: 1.5;
}}

/*数据可视化区域 */
.visualization-section {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
    margin: 2rem 0;
}}

.visualization-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1.5rem;
    text-align: center;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}}

.chart-container {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
}}

.chart-title {{
    color: #F1F5F9;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    text-align: center;
}}

/* AI任务中心 */
.ai-center {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2rem;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
    margin: 2rem 0;
}}

.ai-center-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1.5rem;
    text-align: center;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.tasks-list {{
    display: grid;
    gap: 1rem;
}}

.task-item {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 12px;
    padding: 1.2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}}

.task-item:hover {{
    background: rgba(0, 212, 255, 0.1);
    border-color: rgba(0, 212, 255, 0.3);
}}

.task-info {{
    flex: 1;
}}

.task-name {{
    color: #F1F5F9;
    font-weight: 600;
    margin-bottom: 0.3rem;
}}

.task-status {{
    color: #94A3B8;
    font-size: 0.9rem;
}}

.task-progress {{
    width: 120px;
    height: 8px;
    background: rgba(30, 41, 59, 0.5);
    border-radius: 4px;
    overflow: hidden;
}}

.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #00D4FF, #00F5D4);
    border-radius: 4px;
    transition: width 0.3s ease;
}}

/*通知面板 */
.notifications-panel {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(15px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}}

.notifications-title {{
    color: #F1F5F9;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
}}

.notification-item {{
    background: rgba(15, 23, 42, 0.6);
    border-left: 3px solid #00D4FF;
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

/*响应式设计 */
@media (max-width: 768px) {{
    .header-content {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .dashboard-grid {{
        grid-template-columns: 1fr;
        gap: 1rem;
    }}
    
    .actions-grid {{
        grid-template-columns: 1fr;
    }}
    
    .charts-grid {{
        grid-template-columns: 1fr;
    }}
    
    .main-content {{
        padding: 1rem;
    }}
}}

@media (max-width: 480px) {{
    .logo-text {{
        font-size: 1.4rem;
    }}
    
    .user-name {{
        font-size: 1rem;
    }}
    
    .status-value {{
        font-size: 1.6rem;
    }}
    
    .action-icon {{
        font-size: 2.5rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

def load_mock_data():
    """Load mock data for testing when real data is not available"""
    try:
        # Try to load from root directory first (where the file actually is)
        mock_data_path = os.path.join(os.path.dirname(__file__), "..", "mock_data.json")
        if not os.path.exists(mock_data_path):
            # Fallback to frontend directory
            mock_data_path = os.path.join(os.path.dirname(__file__), "mock_data.json")
        
        with open(mock_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Convert string dates back to datetime objects
        for student in data["student_scores"]:
            if isinstance(student["submit_time"], str):
                student["submit_time"] = datetime.fromisoformat(student["submit_time"])
        
        if isinstance(data["assignment_stats"]["create_time"], str):
            data["assignment_stats"]["create_time"] = datetime.fromisoformat(data["assignment_stats"]["create_time"])
        
        # Convert to proper dataclass objects
        student_scores = []
        for student_data in data["student_scores"]:
            student_scores.append(StudentScore(**student_data))
        
        question_analysis = []
        for question_data in data["question_analysis"]:
            question_analysis.append(QuestionAnalysis(**question_data))
        
        assignment_stats = AssignmentStats(**data["assignment_stats"])
        
        return {
            "student_scores": student_scores,
            "question_analysis": question_analysis,
            "assignment_stats": assignment_stats
        }
    except Exception as e:
        st.error(f"Failed to load mock data: {str(e)}")
        return None

def init_session_state():
    """初始化会话状态"""
    # Initialize session state from utils.py
    initialize_session_state()
    
    # Set logged in state
    st.session_state.logged_in = True
    
    # Check backend connectivity
    try:
        response = requests.get(f"{st.session_state.backend}/docs", timeout=5)
        st.session_state.backend_status = "connected"
    except:
        st.session_state.backend_status = "disconnected"
    
    # Initialize sample data or AI grading data
    if 'sample_data' not in st.session_state:
        with st.spinner("Initializing system data..."):
            # Set default job to MOCK_JOB_001
            st.session_state.selected_job_id = "MOCK_JOB_001"
            
            # Try to load AI grading data if a job is selected
            if 'selected_job_id' in st.session_state:
                ai_data = load_ai_grading_data(st.session_state.selected_job_id)
                if "error" not in ai_data:
                    st.session_state.sample_data = ai_data
                else:
                    # Load mock data if AI data loading fails
                    st.session_state.sample_data = load_mock_data()
            else:
                # Load mock data when no job is selected (before any grading)
                st.session_state.sample_data = load_mock_data()
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {
            'name': '张教授',
            'role': '教师',
            'department': '计算机科学与技术学院'
        }

def render_dashboard_header():
    """渲染仪表板头部导航栏"""
    st.markdown("""
    <div class="dashboard-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-icon">🎓</div>
                <div class="logo-text">SmarTAI Control Center</div>
            </div>
            <div class="user-section">
                <div class="user-info">
                    <div class="user-name">欢迎，{username}教授</div>
                    <div class="user-role">计算机科学与技术学院</div>
                </div>
                <div class="user-avatar">张</div>
            </div>
        </div>
    </div>
    """.format(username=st.session_state.get('username', '张')), unsafe_allow_html=True)

def render_status_overview():
    """渲染状态概览卡片"""
    st.markdown("##📊 系统状态概览")
    
    # 获取统计数据
    data = st.session_state.sample_data
    if not data:
        return
    
    students = data.get('student_scores', [])
    assignment_stats = data.get('assignment_stats')
    
    if assignment_stats:
        total_students = assignment_stats.total_students
        avg_score = assignment_stats.avg_score
        pass_rate = assignment_stats.pass_rate
        need_review = len([s for s in students if s.need_review])
    else:
        total_students = len(students)
        avg_score = sum(s.percentage for s in students) / len(students) if students else 0
        pass_rate = len([s for s in students if s.percentage >= 60]) / len(students) * 100 if students else 0
        need_review = len([s for s in students if s.need_review])
    
    #状态卡片网格
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">总学生数</div>
            <div class="status-value">{total_students}</div>
            <div class="status-trend">↗较 +12%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">平均分</div>
            <div class="status-value">{avg_score:.1f}%</div>
            <div class="status-trend">↗较上次 +3.2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">通过率</div>
            <div class="status-value">{pass_rate:.1f}%</div>
            <div class="status-trend">↗较 +5.1%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="status-card">
            <div class="status-title">待复核</div>
            <div class="status-value">{need_review}</div>
            <div class="status-trend">↘较昨天 -3</div>
        </div>
        """, unsafe_allow_html=True)

def render_quick_actions():
    """渲染快速操作区域"""
    st.markdown("""
    <div class="quick-actions">
        <div class="quick-actions-title">⚡快速操作中心</div>
        <div class="actions-grid">
    """, unsafe_allow_html=True)
    
    # 操作卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">📤</div>
            <div class="action-title">上传题目</div>
            <div class="action-desc">上传新的作业题目文件</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("立即上传", key="upload_prob", use_container_width=True):
            st.switch_page("pages/prob_upload.py")
    
    with col2:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">📊</div>
            <div class="action-title">查看报告</div>
            <div class="action-desc">查看详细的批改结果报告</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("查看报告", key="view_report", use_container_width=True):
            st.switch_page("pages/score_report.py")
    
    with col3:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">📈</div>
            <div class="action-title">数据分析</div>
            <div class="action-desc">查看学生表现和题目分析</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("数据分析", key="data_analysis", use_container_width=True):
            st.switch_page("pages/visualization.py")
    
    with col4:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🤖</div>
            <div class="action-title">AI批改</div>
            <div class="action-desc">启动AI智能批改任务</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("开始批改", key="ai_grading", use_container_width=True):
            st.switch_page("pages/wait_ai_grade.py")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_visualization_charts():
    """渲染数据可视化图表"""
    st.markdown("""
    <div class="visualization-section">
        <div class="visualization-title">📊 数据可视化分析</div>
        <div class="charts-grid">
    """, unsafe_allow_html=True)
    
    # 获取数据
    data = st.session_state.sample_data
    if not data:
        return
    
    students = data.get('student_scores', [])
    
    # 图表区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">成绩分布</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            fig = create_score_distribution_chart(students)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"图表生成失败: {str(e)}")
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">等级分布</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            fig = create_grade_pie_chart(students)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"图表生成失败: {str(e)}")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_ai_task_center():
    """渲染AI任务中心"""
    st.markdown("""
    <div class="ai-center">
        <div class="ai-center-title">🤖 AI批改任务中心</div>
        <div class="tasks-list">
    """, unsafe_allow_html=True)
    
    # 模拟任务列表
    tasks = [
        {
            "name": "数据结构期中考试批改",
            "status": "进行中",
            "progress": 75,
            "time": "2小时前开始"
        },
        {
            "name": "算法设计作业批改",
            "status": "已完成",
            "progress": 100,
            "time": "昨天完成"
        },
        {
            "name": "操作系统实验报告",
            "status": "等待中",
            "progress": 0,
            "time": "刚刚创建"
        }
    ]
    
    for task in tasks:
        progress_color = "#10B981" if task["progress"] == 100 else "#00D4FF"
        st.markdown(f"""
        <div class="task-item">
            <div class="task-info">
                <div class="task-name">{task['name']}</div>
                <div class="task-status">{task['status']} · {task['time']}</div>
            </div>
            <div class="task-progress">
                <div class="progress-bar" style="width: {task['progress']}%; background: {progress_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_notifications():
    """渲染通知面板"""
    st.markdown("""
    <div class="notifications-panel">
        <div class="notifications-title">🔔系统通知</div>
    """, unsafe_allow_html=True)
    
    # 模拟通知
    notifications = [
        {
            "content": "AI批改任务已完成，共批改45份作业",
            "time": "5分钟前"
        },
        {
            "content": "系统检测到3份作业需要人工复核",
            "time": "1小时前"
        },
        {
            "content": "新的题目模板已更新，请查看知识库",
            "time": "3小时前"
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

def render_dashboard():
    """渲染主仪表板内容"""
    # 初始化
    init_session_state()
    
    #渲头部导航
    render_dashboard_header()
    
    # 主内容区域
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    #状态概览
    render_status_overview()
    
    #快速操作
    render_quick_actions()
    
    #可视化分析
    col1, col2 = st.columns([3, 1])
    with col1:
        render_visualization_charts()
    with col2:
        render_notifications()
    
    # AI任务中心
    render_ai_task_center()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """主函数 -应用入口点"""
    #检查登录状态
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # 如果未登录，重定向到登录页面
    if not st.session_state.logged_in:
        st.switch_page("pages/login.py")
    else:
        # 如果已登录，显示主界面内容
        render_dashboard()

if __name__ == "__main__":
    main()