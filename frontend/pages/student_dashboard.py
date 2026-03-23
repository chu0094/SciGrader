"""
SciGrader 学生端仪表盘
功能：我的作业、提交作业、批改后作业、学习统计
"""
import streamlit as st
from utils.db_utils import get_db_manager, logout
from datetime import datetime, date
import requests


def student_dashboard():
    """学生端主界面"""
    
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
        <div class="top-navbar" style="background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);">
            <div class="navbar-title">📚 SciGrader 学生端</div>
            <div class="navbar-user">
                <span>👤 {user_info['username']} / 学生</span>
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
    
    # 1. 我的作业模块
    render_my_assignments_section()
    
    st.divider()
    
    # 2. 批改后作业模块
    render_graded_assignments_section()


def render_my_assignments_section():
    """渲染我的作业列表"""
    st.markdown("### 📝 我的作业")
    
    db = get_db_manager()
    assignments = db.get_all_assignments()
    
    if not assignments:
        st.info("暂无发布的作业")
        return
    
    # 获取学生的提交记录
    submissions = db.get_student_submissions(st.session_state.user_id)
    submitted_ids = {s['assignment_id'] for s in submissions}
    
    for assignment in assignments:
        # 判断作业状态
        status = determine_assignment_status(assignment, assignment['assignment_id'] in submitted_ids)
        render_student_assignment_card(assignment, status)


def determine_assignment_status(assignment, is_submitted):
    """判断作业状态"""
    today = date.today()
    due_date = assignment['due_date']
    
    if is_submitted:
        return 'submitted'
    elif today > due_date:
        return 'overdue'
    else:
        return 'pending'


