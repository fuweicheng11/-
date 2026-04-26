# Camouflage Insect Web Demo

这是一个面向复杂自然背景的伪装昆虫识别 Web 平台，支持电脑端和手机端访问，提供主体分割、融合分类、证据图解释、科普信息、动态区、图鉴与管理员后台等功能。

当前仓库已经去掉了旧版 `CamouflageInsectWebDemo.exe` 分类依赖，识别链路完全运行在 Python 进程内：

`上传图片 -> 分割模型提取主体 -> 裁切主体 -> ConvNeXt + DINOv2 融合分类 -> 返回证据图与科普信息`

## 技术栈

- 前端：Vue 3 + Vite + Element Plus
- 后端：Flask
- 分割模型：PyTorch 自定义分割网络，部署版以 ResNet50 为编码骨干
- 分类模型：ConvNeXt-Base + DINOv2 + Gating Fusion
- 数据存储：MySQL
- 智能问答：DeepSeek 兼容接口，可留空不配置

## 这个仓库包含什么

仓库包含：

- 完整前后端源码
- 前端构建配置
- 分割与分类推理代码
- 启动脚本
- 分类图鉴、示例图片、业务文案

仓库不包含：

- 分类权重 `runtime/CamouflageDriveQ/08/fusion_results/fusion_best.pth`
- 分割权重 `segmentation/models/MODEL06_RUN_best.pth`
- 本地 MySQL 数据目录
- 本地日志
- 真实 AI API Key
- 前端 `node_modules`
- 前端构建产物 `frontend/dist`

## 部署前必须下载的网盘资源

请从你的百度网盘资源中下载权重包，并解压到项目根目录。

- 百度网盘链接：`https://pan.baidu.com/s/1-6FF0QzGhZPsVbIX7L2Rfw?pwd=1234`
- 提取码：`1234`

推荐你上传一个压缩包，包内保持如下相对路径：

```text
runtime/CamouflageDriveQ/08/fusion_results/fusion_best.pth
segmentation/models/MODEL06_RUN_best.pth
```

只要解压后这两个文件落到上述位置，项目就能识别。

说明：

- `fusion_best.pth`：分类融合权重，必需
- `MODEL06_RUN_best.pth`：分割权重，必需
- `_internal/master/ConvNeXt-main/convnext_base_22k_224.pth`：不是当前部署版运行必需
- `_internal/master/dinov2-main/dinov2_vitb14_reg4_pretrain.pth`：不是当前部署版运行必需

## 环境要求

### Windows 本地运行

推荐环境：

- Python 3.10 - 3.12
- Node.js 18+
- MySQL 8.4
- PowerShell 可用

注意：

- Windows 一键脚本默认寻找 `C:\Program Files\MySQL\MySQL Server 8.4`
- 如果你的 MySQL 不在这个路径，请手动修改 `scripts/setup_local_mysql.ps1`

### Linux / 服务器部署

推荐环境：

- Python 3.10 - 3.12
- Node.js 18+
- MySQL 8.x
- Nginx

## 首次部署步骤

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd <repo-dir>
```

### 2. 还原模型权重

把百度网盘中的权重包解压到项目根目录，确认以下两个文件存在：

```text
runtime/CamouflageDriveQ/08/fusion_results/fusion_best.pth
segmentation/models/MODEL06_RUN_best.pth
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 安装前端依赖并构建

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. 配置数据库

项目默认数据库配置如下：

- host：`127.0.0.1`
- port：`3306`
- user：`camouflage_app`
- password：`Camouflage@2026`
- database：`camouflage_insect_app`

你可以用两种方式之一：

1. Windows 本地直接运行 `launch_mini_app.bat`，脚本会尝试自动初始化本地 MySQL
2. 手动创建 MySQL 数据库，并复制 `runtime/mysql/app_db.example.json` 为 `runtime/mysql/app_db.json`

也可以直接使用环境变量覆盖：

- `CAMOUFLAGE_DB_HOST`
- `CAMOUFLAGE_DB_PORT`
- `CAMOUFLAGE_DB_USER`
- `CAMOUFLAGE_DB_PASSWORD`
- `CAMOUFLAGE_DB_NAME`

### 6. 可选配置 AI 问答

如果不配置 API Key，项目仍然可以运行，只是智能问答会退化为本地兜底回答。

配置方式：

1. 复制 `runtime/ai_config.example.json` 为 `runtime/ai_config.json`
2. 填入你自己的 Key

也可以直接使用环境变量：

- `CAMOUFLAGE_AI_PROVIDER`
- `CAMOUFLAGE_AI_BASE`
- `CAMOUFLAGE_AI_MODEL`
- `CAMOUFLAGE_AI_KEY`
- `DEEPSEEK_API_KEY`
- `CAMOUFLAGE_AI_TEMPERATURE`

## 启动方式

### Windows 一键启动

```bat
launch_mini_app.bat
```

默认地址：

```text
http://127.0.0.1:7863
```

停止：

```bat
stop_mini_app.bat
```

生成手机临时访问地址：

```bat
launch_phone_access.bat
```

### 通用手动启动

```bash
python app.py
```

### 生产环境启动

```bash
gunicorn -w 1 -b 127.0.0.1:7863 app:app
```

或者：

```bash
waitress-serve --host=127.0.0.1 --port=7863 app:app
```

## 前端开发

开发模式：

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器会把 `/api` 等请求代理到 `http://127.0.0.1:7863`。

## 常见问题

### 1. 页面能打开，但识别报错

优先检查：

- `fusion_best.pth` 是否放对位置
- `MODEL06_RUN_best.pth` 是否放对位置
- Python 依赖是否完整安装

### 2. 页面数据加载失败，提示 MySQL 连接不上

检查：

- MySQL 是否已启动
- `runtime/mysql/app_db.json` 是否正确
- 数据库 `camouflage_insect_app` 是否存在

Windows 本地可以优先直接试：

```bat
launch_mini_app.bat
```

### 3. 问答功能不可用

通常是没有配置 AI Key。这个不影响主识别链路。

## 项目结构

```text
.
├─ app.py
├─ wsgi.py
├─ requirements.txt
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  ├─ package-lock.json
│  └─ vite.config.js
├─ webapp/
├─ segmentation/
│  ├─ alg06_run/
│  └─ models/
├─ runtime/
│  ├─ CamouflageDriveQ/
│  ├─ mysql/
│  └─ ai_config.example.json
├─ scripts/
├─ _internal/
├─ launch_mini_app.bat
├─ launch_phone_access.bat
└─ stop_mini_app.bat
```

## 发布说明

这个仓库适合公开托管源码和交接部署，不适合直接存放超大权重、数据库数据和真实 API 密钥。

如果你要复现完整效果，正确流程是：

1. 克隆源码仓库
2. 从百度网盘下载权重包
3. 安装 Python / Node.js / MySQL
4. 构建前端
5. 启动项目

按本 README 操作，接手者可以完成完整部署。
