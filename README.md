# 伪装昆虫识别平台源码说明

- GitHub 这里只放源码，不放模型权重、不放本地 MySQL 数据、不放真实 API Key。
- 想把项目直接跑起来，先去百度网盘把权重包拿下来，再按下面的步骤部署。

## 项目现在做什么

这是一个面向复杂自然背景的伪装昆虫识别 Web 平台，支持电脑端和手机端访问。

当前主链路：

`上传图片 -> 分割模型提取主体 -> 裁切主体 -> ConvNeXt + DINOv2 融合分类 -> 返回类别、证据图、科普信息`

项目当前包含这些功能：

- 结果页展示原图、分割图、热力图、定位框结果、局部热力图
- 首页动态区
- 分类图鉴
- 用户登录、头像、历史记录
- 管理员后台
- DeepSeek 问答接口

## 技术栈

- 前端：Vue 3 + Vite + Element Plus
- 后端：Flask
- 分割模型：PyTorch 自定义分割网络，部署版编码骨干为 ResNet50
- 分类模型：ConvNeXt-Base + DINOv2 + Gating Fusion
- 数据存储：MySQL
- 问答：DeepSeek 兼容接口，可不配置

## GitHub 里有什么，没什么

仓库内包含：

- 完整前后端源码
- 前端构建配置
- 启动脚本
- 示例图片
- 图鉴数据和业务文案
- 分割与分类推理代码

仓库内不包含：

- 分类权重 `runtime/CamouflageDriveQ/08/fusion_results/fusion_best.pth`
- 分割权重 `segmentation/models/MODEL06_RUN_best.pth`
- 本地 MySQL 数据目录
- 本地日志
- 真实 AI Key
- `frontend/node_modules`
- `frontend/dist`

所以刚 clone 下来时，不能指望项目裸跑就能识别，权重必须先补回来。

## 权重包获取方式

部署必需的大文件已经单独放到百度网盘。

- 百度网盘链接：`https://pan.baidu.com/s/1-6FF0QzGhZPsVbIX7L2Rfw?pwd=1234`
- 提取码：`1234`

下载后，直接把压缩包解压到项目根目录。压缩包里已经保留了正确的相对路径，正常情况下不需要手动搬文件。

解压后至少确认这两个文件存在：

```text
runtime/CamouflageDriveQ/08/fusion_results/fusion_best.pth
segmentation/models/MODEL06_RUN_best.pth
```

这两个文件缺一个，识别都跑不起来。

补充说明：

- `fusion_best.pth`：分类融合权重，必需
- `MODEL06_RUN_best.pth`：分割权重，必需
- `_internal/master/ConvNeXt-main/convnext_base_22k_224.pth`：当前部署版不是必需
- `_internal/master/dinov2-main/dinov2_vitb14_reg4_pretrain.pth`：当前部署版不是必需

## 推荐部署顺序

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd <repo-dir>
```

### 2. 先还原权重

把百度网盘里的权重包解压到项目根目录，确认上面那两个 `.pth` 文件都在。

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

默认数据库配置如下：

- host：`127.0.0.1`
- port：`3306`
- user：`camouflage_app`
- password：`Camouflage@2026`
- database：`camouflage_insect_app`

有两种方式：

1. Windows 本地直接运行 `launch_mini_app.bat`，脚本会尝试自动初始化本地 MySQL。
2. 手动创建数据库，然后把 `runtime/mysql/app_db.example.json` 复制成 `runtime/mysql/app_db.json`，再把参数改成自己的。

也可以直接用环境变量覆盖：

- `CAMOUFLAGE_DB_HOST`
- `CAMOUFLAGE_DB_PORT`
- `CAMOUFLAGE_DB_USER`
- `CAMOUFLAGE_DB_PASSWORD`
- `CAMOUFLAGE_DB_NAME`

### 6. AI 问答按需配置

不配置 AI Key，主识别链路仍然能跑，只是问答会退化。

如果需要配置：

1. 把 `runtime/ai_config.example.json` 复制成 `runtime/ai_config.json`
2. 填入自己的 Key

也可以直接用环境变量：

- `CAMOUFLAGE_AI_PROVIDER`
- `CAMOUFLAGE_AI_BASE`
- `CAMOUFLAGE_AI_MODEL`
- `CAMOUFLAGE_AI_KEY`
- `DEEPSEEK_API_KEY`
- `CAMOUFLAGE_AI_TEMPERATURE`

## 启动方式

### Windows 本地最省事的方式

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

如果想临时生成手机访问地址：

```bat
launch_phone_access.bat
```

### 手动启动

```bash
python app.py
```

### 服务器部署

```bash
gunicorn -w 1 -b 127.0.0.1:7863 app:app
```

或者：

```bash
waitress-serve --host=127.0.0.1 --port=7863 app:app
```

生产环境建议自行挂 Nginx 做反向代理。

## 前端开发

开发模式：

```bash
cd frontend
npm install
npm run dev
```

Vite 会把 `/api` 等请求代理到 `http://127.0.0.1:7863`。

## 常见问题

### 1. 页面能打开，但识别报错

先检查：

- `fusion_best.pth` 有没有放对位置
- `MODEL06_RUN_best.pth` 有没有放对位置
- Python 依赖有没有装全

### 2. 页面数据加载失败，提示 MySQL 连不上

优先检查：

- MySQL 是否启动
- `runtime/mysql/app_db.json` 是否正确
- `camouflage_insect_app` 这个库是否存在

Windows 本地优先直接试：

```bat
launch_mini_app.bat
```

### 3. 问答功能不能用

大多数情况是没有配置 AI Key。这个问题不影响识别主链路。

### 4. 想重新推 GitHub，但担心把大文件带上去

当前 `.gitignore` 已经排掉以下内容：

- 模型权重
- MySQL 数据目录
- 日志
- 本地 AI 配置
- `node_modules`
- `frontend/dist`

正常按当前仓库结构推送，不会把这些大文件一起带上去。

## 目录结构

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

## 最后再强调一遍


如果要复现完整效果，顺序就是这五步：

1. clone 源码
2. 解压百度网盘里的权重包
3. 安装 Python / Node.js / MySQL
4. 构建前端
5. 启动项目

不要跳步骤，尤其不要忘记先补权重。

