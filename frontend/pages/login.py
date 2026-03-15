"""
SciGrader 登录页面
提供教师端和学生端的登录入口
"""
import streamlit as st
from utils.db_utils import get_db_manager, hash_password


def login_page():
    """登录页面"""
    
    # 页面标题
    st.markdown("""
        <div class="login-container">
            <div class="login-card">
                <h1 class="system-title">📚 SciGrader</h1>
    """, unsafe_allow_html=True)
    
    # 角色切换 Tab
    role = st.session_state.get('login_role', 'teacher')
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍🏫 教师端", key="role_teacher", use_container_width=True):
            st.session_state.login_role = 'teacher'
            st.rerun()
    
    with col2:
        if st.button("👨‍🎓 学生端", key="role_student", use_container_width=True):
            st.session_state.login_role = 'student'
            st.rerun()
    
    # 显示当前选择的角色
    role_display = "教师端" if role == 'teacher' else "学生端"
    st.markdown(f"**当前选择：** {role_display}")
    st.divider()
    
    # 登录表单
    with st.form(key="login_form"):
        username = st.text_input(
            "账号",
            placeholder="请输入用户名",
            key="login_username"
        )
        
        password = st.text_input(
            "密码",
            placeholder="请输入密码",
            type="password",
            key="login_password"
        )
        
        submit_button = st.form_submit_button(
            "登录",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            handle_login(username, password, role)
    
    # 演示账号提示
    st.markdown("""
        <div class="demo-account-tip">
            <strong>💡 演示账号：</strong><br>
            教师端：admin / 123456<br>
            学生端：student1 / 123456
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def handle_login(username, password, role):
    """处理登录逻辑"""
    if not username or not password:
        st.error("请输入用户名和密码")
        return
    
    try:
        db = get_db_manager()
        
        # 检查数据库连接是否成功
        if not db.connection or not db.connection.is_connected():
            st.error("""
            ### ❌ 数据库连接失败
            
            请按照以下步骤检查：
            
            1. **MySQL 服务是否运行**
               - Windows: 按 `Win+R`，输入 `services.msc`
               - 找到 MySQL 服务，右键点击"启动"
            
            2. **数据库配置是否正确**
               - 打开 `.streamlit/secrets.toml`
               - 检查用户名、密码、数据库名是否正确
            
            3. **数据库是否已初始化**
               ```bash
               cd frontend
               python utils/init_database.py
               ```
            
            完成后请刷新页面重试。
            """)
            return
        
        # 简单验证（实际应该用 bcrypt）
        password_hash = hash_password(password)
        
        # 验证用户
        user = db.verify_user(username, password_hash)
        
        if user:
            # 检查角色是否匹配
            if user['role'] != role:
                role_text = "教师" if role == 'teacher' else "学生"
                st.error(f"该账号不是{role_text}角色")
                return
            
            # 设置会话状态
            st.session_state.logged_in = True
            st.session_state.user_info = user
            st.session_state.role = role
            st.session_state.user_id = user['user_id']
            
            st.success(f"欢迎，{user['username']}！")
            st.balloons()
            st.rerun()
        else:
            st.error("用户名或密码错误")
            
    except Exception as e:
        st.error(f"登录过程中发生错误：{str(e)}")
        st.info("请检查数据库配置，或联系系统管理员")


def logout():
    """退出登录"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
