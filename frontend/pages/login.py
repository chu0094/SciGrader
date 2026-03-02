import streamlit as st
import time
import os

# Set page configuration
st.set_page_config(
    page_title="SmarTAI Homework Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 加载深色主题CSS文件
def load_css():
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
{load_css()}

/*隐藏Streamlit默认元素 */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* 主容器样式 */
.main {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%) !important;
    padding: 0;
    min-height: 100vh;
    position: relative;
    overflow: hidden;
}}

/*动态背景效果 */
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
}}

/*动态粒子背景 */
.main::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(0, 245, 212, 0.15) 0%, transparent 50%);
    animation: background-pulse 8s ease-in-out infinite alternate;
    z-index: -1;
}}

@keyframes background-pulse {{
    0% {{ opacity: 0.4; transform: scale(1); }}
    100% {{ opacity: 0.8; transform: scale(1.1); }}
}}

/* 标题样式 - 发光霓虹效果 */
.title {{
    text-align: center;
    font-size: 4rem;
    font-weight: 800;
    margin: 2rem 0 1rem 0;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6, #00F5D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.7);
    position: relative;
    animation: title-glow 3s ease-in-out infinite alternate;
    letter-spacing: 2px;
}}

@keyframes title-glow {{
    0% {{ 
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.6),
                     0 0 40px rgba(139, 92, 246, 0.4);
    }}
    100% {{ 
        text-shadow: 0 0 40px rgba(139, 92, 246, 0.7),
                     0 0 60px rgba(0, 245, 212, 0.5),
                     0 0 80px rgba(0, 212, 255, 0.3);
    }}
}}

/*副样式 */
.subtitle {{
    text-align: center;
    color: #94A3B8;
    font-size: 1.5rem;
    margin-bottom: 3rem;
    font-weight: 400;
    letter-spacing: 1px;
    text-shadow: 0 0 10px rgba(148, 163, 184, 0.3);
}}

/*双选择区域 */
.role-selection {{
    display: flex;
    gap: 2.5rem;
    max-width: 1300px;
    margin: 0 auto;
    padding: 2rem;
    position: relative;
    z-index: 10;
}}

/*角卡片 */
.role-card {{
    flex: 1;
    background: rgba(30, 41, 59, 0.75);
    border: 2px solid rgba(148, 163, 184, 0.25);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    min-height: 450px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}}

.role-card:hover {{
    transform: translateY(-20px) scale(1.03);
    border-color: #00D4FF;
    box-shadow: 
        0 25px 60px rgba(0, 0, 0, 0.4),
        0 0 40px rgba(0, 212, 255, 0.4),
        inset 0 0 20px rgba(0, 212, 255, 0.1);
}}

.role-card.teacher {{
    border-top: 5px solid #00D4FF;
}}

.role-card.student {{
    border-top: 5px solid #8B5CF6;
}}

.role-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(90deg, #00D4FF, #8B5CF6, #00F5D4, #00D4FF);
    transform: scaleX(0);
    transition: transform 0.4s ease;
    animation: border-flow 3s linear infinite;
}}

@keyframes border-flow {{
    0% {{ background-position: 0% 50%; }}
    100% {{ background-position: 200% 50%; }}
}}

.role-card:hover::before {{
    transform: scaleX(1);
}}

/*角色图标 */
.role-icon {{
    font-size: 6rem;
    margin: 1.5rem 0;
    filter: drop-shadow(0 0 25px currentColor);
    transition: all 0.4s ease;
    position: relative;
}}

.role-card.teacher .role-icon {{
    color: #00D4FF;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
}}

.role-card.student .role-icon {{
    color: #8B5CF6;
    text-shadow: 0 0 30px rgba(139, 92, 246, 0.6);
}}

.role-card:hover .role-icon {{
    transform: scale(1.3) rotate(10deg);
    filter: drop-shadow(0 0 40px currentColor);
}}

/*角标题 */
.role-title {{
    font-size: 2.2rem;
    font-weight: 800;
    margin: 1.5rem 0;
    letter-spacing: 1px;
}}

