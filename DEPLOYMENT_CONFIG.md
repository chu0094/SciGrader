# SciGrader 部署配置指南

## 📋 目录
- [本地开发环境配置](#本地开发环境配置)
- [Streamlit Cloud 部署配置](#streamlit-cloud-部署配置)
- [其他云平台部署](#其他云平台部署)
- [配置切换方法](#配置切换方法)

---

## 🖥️ 本地开发环境配置

### 1. Frontend 配置 (`frontend/.streamlit/secrets.toml`)

```toml
[database]
host_local = "localhost"
host_cloud = "your-cloud-db-host.com"
active_host = "host_local"  # 使用本地数据库
port = 3306
user = "root"
password = "你的密码"
database = "scigrader_db"

[backend]
host_local = "localhost"
port_local = 8000
host_cloud = "0.0.0.0"
port_cloud = 8000
mode = "local"  # 本地模式

[frontend]
host_local = "localhost"
port_local = 8501
host_cloud = "0.0.0.0"
port_cloud = 8501
mode = "local"  # 本地模式
```

### 2. Backend 启动（本地模式）

**方式一：使用环境变量**
```bash
# Windows PowerShell
$env:HOST="localhost"; $env:PORT=8000; python backend/start.py

# Linux/Mac
export HOST=localhost PORT=8000 && python backend/start.py
```

**方式二：直接运行（默认本地模式）**
```bash
python backend/start.py
```

### 3. Frontend 启动（本地模式）
```bash
cd frontend
streamlit run app.py
```

---

## ☁️ Streamlit Cloud 部署配置

### 1. Frontend 配置 (`frontend/.streamlit/secrets.toml`)

```toml
[database]
host_local = "localhost"
host_cloud = "your-cloud-db-host.com"  # 修改为你的云数据库地址
active_host = "host_cloud"  # 使用云数据库
port = 3306
user = "your_db_user"
password = "your_db_password"
database = "scigrader_db"

[backend]
host_local = "localhost"
port_local = 8000
host_cloud = "0.0.0.0"  # Streamlit Cloud 需要 0.0.0.0
port_cloud = 8000
mode = "cloud"  # 云服务模式

[frontend]
host_local = "localhost"
port_local = 8501
host_cloud = "0.0.0.0"  # Streamlit Cloud 需要 0.0.0.0
port_cloud = 8501
mode = "cloud"  # 云服务模式
```

### 2. Backend 启动（云服务模式）

在 Streamlit Cloud 或其他云平台上，需要设置环境变量：

**Streamlit Cloud Secrets:**
在 Streamlit Dashboard 的 Settings → Secrets 中添加：
```toml
HOST = "0.0.0.0"
BACKEND_PORT = "8000"
FRONTEND_URLS = "https://your-app-name.streamlit.app"
```

**或者在平台的配置文件中使用：**
```yaml
# render.yaml 或类似配置文件
services:
  - type: web
    envVars:
      - key: HOST
        value: 0.0.0.0
      - key: BACKEND_PORT
        value: 8000
      - key: FRONTEND_URLS
        value: https://your-app-name.streamlit.app
```

---

## 🚀 其他云平台部署

### Render / Railway / Heroku

#### 1. 环境变量配置

在平台的环境变量设置中添加：

```bash
# Host 配置 (必须为 0.0.0.0 以接受外部连接)
HOST=0.0.0.0

# Port 配置 (平台通常会分配端口)
PORT=8000  # 或使用平台分配的端口

# CORS 配置 (允许前端访问)
FRONTEND_URLS=https://your-frontend-domain.com
```

#### 2. `secrets.toml` 配置

```toml
[database]
host_local = "localhost"
host_cloud = "your-render-db-host.railway.app"  # 修改为实际云数据库地址
active_host = "host_cloud"
port = 3306
user = "your_user"
password = "your_password"
database = "scigrader_db"

[backend]
host_local = "localhost"
port_local = 8000
host_cloud = "0.0.0.0"
port_cloud = 8000
mode = "cloud"

[frontend]
host_local = "localhost"
port_local = 8501
host_cloud = "0.0.0.0"
port_cloud = 8501
mode = "cloud"
```

---

## 🔄 配置切换方法

### 方法一：修改 `secrets.toml`（推荐）

**切换到本地模式：**
```toml
[backend]
mode = "local"

[frontend]
mode = "local"

[database]
active_host = "host_local"
```

**切换到云服务模式：**
```toml
[backend]
mode = "cloud"

[frontend]
mode = "cloud"

[database]
active_host = "host_cloud"
```

### 方法二：使用环境变量覆盖

即使在 `secrets.toml` 中配置了 local 模式，也可以通过环境变量临时切换：

```bash
# 临时使用云模式配置
$env:HOST="0.0.0.0"
$env:FRONTEND_URLS="https://your-app.streamlit.app"
python backend/start.py
```

---

## 🔍 配置检查清单

### 本地开发检查
- [ ] `secrets.toml` 中 `mode = "local"`
- [ ] `secrets.toml` 中 `active_host = "host_local"`
- [ ] 数据库在本地运行且可访问
- [ ] Backend 监听 `localhost:8000`
- [ ] Frontend 监听 `localhost:8501`

### 云端部署检查
- [ ] `secrets.toml` 中 `mode = "cloud"`
- [ ] `secrets.toml` 中 `active_host = "host_cloud"`
- [ ] 云数据库地址和密码已正确配置
- [ ] 环境变量 `HOST=0.0.0.0` 已设置
- [ ] 环境变量 `FRONTEND_URLS` 包含前端域名
- [ ] 防火墙/安全组允许相应端口访问

---

## ⚠️ 注意事项

1. **安全性**: 
   - 不要将真实的生产数据库密码提交到 Git
   - 使用 `.gitignore` 忽略 `secrets.toml` 或使用模板文件
   - 在生产环境中使用环境变量管理敏感信息

2. **CORS 配置**:
   - 确保 `FRONTEND_URLS` 包含所有允许的前端域名
   - 多个域名用逗号分隔：`https://app1.com,https://app2.com`

3. **端口冲突**:
   - 本地开发时如遇端口冲突，可通过环境变量修改端口
   - `$env:PORT=9000` (PowerShell) 或 `export PORT=9000` (Linux/Mac)

4. **Streamlit Cloud**:
   - Streamlit Cloud 会自动分配端口，但仍需设置 `HOST=0.0.0.0`
   - 确保在 `.streamlit/secrets.toml` 中配置正确的数据库连接

---

## 📞 故障排查

### 问题：无法连接到数据库
- 检查 `active_host` 是否指向正确的配置
- 验证数据库服务是否运行
- 检查防火墙设置

### 问题：CORS 错误
- 确认 `FRONTEND_URLS` 包含当前前端的完整 URL
- 检查是否有拼写错误或多余的空白字符

### 问题：后端无法访问
- 确认 `HOST` 环境变量设置为 `0.0.0.0` (云) 或 `localhost` (本地)
- 检查端口是否被占用
- 查看日志输出确认服务已启动
