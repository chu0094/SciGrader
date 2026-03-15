"""
SciGrader 通用组件库
"""
import streamlit as st


def render_sidebar(role, user_info):
    """渲染侧边栏（如果需要）"""
    pass


def show_success_message(message):
    """显示成功消息"""
    st.success(f"✓ {message}")


def show_error_message(message):
    """显示错误消息"""
    st.error(f"✗ {message}")


def show_warning_message(message):
    """显示警告消息"""
    st.warning(f"⚠ {message}")


def show_info_message(message):
    """显示信息消息"""
    st.info(f"ℹ {message}")


def create_card(title=None, key=None):
    """创建卡片容器"""
    if title:
        with st.container():
            st.markdown(f"""
                <div class="card" style="margin-bottom: 20px;">
                    {'<h3 class="card-header">' + title + '</h3>' if title else ''}
            """, unsafe_allow_html=True)
            return st.container()
    else:
        return st.container()


def render_assignment_card(assignment, status='default'):
    """渲染作业卡片"""
    status_colors = {
        'pending': ('#FFA000', '#FFF8E1'),
        'submitted': ('#2E7D32', '#E8F5E9'),
        'overdue': ('#D32F2F', '#FFEBEE'),
        'default': ('#BDBDBD', '#FFFFFF')
    }
    
    border_color, bg_color = status_colors.get(status, status_colors['default'])
    
    st.markdown(f"""
        <div class="assignment-card {status}" style="
            border-left-color: {border_color};
            background-color: {bg_color};
            margin-bottom: 16px;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
        </div>
    """, unsafe_allow_html=True)


def render_stat_card(label, number, color_gradient='linear-gradient(135deg, #667eea 0%, #764ba2 100%)'):
    """渲染统计卡片"""
    st.markdown(f"""
        <div class="stat-card" style="
            background: {color_gradient};
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        ">
            <div class="stat-number" style="font-size: 36px; font-weight: 700; margin-bottom: 8px;">
                {number}
            </div>
            <div class="stat-label" style="font-size: 14px; opacity: 0.9;">
                {label}
            </div>
        </div>
    """, unsafe_allow_html=True)


def file_uploader_component(label, file_types, multiple=False):
    """文件上传组件"""
    uploaded_files = st.file_uploader(
        label=label,
        type=file_types,
        accept_multiple_files=multiple,
        help=f"支持的文件类型：{', '.join(file_types)}"
    )
    return uploaded_files


def confirm_dialog(message, yes_callback=None, no_callback=None):
    """确认对话框"""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认", key="confirm_yes"):
            if yes_callback:
                yes_callback()
    with col2:
        if st.button("取消", key="confirm_no"):
            if no_callback:
                no_callback()


def loading_spinner(message="加载中..."):
    """加载动画"""
    with st.spinner(message):
        yield