.role-card.teacher .role-title {{
    background: linear-gradient(135deg, #00D4FF, #00F5D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}}

.role-card.student .role-title {{
    background: linear-gradient(135deg, #8B5CF6, #00D4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}}

/* 角色描述 */
.role-description {{
    color: #CBD5E1;
    font-size: 1.15rem;
    line-height: 1.8;
    margin: 1.5rem 0;
    flex-grow: 1;
    text-shadow: 0 0 5px rgba(203, 213, 225, 0.2);
}}

/*角色特点列表 */
.role-features {{
    text-align: left;
    margin: 2rem 0;
    padding: 0 1rem;
}}

.role-feature {{
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 15px 0;
    color: #94A3B8;
    font-size: 1.05rem;
    transition: all 0.3s ease;
}}

.role-feature:hover {{
    color: #F1F5F9;
    transform: translateX(10px);
}}

.role-feature-icon {{
    font-size: 1.4rem;
    min-width: 24px;
    text-align: center;
}}

.role-card.teacher .role-feature-icon {{
    color: #00D4FF;
    text-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
}}

.role-card.student .role-feature-icon {{
    color: #8B5CF6;
    text-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
}}

/* 选择按钮 */
.select-btn {{
    background: linear-gradient(135deg, #00D4FF, #8B5CF6) !important;
    color: #0F172A !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 18px 36px !important;
    font-weight: 700 !important;
    font-size: 1.2rem !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.4) !important;
    position: relative !important;
    overflow: hidden !important;
    letter-spacing: 1px !important;
}}

.select-btn:hover {{
    transform: translateY(-5px) !important;
    box-shadow: 
        0 15px 40px rgba(0, 212, 255, 0.5),
        0 0 35px rgba(0, 212, 255, 0.4) !important;
}}

.select-btn::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s;
}}

.select-btn:hover::before {{
    left: 100%;
}}

.role-card.student .select-btn {{
    background: linear-gradient(135deg, #8B5CF6, #00D4FF) !important;
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4) !important;
}}

.role-card.student .select-btn:hover {{
    box-shadow: 
        0 15px 40px rgba(139, 92, 246, 0.5),
        0 0 35px rgba(139, 92, 246, 0.4) !important;
}}

/* 登录表单区域 */
.login-form-container {{
    max-width: 550px;
    margin: 3rem auto;
    padding: 0 2rem;
    position: relative;
    z-index: 10;
}}

/*系统介绍区域 */
.system-intro {{
    text-align: center;
    max-width: 900px;
    margin: 4rem auto;
    padding: 0 2rem;
    position: relative;
    z-index: 10;
}}

.intro-title {{
    font-size: 2.8rem;
    font-weight: 800;
    margin: 2rem 0 1.5rem 0;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6, #00F5D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.4);
}}

.intro-description {{
    font-size: 1.3rem;
    color: #94A3B8;
    line-height: 1.9;
    margin: 2rem 0;
    text-shadow: 0 0 10px rgba(148, 163, 184, 0.2);
}}

/* 特性网格 */
.features-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2.5rem;
    margin: 4rem 0;
    position: relative;
    z-index: 10;
}}

.feature-item {{
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 20px;
    padding: 2.5rem;
    text-align: center;
    backdrop-filter: blur(15px);
    transition: all 0.4s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}}

.feature-item:hover {{
    transform: translateY(-10px) scale(1.02);
    border-color: rgba(0, 212, 255, 0.4);
    box-shadow: 
        0 15px 40px rgba(0, 0, 0, 0.3),
        0 0 25px rgba(0, 212, 255, 0.2);
}}

.feature-icon {{
    font-size: 3.5rem;
    margin-bottom: 1.5rem;
    color: #00D4FF;
    filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.4));
}}

.feature-title {{
    font-size: 1.4rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1.2rem;
    text-shadow: 0 0 10px rgba(241, 245, 249, 0.1);
}}

.feature-desc {{
    color: #94A3B8;
    font-size: 1.05rem;
    line-height: 1.7;
    text-shadow: 0 0 5px rgba(148, 163, 184, 0.1);
}}

