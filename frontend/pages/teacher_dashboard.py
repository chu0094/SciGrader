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
    
    # 检查是否显示提交情况
    if st.session_state.get('show_submissions'):
        render_submission_view()
        return
    
    # 检查是否显示编辑作业
    if st.session_state.get('show_edit_assignment'):
        render_edit_assignment_view()
        return
    
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
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👁️ 查看提交情况", key=f"view_{assignment['assignment_id']}", use_container_width=True):
                st.session_state.current_assignment = assignment
                st.session_state.show_submissions = True
                st.session_state.show_edit_assignment = False
                st.rerun()
        
        with col2:
            if st.button("✏️ 编辑作业", key=f"edit_{assignment['assignment_id']}", use_container_width=True):
                st.session_state.current_assignment = assignment
                st.session_state.show_edit_assignment = True
                st.session_state.show_submissions = False
                st.rerun()
        
        with col3:
            if st.button("🗑️ 删除作业", key=f"delete_{assignment['assignment_id']}", use_container_width=True, type="secondary"):
                # 存储要删除的作业 ID
                st.session_state.show_delete_confirm = assignment['assignment_id']
                st.session_state.delete_assignment_title = assignment['assignment_title']
    
    # 显示删除确认对话框
    if st.session_state.get('show_delete_confirm') == assignment['assignment_id']:
        render_delete_confirmation(assignment['assignment_id'], st.session_state.get('delete_assignment_title', ''))


def render_graded_work_section():
    """渲染批改后作业模块"""
    st.markdown("### ✅ 批改后作业")
    
    db = get_db_manager()
    graded_work = db.get_teacher_graded_work(st.session_state.user_id)
    
    if not graded_work:
        st.info("暂无批改完成的作业")
        return
    
    for work in graded_work:
        render_graded_work_card(work)


