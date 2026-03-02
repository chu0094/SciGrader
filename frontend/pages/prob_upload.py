import streamlit as st
import requests
import os
import time
from utils import *
import hashlib
from datetime import datetime
import json

# --- 页面基础设置 ---
st.set_page_config(
    page_title="上传作业题目 -作业核查系统", 
    layout="wide",
    page_icon="📂"
)

KNOWLEDGE_BASE_DIR = "knowledge_bases"
KNOWLEDGE_BASE_CONFIG = "knowledge_base_config.json"

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

/* 上传区域容器 */
.upload-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}}

.upload-header {{
    text-align: center;
    margin-bottom: 3rem;
}}

.upload-title {{
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6, #00F5D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
}}

.upload-subtitle {{
    color: #94A3B8;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}}

/*拖拽上传区域 */
.drag-drop-area {{
    background: rgba(30, 41, 59, 0.7);
    border: 3px dashed #00D4FF;
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    margin: 2rem 0;
    transition: all 0.3s ease;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
}}

.drag-drop-area:hover {{
    border-color: #00F5D4;
    transform: translateY(-5px);
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4), 0 0 30px rgba(0, 245, 212, 0.3);
}}

.drag-drop-area.active {{
    border-color: #8B5CF6;
    background: rgba(139, 92, 246, 0.1);
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4), 0 0 40px rgba(139, 92, 246, 0.3);
}}

.upload-icon {{
    font-size: 4rem;
    color: #00D4FF;
    margin-bottom: 1.5rem;
    filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5));
}}

.upload-text {{
    color: #F1F5F9;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1rem;
}}

.upload-hint {{
    color: #94A3B8;
    font-size: 1rem;
    margin-bottom: 2rem;
}}

/*进度条 */
.upload-progress {{
    width: 100%;
    height: 12px;
    background: rgba(30, 41, 59, 0.5);
    border-radius: 6px;
    overflow: hidden;
    margin: 2rem 0;
    border: 1px solid rgba(0, 212, 255, 0.3);
}}

.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #00D4FF, #00F5D4, #8B5CF6);
    border-radius: 6px;
    width: 0%;
    transition: width 0.3s ease;
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

/*表单区域 */
.form-section {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2.5rem;
    margin: 2rem 0;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
}}

.form-title {{
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

.form-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}}

.form-field {{
    margin-bottom: 1.5rem;
}}

.field-label {{
    color: #F1F5F9;
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}}

.field-description {{
    color: #94A3B8;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
}}

/* AI模型配置区域 */
.ai-config {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
}}

.ai-config-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 1.5rem;
    text-align: center;
    background: linear-gradient(135deg, #8B5CF6, #00D4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.model-selector {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}}

.model-card {{
    background: rgba(30, 41, 59, 0.5);
    border: 2px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
}}

.model-card.selected {{
    border-color: #00D4FF;
    background: rgba(0, 212, 255, 0.15);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}}

.model-icon {{
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
    color: #00D4FF;
}}

.model-name {{
    color: #F1F5F9;
    font-weight: 600;
    margin-bottom: 0.3rem;
}}

.model-desc {{
    color: #94A3B8;
    font-size: 0.85rem;
}}

/*权重调节器 */
.weight-control {{
    margin: 2rem 0;
    padding: 1.5rem;
    background: rgba(15, 23, 42, 0.4);
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.1);
}}

.weight-title {{
    color: #F1F5F9;
    font-weight: 600;
    margin-bottom: 1.2rem;
    text-align: center;
}}

.weight-sliders {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}}

.weight-slider {{
    background: rgba(30, 41, 59, 0.5);
    border-radius: 10px;
    padding: 1.2rem;
    backdrop-filter: blur(8px);
}}