def render_student_assignment_card(assignment, status):
    """渲染学生端作业卡片"""
    status_labels = {
        'pending': ('待提交', '🟡'),
        'submitted': ('已提交', '🟢'),
        'overdue': ('已逾期', '🔴')
    }
    
    status_label, status_icon = status_labels.get(status, ('未知', '⚪'))
    
    with st.container():
        st.markdown(f"""
            <div class="assignment-card {status}" style="
                margin-bottom: 16px;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            ">
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**📖 课程名称：** {assignment.get('course_name', '未指定')}")
            st.markdown(f"**📋 作业标题：** {assignment['assignment_title']}")
        
        with col2:
            st.markdown(f"**📅 截止时间：** {assignment['due_date']}")
            st.markdown(f"**💯 作业分值：** {assignment['total_score']}分")
        
        with col3:
            st.markdown(f"**状态：** {status_icon} {status_label}")
            st.markdown(f"**编号：** {assignment['assignment_number']}")
        
        # 操作按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if status == 'pending':
                if st.button("📤 提交作业", key=f"submit_{assignment['assignment_id']}", use_container_width=True):
                    st.session_state.show_submit_modal = assignment['assignment_id']
                    st.rerun()
            elif status == 'submitted':
                if st.button("👁️ 查看提交", key=f"view_{assignment['assignment_id']}", use_container_width=True):
                    st.session_state.show_view_submission = assignment['assignment_id']
                    st.rerun()
                # ⭐ 新增：重新提交按钮
                if st.button("🔄 重新提交", key=f"resubmit_{assignment['assignment_id']}", use_container_width=True):
                    st.session_state.show_resubmit_modal = assignment['assignment_id']
                    st.rerun()
            else:  # overdue
                if st.button("📤 补交作业", key=f"late_{assignment['assignment_id']}", use_container_width=True):
                    st.session_state.show_submit_modal = assignment['assignment_id']
                    st.rerun()
        
        with col2:
            if st.button("📋 查看详情", key=f"details_{assignment['assignment_id']}", use_container_width=True):
                st.session_state.show_assignment_details = assignment['assignment_id']
                st.rerun()
        
        with col3:
            # 占位或添加其他功能按钮
            st.markdown("")
        
        # 显示提交对话框
        if st.session_state.get('show_submit_modal') == assignment['assignment_id']:
            show_submit_dialog(assignment)
        
        # 显示查看提交对话框
        if st.session_state.get('show_view_submission') == assignment['assignment_id']:
            show_view_submission_dialog(assignment)
        
        # ⭐ 新增：显示重新提交对话框
        if st.session_state.get('show_resubmit_modal') == assignment['assignment_id']:
            show_resubmit_dialog(assignment)
        
        # 显示作业详情对话框 ⭐ 新增
        if st.session_state.get('show_assignment_details') == assignment['assignment_id']:
            show_assignment_details_dialog(assignment)


def show_submit_dialog(assignment):
    """显示提交作业对话框"""
    st.warning(f"正在提交作业：{assignment['assignment_title']}")
    
    with st.form(key=f"submit_form_{assignment['assignment_id']}"):
        submission_content = st.text_area(
            "作答内容",
            placeholder="请输入你的答案（支持文本、公式、代码）",
            height=200,
            key=f"submission_content_{assignment['assignment_id']}"
        )
        
        uploaded_files = st.file_uploader(
            "附件上传（可选）",
            type=["pdf", "png", "jpg", "txt", "py", "java", "cpp"],
            accept_multiple_files=True,
            key=f"upload_{assignment['assignment_id']}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("✅ 确认提交", use_container_width=True, type="primary")
        with col2:
            cancel_button = st.form_submit_button("❌ 取消", use_container_width=True)
        
        if submit_button:
            handle_submit_assignment(assignment, submission_content, uploaded_files)
        
        if cancel_button:
            st.session_state.show_submit_modal = None
            st.rerun()


def show_resubmit_dialog(assignment):
    """显示重新提交作业对话框 ⭐"""
    st.warning(f"🔄 重新提交作业：{assignment['assignment_title']}")
    st.info("⚠️ 注意：重新提交将覆盖之前的提交记录和 AI 批改结果")
    
    # 获取之前的提交记录
    db = get_db_manager()
    submissions = db.get_student_submissions(st.session_state.user_id)
    previous_submission = next((s for s in submissions if s['assignment_id'] == assignment['assignment_id']), None)
    
    if previous_submission:
        with st.expander("👁️ 查看之前的提交", expanded=False):
            st.text_area("之前的答案", previous_submission.get('submission_content', ''), disabled=True, height=100)
            st.markdown(f"**提交时间：** {previous_submission['submit_time']}")
            st.markdown(f"**AI 评分：** {previous_submission.get('auto_grade_score', '未评分')}分")
    
    with st.form(key=f"resubmit_form_{assignment['assignment_id']}"):
        submission_content = st.text_area(
            "新的作答内容",
            placeholder="请输入你的新答案（支持文本、公式、代码）",
            height=200,
            key=f"resubmission_content_{assignment['assignment_id']}"
        )
        
        uploaded_files = st.file_uploader(
            "附件上传（可选）",
            type=["pdf", "png", "jpg", "txt", "py", "java", "cpp"],
            accept_multiple_files=True,
            key=f"resubmit_upload_{assignment['assignment_id']}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("✅ 确认重新提交", use_container_width=True, type="primary")
        with col2:
            cancel_button = st.form_submit_button("❌ 取消", use_container_width=True)
        
        if submit_button:
            handle_resubmit_assignment(assignment, submission_content, uploaded_files, previous_submission)
        
        if cancel_button:
            st.session_state.show_resubmit_modal = None
            st.rerun()


def handle_submit_assignment(assignment, content, files):
    """处理提交作业逻辑 - 调用后端 AI 批改 API ⭐"""
    import json
    
    if not content:
        st.error("请填写作答内容")
        return
    
    db = get_db_manager()
    
    # 处理文件信息
    file_list = []
    if files:
        for f in files:
            file_list.append({
                "name": f.name,
                "size": f.size,
                "type": f.type
            })
    
    # 判断是否逾期
    today = date.today()
    status = 'late' if today > assignment['due_date'] else 'submitted'
    
    # 转换为 JSON 格式（MySQL JSON 字段要求）
    try:
        files_json = json.dumps(file_list, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        st.error(f"数据格式错误：{e}")
        return
    
    submission_data = (
        assignment['assignment_id'],
        st.session_state.user_id,
        content,
        files_json,
        status
    )
    
    result = db.create_submission(submission_data)
    
    if result:
        st.success("✓ 作业提交成功！")
        st.balloons()
        
        # ⭐ 新增：调用后端 AI 批改 API
        try:
            # 🤖 显示 AI 批改进度提示 - ⭐ 修改：增加预计时间提示
            with st.spinner('🤖 AI 正在批改中，请稍候...（预计需要 1-2 分钟）'):
                ai_grade_result = call_backend_ai_grading(assignment, content, result)
            
            # ⭐ 修改：检查是否是待处理状态
            if ai_grade_result.get('pending'):
                st.warning("⏱️ AI 批改正在进行中，请稍后刷新页面查看结果")
                st.info("💡 批改完成后会自动更新成绩，您可以继续浏览其他内容")
            else:
                # ✅ 显示批改结果
                st.success(f"✅ AI 批改完成！评分：{ai_grade_result['score']}分")
                
                # ⭐ 新增：显示批改耗时
                if 'grading_time' in ai_grade_result:
                    grading_time = ai_grade_result['grading_time']
                    if grading_time >= 60:
                        st.info(f"⏱️ 批改耗时：{grading_time/60:.1f} 分钟")
                    else:
                        st.info(f"⏱️ 批改耗时：{grading_time:.1f} 秒")
                
                # 更新提交状态为 'graded'
                with st.spinner('📝 正在更新成绩...'):
                    update_result = update_submission_grade(result, ai_grade_result)
                
                if update_result:
                    st.info(f"💯 最终得分：{ai_grade_result['score']}分")
                    if ai_grade_result.get('comments'):
                        st.info(f"💬 AI 评语：{ai_grade_result['comments']}")
                    st.success("✅ 成绩已更新到数据库！")
                else:
                    st.error("❌ 成绩更新失败！请刷新页面重试。")
                
        except Exception as e:
            error_msg = str(e)
            st.warning(f"⚠️ AI 批改异常：{error_msg}")
            st.info("💡 作业已成功提交，但 AI 批改失败。请联系教师或稍后重试。")
            # 不抛出异常，让用户可以看到友好提示
        
        st.session_state.show_submit_modal = None
        st.rerun()
    else:
        st.error("✗ 提交失败，请重试")


def handle_resubmit_assignment(assignment, content, files, previous_submission):
    """处理重新提交作业逻辑 - 调用后端 AI 批改 API ⭐"""
    import json
    
    if not content:
        st.error("请填写作答内容")
        return
    
    db = get_db_manager()
    
    # 处理文件信息
    file_list = []
    if files:
        for f in files:
            file_list.append({
                "name": f.name,
                "size": f.size,
                "type": f.type
            })
    
    # 判断是否逾期
    today = date.today()
    status = 'late' if today > assignment['due_date'] else 'submitted'
    
    # 转换为 JSON 格式（MySQL JSON 字段要求）
    try:
        files_json = json.dumps(file_list, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        st.error(f"数据格式错误：{e}")
        return
    
    # ⭐ 修改：只传递需要更新的字段
    submission_data = (
        content,
        files_json,
        status
    )
    
    # ⭐ 修改：update_submission 返回的是受影响行数，不是 submission_id
    # 需要使用之前提交的 ID
    update_result = db.update_submission(submission_data, previous_submission['submission_id'])
    
    if update_result:
        st.success("✓ 作业重新提交成功！")
        st.balloons()
        
        # ⭐ 新增：调用后端 AI 批改 API
        try:
            # ⭐ 修改：使用 previous_submission['submission_id'] 而不是 result
            with st.spinner('🤖 AI 正在批改中，请稍候...（预计需要 1-2 分钟）'):
                ai_grade_result = call_backend_ai_grading(assignment, content, previous_submission['submission_id'])
            
            # ⭐ 修改：检查是否是待处理状态
            if ai_grade_result.get('pending'):
                st.warning("⏱️ AI 批改正在进行中，请稍后刷新页面查看结果")
                st.info("💡 批改完成后会自动更新成绩")
            else:
                # 更新提交状态为 'graded'
                update_submission_grade(previous_submission['submission_id'], ai_grade_result)
                
                st.info(f"🤖 AI 评分：{ai_grade_result['score']}分")
                if ai_grade_result.get('comments'):
                    st.info(f"💬 AI 评语：{ai_grade_result['comments']}")
                
                # ⭐ 新增：显示批改耗时
                if 'grading_time' in ai_grade_result:
                    grading_time = ai_grade_result['grading_time']
                    if grading_time >= 60:
                        st.info(f"⏱️ 批改耗时：{grading_time/60:.1f} 分钟")
                    else:
                        st.info(f"⏱️ 批改耗时：{grading_time:.1f} 秒")
        except Exception as e:
            st.warning(f"⚠️ AI 批改失败：{str(e)}，请稍后重试或联系教师")
        
        st.session_state.show_resubmit_modal = None
        st.rerun()
    else:
        st.error("✗ 重新提交失败，请重试")


def call_backend_ai_grading(assignment, content, submission_id):
    """调用后端 AI 批改 API ⭐"""
    # 后端 API 地址 ⭐ 根据实际运行端口调整
    # backend_url = "http://localhost:8000/ai_grading/submit"
    # ⭐ 修改：从 secrets.toml 读取后端地址
    backend_url = st.secrets.get("BACKEND_URL", "https://scigrader.onrender.com") + "/ai_grading/submit"
    
    # 获取作业包含的所有题目
    db = get_db_manager()
    problems = db.get_assignment_problems(assignment['assignment_id'])
    
    if not problems:
        return {"score": 0, "comments": "该作业没有题目"}
    
    # 构建请求数据
    request_data = {
        "submission_id": str(submission_id),
        "assignment_id": assignment['assignment_id'],
        "student_id": st.session_state.user_id,
        "content": content,
        "problems": []
    }
    
    # 添加题目信息
    for problem in problems:
        problem_data = {
            "problem_id": problem['problem_id'],
            "problem_number": problem['problem_number'],
            "problem_type": problem['problem_type'],
            "difficulty_level": problem['difficulty_level'],
            "description": problem['description'],
            "reference_answer": problem.get('reference_answer', ''),
            "max_score": problem['max_score']
        }
        request_data["problems"].append(problem_data)
    
    # 发送 POST 请求到后端
    try:
        # ⭐ 修改：增加超时时间，给 AI 批改更多时间
        response = requests.post(backend_url, json=request_data, timeout=600)
        response.raise_for_status()
        
        # 解析响应
        grading_result = response.json()
        
        # 提取评分和评语
        total_score = grading_result.get('total_score', 0)
        comments = grading_result.get('comments', '')
        
        return {
            "score": total_score,
            "comments": comments,
            "graded_at": date.today().strftime("%Y-%m-%d")
        }
        
    except requests.exceptions.Timeout:
        # ⭐ 新增：超时错误处理
        st.error("⏱️ AI 批改超时！批改时间较长，请稍后查看结果。")
        st.info("💡 作业已成功提交，AI 正在后台批改中。请刷新页面或前往'批改后作业'查看结果。")
        # 返回一个默认结果，避免流程中断
        return {
            "score": 0,
            "comments": "批改中，请稍后查看",
            "graded_at": date.today().strftime("%Y-%m-%d"),
            "pending": True  # 标记为待处理
        }
    except requests.exceptions.RequestException as e:
        st.info("💡 作业已成功提交，但 AI 批改失败。请联系教师或稍后重试。")
        # 不抛出异常，让用户可以看到友好提示

def update_submission_grade(submission_id, grade_result):
    """更新提交评分 ⭐ 新增"""
    db = get_db_manager()
    
    query = """
        UPDATE submissions 
        SET status = 'graded',
            auto_grade_score = %s,
            auto_grade_comments = %s,
            graded_at = %s
        WHERE submission_id = %s
    """
    
    params = (
        float(grade_result['score']),  # 确保是浮点数
        str(grade_result['comments']),  # 确保是字符串
        str(grade_result['graded_at']),  # 确保是字符串
        int(submission_id)  # 确保是整数
    )
    
    try:
        result = db.execute_query(query, params)
        if result:
            return True
        else:
            return False
    except Exception as e:
        # 记录错误但不抛出，让调用方处理
        return False


def show_assignment_details_dialog(assignment):
    """显示作业详情对话框 ⭐ 新增"""
    st.markdown(f"### 📋 {assignment['assignment_title']} - 作业详情")
    
    db = get_db_manager()
    
    # 获取作业包含的题目列表
    problems = db.get_assignment_problems(assignment['assignment_id'])
    
    # 作业基本信息
    with st.expander("📝 作业基本信息", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**课程名称：** {assignment.get('course_name', '未指定')}")
            st.markdown(f"**作业编号：** {assignment['assignment_number']}")
            st.markdown(f"**发布时间：** {assignment['publish_date']}")
        
        with col2:
            st.markdown(f"**总分值：** {assignment['total_score']}分")
            st.markdown(f"**截止时间：** {assignment['due_date']}")
            
            # 计算剩余时间
            from datetime import datetime, date
            today = date.today()
            due_date = assignment['due_date']
            days_left = (due_date - today).days
            
            if days_left < 0:
                st.markdown(f"**状态：** 🔴 已逾期 {-days_left} 天")
            elif days_left == 0:
                st.markdown(f"**状态：** 🟡 今天截止")
            else:
                st.markdown(f"**状态：** 🟢 剩余 {days_left} 天")
        
        if assignment.get('assignment_description'):
            st.divider()
            st.markdown("**作业说明：**")
            st.info(assignment['assignment_description'])
    
    # 题目列表
    if problems:
        st.markdown(f"### 📚 题目列表（共 {len(problems)} 题）")
        
        for idx, problem in enumerate(problems, 1):
            with st.expander(f"**题目{idx}:** {problem['problem_number']} - {problem['problem_title']}"):
                # 题目基本信息
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    type_map = {
                        "concept": "概念题",
                        "calculation": "计算题",
                        "programming": "编程题"
                    }
                    st.markdown(f"**类型：** {type_map.get(problem['problem_type'], '未知')}")
                
                with col2:
                    difficulty_map = {
                        "easy": "简单",
                        "medium": "中等",
                        "hard": "困难"
                    }
                    st.markdown(f"**难度：** {difficulty_map.get(problem['difficulty_level'], '未知')}")
                
                with col3:
                    st.markdown(f"**分值：** {problem['max_score']}分")
                
                st.divider()
                
                # 题目内容
                st.markdown("**题目内容：**")
                st.write(problem['description'])
                
                # 如果有参考答案，使用折叠显示（避免在 dialog 中使用 expander）
                if problem.get('reference_answer'):
                    st.info(f"**参考答案：**\n\n{problem['reference_answer']}")
                
                # 知识点标签
                if problem.get('knowledge_points'):
                    import json
                    try:
                        kps = json.loads(problem['knowledge_points'])
                        if kps:
                            st.divider()
                            st.markdown("**知识点：**")
                            kp_tags = " ".join([f"`{kp}`" for kp in kps])
                            st.markdown(kp_tags)
                    except:
                        pass
                
                # 附件信息
                if problem.get('attachments'):
                    import json
                    try:
                        attachments = json.loads(problem['attachments'])
                        if attachments:
                            st.divider()
                            st.markdown("**附件：**")
                            for att in attachments:
                                st.markdown(f"📎 {att.get('name', '未知文件')} ({att.get('size', 0)} bytes)")
                    except:
                        pass
    else:
        st.warning("该作业还没有添加题目")
    
    # 关闭按钮
    st.divider()
    if st.button("❌ 关闭", key=f"close_details_{assignment['assignment_id']}", use_container_width=True):
        st.session_state.show_assignment_details = None
        st.rerun()


def show_view_submission_dialog(assignment):
    """显示查看已提交作业对话框"""
    st.info(f"查看提交：{assignment['assignment_title']}")
    
    db = get_db_manager()
    submissions = db.get_student_submissions(st.session_state.user_id)
    submission = next((s for s in submissions if s['assignment_id'] == assignment['assignment_id']), None)
    
    if submission:
        st.text_area("提交内容", submission.get('submission_content', ''), disabled=True)
        
        if submission.get('submission_files'):
            st.markdown("**附件：**")
            st.code(submission['submission_files'])
        
        st.markdown(f"**提交时间：** {submission['submit_time']}")
        st.markdown(f"**状态：** {submission['status']}")
    else:
        st.error("未找到提交记录")
    
    if st.button("关闭", key="close_view"):
        st.session_state.show_view_submission = None
        st.rerun()


def render_graded_assignments_section():
    """渲染批改后作业模块"""
    st.markdown("### ✅ 批改后作业")
    
    db = get_db_manager()
    graded_assignments = db.get_graded_assignments(st.session_state.user_id)
    
    if not graded_assignments:
        st.info("暂无批改完成的作业")
        return
    
    for work in graded_assignments:
        with st.expander(f"**{work['assignment_title']}** - 批改详情", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**作业编号：** {work['assignment_number']}")
                st.markdown(f"**学生姓名：** {work['student_name']}")
                st.markdown(f"**批改时间：** {work['graded_at']}")
            
            with col2:
                score = work.get('auto_grade_score') or work.get('teacher_grade_score')
                st.metric("系统评分", f"{score}分" if score else "未评分")
            
            if work.get('submission_content'):
                st.text_area("提交答案", work['submission_content'], disabled=True, height=100,
                           key=f"submission_{work.get('submission_id', hash(work['assignment_title']))}")
            
            if work.get('auto_grade_comments'):
                st.text_area("系统评语", work['auto_grade_comments'], disabled=True, height=80,
                           key=f"auto_{work.get('submission_id', hash(work['assignment_title']))}")
            
            if work.get('teacher_comments'):
                st.text_area("教师评语", work['teacher_comments'], disabled=True, height=80,
                           key=f"teacher_{work.get('submission_id', hash(work['assignment_title']))}")


def render_right_panel(user_info):
    """渲染右侧学习统计面板"""
    
    # 学习统计卡片
    st.markdown("### 📊 学习统计")
    
    db = get_db_manager()
    stats = db.get_student_statistics(st.session_state.user_id)
    
    if stats:
        # 统计卡片
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin-bottom: 16px;
                ">
                    <div style="font-size: 36px; font-weight: 700;">{stats.get('total_assignments', 0)}</div>
                    <div style="font-size: 14px; opacity: 0.9;">总作业数</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            completed = stats.get('completed_assignments', 0)
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin-bottom: 16px;
                ">
                    <div style="font-size: 36px; font-weight: 700;">{completed}</div>
                    <div style="font-size: 14px; opacity: 0.9;">已完成</div>
                </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            pending = stats.get('pending_assignments', 0)
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin-bottom: 16px;
                ">
                    <div style="font-size: 36px; font-weight: 700;">{pending}</div>
                    <div style="font-size: 14px; opacity: 0.9;">待提交</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            overdue = stats.get('overdue_assignments', 0)
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin-bottom: 16px;
                ">
                    <div style="font-size: 36px; font-weight: 700;">{overdue}</div>
                    <div style="font-size: 14px; opacity: 0.9;">已逾期</div>
                </div>
            """, unsafe_allow_html=True)
        
        # 平均分
        avg_score = stats.get('average_score')
        if avg_score:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    color: #333;
                    padding: 15px;
                    border-radius: 12px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; font-weight: 700; color: #2E7D32;">{avg_score:.1f}分</div>
                    <div style="font-size: 14px;">平均得分</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("暂无统计数据")
    
    st.divider()
    
    # 系统信息
    st.markdown("### ℹ️ 个人信息")
    
    st.markdown(f"""
        <div style="background-color: #F5F5F5; padding: 15px; border-radius: 8px;">
            <p><strong>用户名：</strong> {user_info['username']}</p>
            <p><strong>角色：</strong> 学生</p>
            <p><strong>邮箱：</strong> {user_info.get('email', '未设置')}</p>
        </div>
    """, unsafe_allow_html=True)
