# 伪装昆虫识别平台源码交接说明

这个仓库是我现在这套伪装昆虫识别平台的源码版。

我先把最重要的话说前面：

- GitHub 这里我只放源码，不放大模型权重，不放本地 MySQL 数据，不放真实 API Key。
- 你如果想把项目直接跑起来，先去百度网盘把权重包拿下来，再按下面的步骤做。
- 当前版本已经去掉了老的 `CamouflageInsectWebDemo.exe` 依赖，现在分类和分割都在 Python 进程里跑。

## 这个项目现在是干什么的

这是一个面向复杂自然背景的伪装昆虫识别 Web 平台，电脑端和手机端都能访问。

现在这套主链路是：

`上传图片 -> 分割模型先提主体 -> 裁切主体 -> ConvNeXt + DINOv2 融合分类 -> 返回类别、证据图、科普信息`

除了识别本身，这个项目里还有这些功能：

- 结果页展示原图、分割图、热力图、定位框结果、局部热力图
- 首页动态区
- 分类图鉴
- 用户登录、头像、历史记录
- 管理员后台
- DeepSeek 问答接口

## 技术栈

- 前端：Vue 3 + Vite + Element Plus
- 后端：Flask
- 分割模型：PyTorch 自定义分割网络，部署版编码骨干是 ResNet50
- 分类模型：ConvNeXt-Base + DINOv2 + Gating Fusion
- 数据存储：MySQL
- 问答：DeepSeek 兼容接口，可不配

## GitHub 里有什么，没什么

### 这个仓库里有的

- 完整前后端源码
- 前端构建配置
- 启动脚本
- 示例图片
- 图鉴数据和业务文案
- 分割与分类推理代码

### 这个仓库里没有的

- 分类权重 `runtime/CamouflageDriveQ/08/fusion_results/fusion_best.pth`
- 分割权重 `segmentation/models/MODEL06_RUN_best.pth`
- 本地 MySQL 数据目录
- 本地日志
- 真实 AI Key
- `frontend/node_modules`
- `frontend/dist`

所以你如果刚 clone 下来，不能指望它“裸跑就识别”，权重必须自己补回来。

## 权重包去哪里拿

已经把部署必需的大文件单独放到百度网盘了。

- 百度网盘链接：`https://pan.baidu.com/s/1-6FF0QzGhZPsVbIX7L2Rfw?pwd=1234`
- 提取码：`1234`

你下载下来后，直接把压缩包解压到项目根目录。压缩包里我已经把相对路径摆好了，正常情况下你不用自己手动搬文件。

解压后你至少要确认这两个文件在：

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

## 你按这个顺序跑，基本不会出错

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd <repo-dir>
```

### 2. 先还原权重

把百度网盘里的权重包解压到项目根目录，确认上面说的两个 `.pth` 文件都在。

### 3. 装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 装前端依赖并构建

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. 配数据库

默认数据库配置就是下面这套：

- host：`127.0.0.1`
- port：`3306`
- user：`camouflage_app`
- password：`Camouflage@2026`
- database：`camouflage_insect_app`

你有两种搞法：

1. Windows 本地直接跑 `launch_mini_app.bat`，脚本会尝试帮你把本地 MySQL 初始化好。
2. 你自己手动建库，然后把 `runtime/mysql/app_db.example.json` 复制成 `runtime/mysql/app_db.json`，把里面参数改成你自己的。

也可以直接用环境变量覆盖：

- `CAMOUFLAGE_DB_HOST`
- `CAMOUFLAGE_DB_PORT`
- `CAMOUFLAGE_DB_USER`
- `CAMOUFLAGE_DB_PASSWORD`
- `CAMOUFLAGE_DB_NAME`

### 6. AI 问答想用就配，不想用可以先不配

这个项目就算没有 AI Key，主识别链路还是能跑，只是问答会退化。

如果你要配：

1. 把 `runtime/ai_config.example.json` 复制成 `runtime/ai_config.json`
2. 把你自己的 Key 填进去

也可以直接用环境变量：

- `CAMOUFLAGE_AI_PROVIDER`
- `CAMOUFLAGE_AI_BASE`
- `CAMOUFLAGE_AI_MODEL`
- `CAMOUFLAGE_AI_KEY`
- `DEEPSEEK_API_KEY`
- `CAMOUFLAGE_AI_TEMPERATURE`

## 启动方式我给你分开说

### Windows 本地最省事的启动方式

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

如果你想临时给手机访问地址：

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

生产环境建议你自己再挂 Nginx 做反代。

## 如果你要改前端

开发模式：

```bash
cd frontend
npm install
npm run dev
```

Vite 会把 `/api` 这些请求代理到 `http://127.0.0.1:7863`。

## 常见坑我提前帮你踩掉

### 1. 页面能开，识别报错

先检查这几个最容易错的：

- `fusion_best.pth` 放没放对
- `MODEL06_RUN_best.pth` 放没放对
- Python 依赖有没有装全

### 2. 页面数据加载失败，提示 MySQL 连接不上

优先看：

- MySQL 起没起
- `runtime/mysql/app_db.json` 对不对
- `camouflage_insect_app` 这个库在不在

Windows 本地优先直接试：

```bat
launch_mini_app.bat
```

### 3. 问答功能不能用

一般就是没配 AI Key。这个不影响识别主链路。

### 4. 你想把仓库重新推 GitHub，但是怕把大文件带上去

不用担心，我已经在 `.gitignore` 里把这些排掉了：

- 模型权重
- MySQL 数据目录
- 日志
- 本地 AI 配置
- `node_modules`
- `frontend/dist`

正常按现在这个仓库结构推，不会把那几个大东西带上去。

## 目录结构你大概认一下

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

## 最后我再强调一遍

这个仓库现在适合做三件事：

- 源码公开托管
- 交接给下一个人继续改
- 拉到新机器上重新部署

你如果真要复现完整效果，正确顺序就五步：

1. clone 源码
2. 解压百度网盘里的权重包
3. 装 Python / Node.js / MySQL
4. 构建前端
5. 启动项目

别跳步骤，尤其别忘了先补权重。

按我这个 README 走，正常就能把项目拉起来。