.slider-label {{
    color: #F1F5F9;
    font-weight: 600;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.slider-value {{
    color: #00D4FF;
    font-weight: 700;
    font-size: 1.1rem;
}}

/*确认区域 */
.confirmation-section {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 2.5rem;
    margin: 2rem 0;
    text-align: center;
    backdrop-filter: blur(15px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.3);
}}

.confirmation-title {{
    font-size: 2rem;
    font-weight: 800;
    color: #F1F5F9;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #10B981, #00D4FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.confirmation-desc {{
    color: #94A3B8;
    font-size: 1.1rem;
    margin-bottom: 2rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}}

/*文件预览区域 */
.file-preview {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    backdrop-filter: blur(10px);
}}

.preview-title {{
    color: #F1F5F9;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    text-align: center;
}}

.preview-content {{
    background: rgba(30, 41, 59, 0.5);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid rgba(148, 163, 184, 0.1);
    backdrop-filter: blur(8px);
}}

.file-info {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    margin: 0.5rem 0;
    background: rgba(0, 212, 255, 0.1);
    border-radius: 10px;
    border: 1px solid rgba(0, 212, 255, 0.3);
}}

.file-icon {{
    font-size: 2rem;
    color: #00D4FF;
}}

.file-details {{
    flex: 1;
}}

.file-name {{
    color: #F1F5F9;
    font-weight: 600;
    margin-bottom: 0.3rem;
}}

.file-size {{
    color: #94A3B8;
    font-size: 0.9rem;
}}

