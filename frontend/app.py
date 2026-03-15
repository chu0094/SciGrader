"""
SciGrader 主应用入口
理工科 AI 作业批改系统
"""
import streamlit as st
from utils.db_utils import check_session_state, get_db_manager, logout
from pages.login import login_page
from pages.teacher_dashboard import teacher_dashboard
from pages.student_dashboard import student_dashboard


def main():
    """主应用函数"""
    st.set_page_config(
        page_title="SciGrader - 理工科 AI 作业批改系统",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 加载自定义 CSS
    with open("static/styles.css", "r", encoding='utf-8') as f:
        custom_css = f.read()
    st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    
    # 检查会话状态
    check_session_state()
    
    # 根据登录状态和角色显示不同页面
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.role == 'teacher':
            teacher_dashboard()
        elif st.session_state.role == 'student':
            student_dashboard()
        else:
            st.error("未知角色")
            if st.button("返回登录"):
                logout()
                st.rerun()


if __name__ == "__main__":
    main()
