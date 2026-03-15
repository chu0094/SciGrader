"""
SciGrader 教师端仪表盘
功能：题目管理、已发布作业、批改后作业
"""
import streamlit as st
from utils.db_utils import get_db_manager, logout
from datetime import datetime, date


def teacher_dashboard():
    """教师端主界面"""
    
    user_info = st.session_state.user_info
    
    # 顶部导航栏
    render_top_nav(user_info)
    
    # 主内容区域 - 左右布局
    left_col, right_col = st.columns([7, 3])
    
    with left_col:
        render_left_panel()
    
    with right_col:
        render_right_panel(user_info)


def render_top_nav(user_info):
    """渲染顶部导航栏"""
    st.markdown(f"""
        <div class="top-navbar">
            <div class="navbar-title">📚 题目管理</div>
            <div class="navbar-user">
                <span>👤 {user_info['username']} / 教师</span>
                <button class="logout-button" onclick="alert('logout')">退出登录</button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Streamlit 退出按钮
    if st.button("🚪 退出登录", key="logout_btn"):
        logout()
        st.rerun()


def render_left_panel():
    """渲染左侧主要区域"""
    
    # 1. 新建题目模块
    render_create_problem_section()
    
    st.divider()
    
    # 1.5 发布作业模块（新增）
    render_publish_assignment_section()
    
    st.divider()
    
    # 2. 已发布作业模块
    render_published_assignments_section()
    
    st.divider()
    
    # 3. 批改后作业模块
    render_graded_work_section()


def render_publish_assignment_section():
    """渲染发布作业表单"""
    st.markdown("### 📢 发布新作业")
    
    db = get_db_manager()
    
    # 获取该教师创建的所有题目
    problems = db.get_all_problems(st.session_state.user_id)
    
    if not problems:
        st.info("请先创建题目，然后再发布作业")
        return
    
    problem_options = {f"{p['problem_number']} - {p['problem_title']}": p['problem_id'] for p in problems}
    
    with st.form(key="publish_assignment_form"):
        # 第一行：作业编号和标题
        col1, col2 = st.columns(2)
        with col1:
            assignment_number = st.text_input(
                "作业编号",
                placeholder="例如：HW001",
                key="assignment_number"
            )
        
        with col2:
            assignment_title = st.text_input(
                "作业标题",
                placeholder="例如：第一次作业",
                key="assignment_title"
            )
        
        # 第二行：课程名称和总分
        col1, col2 = st.columns(2)
        with col1:
            course_name = st.text_input(
                "课程名称",
                placeholder="例如：线性代数",
                value="线性代数",
                key="course_name"
            )
        
        with col2:
            total_score = st.number_input(
                "总分值",
                min_value=1,
                max_value=1000,
                value=100,
                key="total_score"
            )
        
        # 第三行：发布时间和截止时间
        col1, col2 = st.columns(2)
        with col1:
            from datetime import date, timedelta
            publish_date = st.date_input(
                "发布时间",
                value=date.today(),
                key="publish_date"
            )
        
        with col2:
            due_date = st.date_input(
                "截止时间",
                value=date.today() + timedelta(days=7),
                key="due_date"
            )
        
        # 第四行：选择题目
        selected_problems = st.multiselect(
            "选择题目（从已创建的题目中选择）",
            options=list(problem_options.keys()),
            help="可以选择多个题目组成作业",
            key="select_problems_for_assignment"
        )
        
        # 第五行：作业说明
        assignment_description = st.text_area(
            "作业说明",
            placeholder="请输入作业要求和说明...",
            height=80,
            key="assignment_description"
        )
        
        # 提交按钮
        submit_button = st.form_submit_button(
            "📢 发布作业",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            handle_publish_assignment(
                assignment_number, assignment_title, course_name,
                total_score, publish_date, due_date,
                selected_problems, problem_options, assignment_description
            )


def render_create_problem_section():
    """渲染新建题目表单"""
    st.markdown("### 📝 新建题目")
    
    with st.form(key="create_problem_form"):
        # 第一行：题目类型和难度
        col1, col2 = st.columns(2)
        with col1:
            problem_type = st.selectbox(
                "题目类型",
                ["概念题", "计算题", "编程题"],
                key="problem_type"
            )
        
        with col2:
            difficulty = st.selectbox(
                "难度等级",
                ["简单", "中等", "困难"],
                key="difficulty_level"
            )
        
        # 第二行：题目编号和分值
        col1, col2 = st.columns(2)
        with col1:
            problem_number = st.text_input(
                "题目编号",
                placeholder="例如：Q001",
                key="problem_number"
            )
        
        with col2:
            max_score = st.number_input(
                "分值",
                min_value=1,
                max_value=100,
                value=10,
                key="max_score"
            )
        
        # 第三行：题目内容
        description = st.text_area(
            "题目内容",
            placeholder="请输入题目描述（支持文本、公式、代码）",
            height=150,
            key="problem_description"
        )
        
        # 第四行：参考答案
        reference_answer = st.text_area(
            "参考答案",
            placeholder="请输入参考答案",
            height=100,
            key="reference_answer"
        )
        
        # 第五行：知识点标签
        existing_kps = ["线性代数", "微积分", "编程基础", "数据结构"]
        knowledge_points = st.multiselect(
            "知识点标签",
            options=existing_kps,
            help="可选择已有知识点或在下方的输入框中添加新的",
            key="knowledge_points"
        )
        
        # 添加自定义知识点输入
        custom_kp = st.text_input(
            "添加自定义知识点（可选）",
            placeholder="输入新的知识点名称",
            key="custom_knowledge_point"
        )
        
        if custom_kp and custom_kp not in knowledge_points:
            knowledge_points.append(custom_kp)
        
        # 第六行：附件上传
        uploaded_files = st.file_uploader(
            "附件上传",
            type=["pdf", "png", "jpg", "txt", "py", "java", "cpp"],
            accept_multiple_files=True,
            help="支持 PDF、PNG、JPG、TXT、代码文件等"
        )
        
        # 提交按钮
        submit_button = st.form_submit_button(
            "➕ 创建题目",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            handle_create_problem(
                problem_type, difficulty, problem_number, max_score,
                description, reference_answer, knowledge_points, uploaded_files
            )


def handle_create_problem(problem_type, difficulty, problem_number, max_score,
                         description, reference_answer, knowledge_points, uploaded_files):
    """处理创建题目逻辑"""
    import json
    
    if not problem_number or not description:
        st.error("请填写题目编号和题目内容")
        return
    
    db = get_db_manager()
    
    # 映射类型和难度
    type_map = {"概念题": "concept", "计算题": "calculation", "编程题": "programming"}
    difficulty_map = {"简单": "easy", "中等": "medium", "困难": "hard"}
    
    # 处理附件信息
    attachments = []
    if uploaded_files:
        for f in uploaded_files:
            attachments.append({
                "name": f.name,
                "size": f.size,
                "type": f.type
            })
    
    # 转换为 JSON 格式（MySQL JSON 字段要求）
    try:
        kp_json = json.dumps(knowledge_points, ensure_ascii=False)
        attachments_json = json.dumps(attachments, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        st.error(f"数据格式错误：{e}")
        return
    
    # 插入数据库
    problem_data = (
        problem_number,
        f"{problem_type} - {problem_number}",
        type_map[problem_type],
        difficulty_map[difficulty],
        description,
        reference_answer,
        max_score,
        st.session_state.user_id,
        kp_json,
        attachments_json,
        "published"
    )
    
    result = db.create_problem(problem_data)
    
    if result:
        st.success("✓ 题目创建成功！")
        st.balloons()
    else:
        st.error("✗ 题目创建失败")


def handle_publish_assignment(assignment_number, assignment_title, course_name,
                              total_score, publish_date, due_date,
                              selected_problems, problem_options, assignment_description):
    """处理发布作业逻辑"""
    import json
    
    if not assignment_number or not assignment_title:
        st.error("请填写作业编号和标题")
        return
    
    if not selected_problems:
        st.error("请至少选择一个题目")
        return
    
    db = get_db_manager()
    
    # 获取选中的题目 ID 列表
    problem_ids = [problem_options[title] for title in selected_problems]
    
    # 转换为 JSON 格式
    try:
        problem_ids_json = json.dumps(problem_ids)
    except (TypeError, ValueError) as e:
        st.error(f"数据格式错误：{e}")
        return
    
    # 插入数据库
    assignment_data = (
        assignment_number,
        assignment_title,
        assignment_description,
        course_name,
        st.session_state.user_id,
        total_score,
        publish_date,
        due_date,
        "active",  # status
        problem_ids_json
    )
    
    result = db.create_assignment(assignment_data)
    
    if result:
        st.success("✓ 作业发布成功！")
        st.balloons()
    else:
        st.error("✗ 作业发布失败")


def render_published_assignments_section():
    """渲染已发布作业列表"""
    st.markdown("### 📋 已发布作业")
    
    db = get_db_manager()
    assignments = db.get_all_assignments(st.session_state.user_id)
    
    if not assignments:
        st.info("暂无已发布的作业")
        return
    
    for assignment in assignments:
        render_assignment_card_teacher(assignment)


def render_assignment_card_teacher(assignment):
    """渲染教师端作业卡片"""
    with st.expander(f"**{assignment['assignment_title']}** - {assignment['course_name']}", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**作业编号：** {assignment['assignment_number']}")
            st.markdown(f"**发布时间：** {assignment['publish_date']}")
        
        with col2:
            st.markdown(f"**总分值：** {assignment['total_score']}分")
            st.markdown(f"**截止时间：** {assignment['due_date']}")
        
        with col3:
            status_badge = "✅ 进行中" if assignment['status'] == 'active' else "🔒 已截止"
            st.markdown(f"**状态：** {status_badge}")
        
        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ 查看提交情况", key=f"view_{assignment['assignment_id']}", use_container_width=True):
                st.session_state.current_assignment = assignment
                st.session_state.show_submissions = True
        
        with col2:
            if st.button("✏️ 编辑作业", key=f"edit_{assignment['assignment_id']}", use_container_width=True):
                pass


def render_graded_work_section():
    """渲染批改后作业模块"""
    st.markdown("### ✅ 批改后作业")
    
    db = get_db_manager()
    graded_work = db.get_teacher_graded_work(st.session_state.user_id)
    
    if not graded_work:
        st.info("暂无批改完成的作业")
        return
    
    for work in graded_work:
        with st.expander(f"**{work['student_name']} - {work['assignment_title']}**", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**学生姓名：** {work['student_name']}")
                st.markdown(f"**作业编号：** {work['assignment_number']}")
                st.markdown(f"**批改时间：** {work['graded_at']}")
            
            with col2:
                score = work.get('auto_grade_score') or work.get('teacher_grade_score')
                st.metric("系统评分", f"{score}分" if score else "未评分")
            
            if work.get('auto_grade_comments'):
                st.text_area("系统评语", work['auto_grade_comments'], disabled=True)
            
            if work.get('teacher_comments'):
                st.text_area("教师评语", work['teacher_comments'], disabled=True)


def render_right_panel(user_info):
    """渲染右侧快捷操作面板"""
    
    # 快捷操作卡片
    st.markdown("### ⚡ 快捷操作")
    
    if st.button("📥 批量导入题目", use_container_width=True, key="bulk_import"):
        st.info("批量导入功能开发中...")
    
    if st.button("🏷️ 管理知识点标签", use_container_width=True, key="manage_kp"):
        st.info("知识点管理功能开发中...")
    
    if st.button("🤖 AI 难度评估", use_container_width=True, key="ai_assess"):
        st.info("AI 评估功能开发中...")
    
    st.divider()
    
    # 系统信息卡片
    st.markdown("### ℹ️ 系统信息")
    
    st.markdown(f"""
        <div style="background-color: #F5F5F5; padding: 15px; border-radius: 8px;">
            <p><strong>当前用户：</strong> {user_info['username']}</p>
            <p><strong>角色：</strong> 教师</p>
            <p><strong>邮箱：</strong> {user_info.get('email', '未设置')}</p>
            <p><strong>登录时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    """, unsafe_allow_html=True)