/*响应式设计 */
@media (max-width: 768px) {{
    .upload-container {{
        padding: 1rem;
    }}
    
    .upload-title {{
        font-size: 2rem;
    }}
    
    .drag-drop-area {{
        padding: 2rem 1rem;
    }}
    
    .form-grid {{
        grid-template-columns: 1fr;
    }}
    
    .model-selector {{
        grid-template-columns: 1fr;
    }}
    
    .weight-sliders {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 480px) {{
    .upload-title {{
        font-size: 1.6rem;
    }}
    
    .upload-icon {{
        font-size: 3rem;
    }}
    
    .form-section {{
        padding: 1.5rem;
    }}
    
    .ai-config {{
        padding: 1.5rem;
    }}
}}
</style>
""", unsafe_allow_html=True)

def save_knowledge_base_config():
    """Save knowledge base configuration"""
    try:
        with open(KNOWLEDGE_BASE_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.knowledge_bases, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        st.error(f"Failed to save knowledge base configuration: {e}")

def create_knowledge_base(name: str, description: str, category: str = "General"):
    """Create new knowledge base"""
    kb_id = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
    kb_path = os.path.join(KNOWLEDGE_BASE_DIR, kb_id)
    
    if not os.path.exists(kb_path):
        os.makedirs(kb_path)
    
    kb_info = {
        "id": kb_id,
        "name": name,
        "description": description,
        "category": category,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "file_count": 0,
        "total_size": 0,
        "files": {}
    }
    
    st.session_state.knowledge_bases[kb_id] = kb_info
    save_knowledge_base_config()
    return kb_id

def add_file_to_kb(kb_id: str, file_name: str, file_content: bytes, file_type: str = "unknown"):
    """向知识库添加文件"""
    if kb_id not in st.session_state.knowledge_bases:
        return False
    
    kb_path = os.path.join(KNOWLEDGE_BASE_DIR, kb_id)
    file_path = os.path.join(kb_path, file_name)
    
    try:
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 更新配置
        file_id = hashlib.md5((file_name + datetime.now().isoformat()).encode()).hexdigest()[:12]
        file_info = {
            "id": file_id,
            "name": file_name,
            "type": file_type,
            "size": len(file_content),
            "uploaded_at": datetime.now().isoformat(),
            "path": file_path
        }
        
        st.session_state.knowledge_bases[kb_id]["files"][file_id] = file_info
        st.session_state.knowledge_bases[kb_id]["file_count"] += 1
        st.session_state.knowledge_bases[kb_id]["total_size"] += len(file_content)
        st.session_state.knowledge_bases[kb_id]["updated_at"] = datetime.now().isoformat()
        
        save_knowledge_base_config()
        return True
    except Exception as e:
        st.error(f"Failed to add file: {e}")
        return False

def render_upload_header():
    """渲染上传页面头部"""
    st.markdown("""
    <div class="upload-container">
        <div class="upload-header">
            <div class="upload-title">📤上传管理器</div>
            <div class="upload-subtitle">智能识别题目类型，AI自动批改第一步</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_drag_drop_upload():
    """渲染拖拽上传区域"""
    st.markdown("""
    <div class="upload-container">
        <div class="drag-drop-area" id="dropArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">拖拽文件到此处或点击选择</div>
            <div class="upload-hint">支持 PDF、Word、TXT格文件文件</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 文件上传组件
    uploaded_file = st.file_uploader(
        "选择题目文件",
        type=["pdf", "docx", "txt"],
        key="problem_file",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # 模拟上传进度
        progress_bar = st.empty()
        progress_text = st.empty()
        
        for i in range(101):
            progress_bar.progress(i)
            progress_text.text(f"正在处理文件... {i}%")
            time.sleep(0.02)
        
        progress_bar.empty()
        progress_text.empty()
        
        #显示文件信息
        st.success(f"✅ 文件上传成功：{uploaded_file.name}")
        st.session_state.uploaded_problem_file = uploaded_file
        
        # 文件预览
        render_file_preview(uploaded_file)

def render_file_preview(file):
    """渲染文件预览"""
    st.markdown("""
    <div class="file-preview">
        <div class="preview-title">📄 文件预览</div>
        <div class="preview-content">
    """, unsafe_allow_html=True)
    
    # 文件信息显示
    file_size = len(file.getvalue())
    size_unit = "bytes"
    if file_size > 1024 * 1024:
        file_size = round(file_size / (1024 * 1024), 2)
        size_unit = "MB"
    elif file_size > 1024:
        file_size = round(file_size / 1024, 2)
        size_unit = "KB"
    
    st.markdown(f"""
    <div class="file-info">
        <div class="file-icon">📝</div>
        <div class="file-details">
            <div class="file-name">{file.name}</div>
            <div class="file-size">{file_size} {size_unit} • {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_basic_info_form():
    """渲染基本信息表单"""
    st.markdown("""
    <div class="form-section">
        <div class="form-title">📋基本信息配置</div>
        <div class="form-grid">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-field">', unsafe_allow_html=True)
        st.markdown('<div class="field-label">作业名称</div>', unsafe_allow_html=True)
        st.markdown('<div class="field-description">为本次作业设置一个易于识别的名称</div>', unsafe_allow_html=True)
        assignment_name = st.text_input(
            "作业名称",
            placeholder="例如：数据结构期中考试",
            key="assignment_name"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-field">', unsafe_allow_html=True)
        st.markdown('<div class="field-label">课程名称</div>', unsafe_allow_html=True)
        st.markdown('<div class="field-description">关联的课程信息</div>', unsafe_allow_html=True)
        course_name = st.text_input(
            "课程名称",
            placeholder="例如：数据结构与算法",
            key="course_name"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-field">', unsafe_allow_html=True)
        st.markdown('<div class="field-label">截止时间</div>', unsafe_allow_html=True)
        st.markdown('<div class="field-description">设置作业提交截止时间</div>', unsafe_allow_html=True)
        deadline = st.date_input(
            "截止日期",
            value=datetime.now().date(),
            key="deadline"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-field">', unsafe_allow_html=True)
        st.markdown('<div class="field-label">题目类型</div>', unsafe_allow_html=True)
        st.markdown('<div class="field-description">系统将自动识别题目类型</div>', unsafe_allow_html=True)
        question_types = st.multiselect(
            "题目类型",
            ["计算题", "概念题", "证明题", "编程题"],
            default=["计算题", "概念题"],
            key="question_types"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_ai_configuration():
    """渲染AI配置区域"""
    st.markdown("""
    <div class="ai-config">
        <div class="ai-config-title">🤖 AI批改配置</div>
    """, unsafe_allow_html=True)
    
    # AI模型选择
    st.markdown('<div class="field-label">选择AI模型</div>', unsafe_allow_html=True)
    st.markdown('<div class="field-description">选择用于批改的AI模型（可多选）</div>', unsafe_allow_html=True)
    
    models = [
        {"name": "Gemini Pro", "icon": "🔮", "desc": "Google最新大语言模型"},
        {"name": "ChatGPT-4", "icon": "💬", "desc": "OpenAI旗舰模型"},
        {"name": "DeepSeek", "icon": "🔍", "desc": "深度求索大模型"},
        {"name": "Claude", "icon": "🧠", "desc": "Anthropic智能模型"}
    ]
    
    #模型选择网格
    cols = st.columns(4)
    selected_models = []
    
    for i, (model, col) in enumerate(zip(models, cols)):
        with col:
            is_selected = st.checkbox(
                model["name"],
                key=f"model_{i}",
                label_visibility="collapsed"
            )
            
            if is_selected:
                selected_models.append(model["name"])
                st.markdown(f"""
                <div class="model-card selected">
                    <div class="model-icon">{model["icon"]}</div>
                    <div class="model-name">{model["name"]}</div>
                    <div class="model-desc">{model["desc"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="model-card">
                    <div class="model-icon">{model["icon"]}</div>
                    <div class="model-name">{model["name"]}</div>
                    <div class="model-desc">{model["desc"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    #权配置
    if selected_models:
        st.markdown('<div class="weight-control">', unsafe_allow_html=True)
        st.markdown('<div class="weight-title">⚖️模型权重配置</div>', unsafe_allow_html=True)
        
        #计算平均权重
        avg_weight = 100 // len(selected_models)
        weights = {}
        
        st.markdown('<div class="weight-sliders">', unsafe_allow_html=True)
        weight_cols = st.columns(len(selected_models))
        
        for i, (model, col) in enumerate(zip(selected_models, weight_cols)):
            with col:
                weight = st.slider(
                    model,
                    0, 100, avg_weight,
                    key=f"weight_{model}",
                    help=f"设置 {model} 的批改权重"
                )
                weights[model] = weight
                st.markdown(f"""
                <div class="weight-slider">
                    <div class="slider-label">
                        <span>{model}</span>
                        <span class="slider-value">{weight}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_confirmation():
    """渲染确认区域"""
    st.markdown("""
    <div class="confirmation-section">
        <div class="confirmation-title">✅准就绪</div>
        <div class="confirmation-desc">
           所有配置已完成，请确认信息无误后开始AI批改任务
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    #确认按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 开始AI批改", type="primary", use_container_width=True, key="start_grading"):
            if 'uploaded_problem_file' not in st.session_state:
                st.error("❌ 请先上传题目文件")
                return
            
            if not st.session_state.get('assignment_name'):
                st.error("❌ 请填写作业名称")
                return
            
            # 模拟处理过程
            with st.spinner("正在启动AI批改任务..."):
                time.sleep(2)
            
            st.success("✅ AI批改任务已启动！正在跳转到任务监控页面...")
            time.sleep(1)
            st.switch_page("pages/wait_ai_grade.py")

def main():
    """主函数"""
    # 初始化
    initialize_session_state()
    
    #只在开始全新的批改流程时才重置状态
    if 'prob_data' not in st.session_state or not st.session_state.get('prob_data'):
        reset_grading_state()
    
    #渲页面
    render_upload_header()
    render_drag_drop_upload()
    render_basic_info_form()
    render_ai_configuration()
    render_confirmation()

if __name__ == "__main__":
    main()