def render_graded_work_card(work):
    """渲染批改后作业卡片"""
    submission_id = work.get('submission_id')
    
    with st.expander(f"**{work['student_name']}** - {work['assignment_title']}", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**学生姓名：** {work['student_name']}")
            st.markdown(f"**作业编号：** {work['assignment_number']}")
            st.markdown(f"**批改时间：** {work['graded_at']}")
        
        with col2:
            auto_score = work.get('auto_grade_score')
            teacher_score = work.get('teacher_grade_score')
            st.metric("AI 评分", f"{auto_score}分" if auto_score else "未评分")
            st.metric("教师评分", f"{teacher_score}分" if teacher_score else "未评分")
        
        # AI 评语
        if work.get('auto_grade_comments'):
            st.markdown("**🤖 AI 评语：**")
            st.info(work['auto_grade_comments'])
        
        # 教师评语（可编辑）
        st.markdown("**👨‍🏫 教师评语：**")
        
        # 检查是否正在编辑该提交
        is_editing = st.session_state.get(f'editing_submission_{submission_id}')
        
        if is_editing:
            render_edit_teacher_comments(work)
        else:
            # 显示评语和编辑按钮
            if work.get('teacher_comments'):
                st.success(work['teacher_comments'])
            else:
                st.warning("暂无教师评语")
            
            if st.button("✏️ 修改评语", key=f"edit_comments_{submission_id}", use_container_width=True):
                st.session_state[f'editing_submission_{submission_id}'] = True
                st.rerun()


def render_edit_teacher_comments(work):
    """渲染编辑教师评语表单"""
    submission_id = work.get('submission_id')
    
    with st.form(key=f"edit_comments_form_{submission_id}"):
        # 显示当前评语
        st.markdown("**📝 当前评语：**")
        current_comments = work.get('teacher_comments', '')
        if current_comments:
            st.info(current_comments)
        else:
            st.info("（暂无评语）")
        
        # 输入新评语
        st.markdown("**✍️ 输入新评语：**")
        new_comments = st.text_area(
            "",
            value=current_comments,
            height=150,
            key=f"new_comments_{submission_id}",
            placeholder="请输入您的评价和建议..."
        )
        
        # 按钮
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("💾 保存评语", type="primary", use_container_width=True)
        
        with col2:
            cancel_button = st.form_submit_button("❌ 取消", use_container_width=True)
        
        if submit_button:
            handle_update_teacher_comments(submission_id, new_comments)
        
        if cancel_button:
            st.session_state[f'editing_submission_{submission_id}'] = False
            st.rerun()


def render_delete_confirmation(assignment_id, assignment_title):
    """渲染删除确认对话框"""
    st.warning(f"⚠️ 您确定要删除作业 **{assignment_title}** 吗？")
    st.info("ℹ️ 删除后将同时删除该作业的所有学生提交记录和批改记录，此操作不可恢复！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ 确认删除", key=f"confirm_delete_{assignment_id}", type="primary", use_container_width=True):
            handle_delete_assignment(assignment_id)
    
    with col2:
        if st.button("❌ 取消", key=f"cancel_delete_{assignment_id}", use_container_width=True):
            # 清除删除确认状态
            st.session_state.show_delete_confirm = None
            st.session_state.delete_assignment_title = None
            st.rerun()


def handle_delete_assignment(assignment_id):
    """处理删除作业逻辑"""
    db = get_db_manager()
    
    try:
        # 直接调用数据库管理器删除作业
        result = db.delete_assignment(assignment_id, st.session_state.user_id)
        
        if result:
            st.success(f"✅ 作业删除成功！")
            # 清除删除确认状态
            st.session_state.show_delete_confirm = None
            st.session_state.delete_assignment_title = None
            # 延迟一下让用户看到成功消息
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ 作业删除失败，请重试")
            
    except Exception as e:
        st.error(f"❌ 删除作业时发生错误：{str(e)}")


def handle_edit_assignment(assignment_id, title, course_name, total_score, due_date, description):
    """处理编辑作业逻辑"""
    if not title:
        st.error("请填写作业标题")
        return
    
    db = get_db_manager()
    
    try:
        # 更新作业信息
        update_data = (
            title,
            description,
            course_name,
            total_score,
            due_date,
            assignment_id,
            st.session_state.user_id  # 确保只能修改自己的作业
        )
        
        result = db.update_assignment(update_data)
        
        if result:
            st.success("✅ 作业更新成功！")
            import time
            time.sleep(1)
            st.session_state.show_edit_assignment = False
            st.session_state.current_assignment = None
            st.rerun()
        else:
            st.error("❌ 作业更新失败，请重试")
            
    except Exception as e:
        st.error(f"❌ 更新作业时发生错误：{str(e)}")


def handle_update_teacher_comments(submission_id, new_comments):
    """处理更新教师评语逻辑"""
    db = get_db_manager()
    
    try:
        # 更新教师评语
        result = db.update_teacher_comments(
            submission_id,
            new_comments,
            st.session_state.user_id  # 记录批改教师
        )
        
        if result:
            st.success("✅ 评语更新成功！")
            # 清除编辑状态
            st.session_state[f'editing_submission_{submission_id}'] = False
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ 评语更新失败，请重试")
            
    except Exception as e:
        st.error(f"❌ 更新评语时发生错误：{str(e)}")


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


def render_submission_view():
    """渲染作业提交情况视图"""
    assignment = st.session_state.get('current_assignment')
    
    if not assignment:
        st.error("未找到作业信息")
        return
    
    # 返回按钮
    if st.button("← 返回作业列表", key="back_to_assignments"):
        st.session_state.show_submissions = False
        st.session_state.current_assignment = None
        st.rerun()
    
    st.markdown(f"### 👁️ {assignment['assignment_title']} - 提交情况")
    
    # 作业信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("作业编号", assignment['assignment_number'])
    with col2:
        st.metric("总分值", f"{assignment['total_score']}分")
    with col3:
        st.metric("截止时间", str(assignment['due_date']))
    
    st.divider()
    
    # 获取提交记录
    db = get_db_manager()
    submissions = db.get_assignment_submissions(assignment['assignment_id'])
    
    if not submissions:
        st.info("📭 暂无学生提交")
        return
    
    # 统计信息
    total_students = len(submissions)
    graded_count = sum(1 for s in submissions if s.get('status') == 'graded')
    pending_count = total_students - graded_count
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总提交数", total_students)
    with col2:
        st.metric("已批改", graded_count)
    with col3:
        st.metric("待批改", pending_count)
    
    st.divider()
    
    # 提交列表
    st.markdown("### 📝 提交详情")
    
    for idx, submission in enumerate(submissions):
        with st.expander(
            f"**{submission['student_name']}** - 提交时间：{submission['submit_time']} - 状态：{submission['status']}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**学生姓名：** {submission['student_name']}")
                st.markdown(f"**提交时间：** {submission['submit_time']}")
                st.markdown(f"**状态：** {submission['status']}")
            
            with col2:
                auto_score = submission.get('auto_grade_score')
                teacher_score = submission.get('teacher_grade_score')
                st.metric("AI 评分", f"{auto_score}分" if auto_score else "未评分")
                st.metric("教师评分", f"{teacher_score}分" if teacher_score else "未评分")
            
            # 提交内容
            st.markdown("**📄 提交内容：**")
            st.text_area(
                "",
                value=submission.get('submission_content', ''),
                height=150,
                disabled=True,
                key=f"submission_content_{submission['submission_id']}"
            )
            
            # AI 评语
            if submission.get('auto_grade_comments'):
                st.markdown("**🤖 AI 评语：**")
                st.info(submission['auto_grade_comments'])
            
            # 教师评语
            if submission.get('teacher_comments'):
                st.markdown("**👨‍🏫 教师评语：**")
                st.success(submission['teacher_comments'])


def render_edit_assignment_view():
    """渲染编辑作业视图"""
    assignment = st.session_state.get('current_assignment')
    
    if not assignment:
        st.error("未找到作业信息")
        return
    
    # 返回按钮
    if st.button("← 返回作业列表", key="back_to_assignments_from_edit"):
        st.session_state.show_edit_assignment = False
        st.session_state.current_assignment = None
        st.rerun()
    
    st.markdown(f"### ✏️ 编辑作业 - {assignment['assignment_title']}")
    
    db = get_db_manager()
    
    with st.form(key="edit_assignment_form"):
        # 作业编号（不可编辑）
        st.text_input("作业编号", value=assignment['assignment_number'], disabled=True)
        
        # 第一行：作业标题和课程名称
        col1, col2 = st.columns(2)
        with col1:
            new_title = st.text_input(
                "作业标题",
                value=assignment['assignment_title'],
                key="edit_assignment_title"
            )
        
        with col2:
            new_course = st.text_input(
                "课程名称",
                value=assignment['course_name'],
                key="edit_course_name"
            )
        
        # 第二行：总分和截止时间
        col1, col2 = st.columns(2)
        with col1:
            new_total_score = st.number_input(
                "总分值",
                min_value=1,
                max_value=1000,
                value=int(assignment['total_score']),
                key="edit_total_score"
            )
        
        with col2:
            from datetime import date
            # 转换 due_date 为 date 对象
            due_date_str = str(assignment['due_date'])
            try:
                due_date_val = date.fromisoformat(due_date_str)
            except:
                due_date_val = date.today()
            
            new_due_date = st.date_input(
                "截止时间",
                value=due_date_val,
                key="edit_due_date"
            )
        
        # 作业说明
        new_description = st.text_area(
            "作业说明",
            value=assignment.get('assignment_description', ''),
            height=100,
            key="edit_assignment_description"
        )
        
        # 提交按钮
        submit_button = st.form_submit_button(
            "💾 保存修改",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            handle_edit_assignment(
                assignment['assignment_id'],
                new_title,
                new_course,
                new_total_score,
                new_due_date,
                new_description
            )