/*响应式设计 */
@media (max-width: 1200px) {{
    .role-selection {{
        gap: 2rem;
        padding: 1.5rem;
    }}
    
    .role-card {{
        padding: 2.5rem 2rem;
        min-height: 400px;
    }}
}}

@media (max-width: 768px) {{
    .role-selection {{
        flex-direction: column;
        gap: 2rem;
    }}
    
    .title {{
        font-size: 3rem;
    }}
    
    .role-card {{
        padding: 2.5rem 1.5rem;
        min-height: 380px;
    }}
    
    .role-icon {{
        font-size: 5rem;
    }}
    
    .features-grid {{
        grid-template-columns: 1fr;
        gap: 2rem;
    }}
    
    .system-intro {{
        margin: 3rem auto;
    }}
}}

@media (max-width: 480px) {{
    .title {{
        font-size: 2.2rem;
    }}
    
    .subtitle {{
        font-size: 1.2rem;
    }}
    
    .role-card {{
        padding: 2rem 1.2rem;
        min-height: 350px;
    }}
    
    .role-icon {{
        font-size: 4rem;
    }}
    
    .role-title {{
        font-size: 1.8rem;
    }}
    
    .select-btn {{
        padding: 15px 25px !important;
        font-size: 1.1rem !important;
    }}
    
    .feature-item {{
        padding: 2rem 1.5rem;
    }}
    
    .feature-icon {{
        font-size: 3rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'show_login_modal' not in st.session_state:
    st.session_state.show_login_modal = False
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None

# 登录函数
def login(username, password, role):
    #这里可以添加真实的认证逻辑
    #目前使用简单的演示逻辑
    if username == "admin" and password == "123456" and role == "teacher":
        return True, "teacher"
    elif username == "student" and password == "123456" and role == "student":
        return True, "student"
    elif username and password and role:  # 任何非空用户名和密码都可以登录（演示用）
        return True, role
    return False, None

def render_role_selection():
    """渲染角色选择界面"""
    # 标题和副标题
    st.markdown('<div class="title" data-text="SmarTAI">SmarTAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Intelligent Homework Assessment Platform</div>', unsafe_allow_html=True)
    
    #双选择卡片
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="role-card teacher">
            <div class="role-icon">👨‍🏫</div>
            <div class="role-title">Teacher</div>
            <div class="role-description">
                Access the complete teaching management system with AI-powered grading capabilities
            </div>
            <div class="role-features">
                <div class="role-feature">
                    <div class="role-feature-icon">🤖</div>
                    <span>AI智能批改</span>
                </div>
                <div class="role-feature">
                    <div class="role-feature-icon">📊</div>
                    <span>数据可视化分析</span>
                </div>
                <div class="role-feature">
                    <div class="role-feature-icon">📚</div>
                    <span>知识库管理</span>
                </div>
                <div class="role-feature">
                    <div class="role-feature-icon">⚙️</div>
                    <span>系统配置管理</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("选择教师端", key="teacher_select", use_container_width=True):
            st.session_state.selected_role = "teacher"
            st.rerun()
    
    with col2:
        st.markdown('''
        <div class="role-card student">
            <div class="role-icon">🎓</div>
            <div class="role-title">Student</div>
            <div class="role-description">
                Submit assignments and track learning progress with personalized feedback
            </div>
            <div class="role-features">
                <div class="role-feature">
                    <div class="role-feature-icon">📤</div>
                    <span>作业提交</span>
                </div>
                <div class="role-feature">
                    <div class="role-feature-icon">📈</div>
                    <span>成绩查看</span>
                </div>
                <div class="role-feature">
                    <div class="role-feature-icon">📝</div>
                    <span>反馈查看</span>
                </div>
                <div class="role-feature">
                    <div class="role-feature-icon">🎯</div>
                    <span>学习进度跟踪</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("选择学生端", key="student_select", use_container_width=True):
            st.session_state.selected_role = "student"
            st.rerun()
    
    #系统介绍
    st.markdown("""
    <div class="system-intro">
        <div class="intro-title">🚀 Next-Generation AI Teaching Platform</div>
        <div class="intro-description">
            SmarTAI combines cutting-edge artificial intelligence with educational technology to create 
            an intelligent homework assessment platform that revolutionizes the way assignments are 
            graded and learning is tracked.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    #特网格
    st.markdown("""
    <div class="features-grid">
        <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Lightning Fast Processing</div>
            <div class="feature-desc">AI-powered grading delivers results in seconds, not hours</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Precision Grading</div>
            <div class="feature-desc">Advanced algorithms ensure consistent and accurate evaluation</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Enterprise Security</div>
            <div class="feature-desc">Bank-level encryption protects all your educational data</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🌐</div>
            <div class="feature-title">Global Accessibility</div>
            <div class="feature-desc">Access your platform anytime, anywhere with cloud deployment</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_login_form():
    """渲染登录表单"""
    st.markdown('<div class="title">🔐 User Login</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Welcome {st.session_state.selected_role}! Please enter your credentials</div>', unsafe_allow_html=True)
    
    # 创建居中的登录表单
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        #角色指示器
        role_color = "#00D4FF" if st.session_state.selected_role == "teacher" else "#8B5CF6"
        role_icon = "👨‍🏫" if st.session_state.selected_role == "teacher" else "🎓"
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{role_icon}</div>
            <div style="background: rgba(0, 212, 255, 0.1); border: 2px solid {role_color}; border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(10px);">
                <h3 style="color: {role_color}; margin: 0; font-size: 1.8rem; font-weight: 700;">{st.session_state.selected_role.title()} Mode</h3>
                <p style="color: #94A3B8; margin: 0.5rem 0 0 0;">Please enter your login credentials</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 登录表单
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Username",
                placeholder=f"Enter your {st.session_state.selected_role} username",
                key="login_username",
                help=f"Enter your {st.session_state.selected_role} username or email address"
            )
            
            password = st.text_input(
                "🔒 Password",
                type="password", 
                placeholder="Enter your password",
                key="login_password",
                help="Enter your login password"
            )
            
            st.markdown('<br>', unsafe_allow_html=True)
            
            # 按钮区域
            col_login, col_cancel = st.columns([3, 1])
            
            with col_login:
                login_btn = st.form_submit_button(
                    "🚀 Log in Now", 
                    use_container_width=True,
                    help="Click to log in"
                )
            
            with col_cancel:
                cancel_btn = st.form_submit_button(
                    "Back", 
                    use_container_width=True,
                    help="Return to role selection"
                )
            
            #处理登录逻辑
            if login_btn:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    success, user_role = login(username, password, st.session_state.selected_role)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = user_role
                        st.session_state.show_login_modal = False
                        st.success("✅ Login successful! Redirecting...")
                        time.sleep(1)
                        #到主界面
                        st.switch_page("pages/main.py")
                    else:
                        st.error("❌ Incorrect username or password, please try again")

            if cancel_btn:
                st.session_state.selected_role = None
                st.rerun()
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        #账户信息
        demo_accounts = {
            "teacher": {"username": "admin", "password": "123456"},
            "student": {"username": "student", "password": "123456"}
        }
        
        demo = demo_accounts.get(st.session_state.selected_role, {})
        st.markdown(f"""
        <div style="background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; backdrop-filter: blur(10px);">
            <div style="color: #00D4FF; font-weight: 600; text-align: center; margin-bottom: 0.5rem;">💡 Demo Account</div>
            <div style="text-align: center; color: #94A3B8;">
                <div><strong>Username:</strong> {demo.get('username', 'N/A')}</div>
                <div><strong>Password:</strong> {demo.get('password', 'N/A')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    # 如果已登录，直接跳转到主界面
    if st.session_state.logged_in:
        st.switch_page("pages/main.py")
        return
    
    #根据状态渲染不同界面
    if st.session_state.selected_role:
        render_login_form()
    else:
        render_role_selection()

if __name__ == "__main__":
    main()