from __future__ import annotations


FEED_TABS = ["动态", "鉴定", "文章", "百科"]

DISCOVER_TOOLS = [
    {
        "title": "昆虫资料检索",
        "subtitle": "可按识别结果名称跳转至公开资料站点继续核查分布、习性与命名信息。",
        "target": "search",
    },
    {
        "title": "分类图鉴",
        "subtitle": "集中浏览 11 类目标昆虫的识别线索、生态角色、风险影响与现场处理建议。",
        "target": "catalog",
    },
    {
        "title": "识别问答",
        "subtitle": "在识别完成后继续围绕当前对象发起问答，快速查询危害性、栖息环境与易混种。",
        "target": "assistant",
    },
    {
        "title": "资料参考",
        "subtitle": "汇总地图资源、分类科普来源与平台说明，便于查证与交接。",
        "target": "guide",
    },
]

MINE_ACTIONS = [
    {"title": "识别记录", "subtitle": "回看最近五条识别结果与提问记录", "target": "history"},
    {"title": "好友动态", "subtitle": "查看已关注用户的最新观察与发布", "target": "feed"},
    {"title": "识别问答", "subtitle": "继续围绕当前识别结果提出补充问题", "target": "assistant"},
    {"title": "资料参考", "subtitle": "查看公开来源、数据说明与地图资源", "target": "guide"},
]

GUIDE_CARDS = [
    {
        "title": "桌面端工作流",
        "text": "桌面端保留图像分割过程、分类证据、指标卡和后台维护入口，适合教学展示、复核分析与平台管理。",
    },
    {
        "title": "移动端工作流",
        "text": "移动端仅保留拍照、上传、识别结果、生态解读与问答入口，减少冗余信息，更适合现场使用。",
    },
    {
        "title": "数据存储方式",
        "text": "识别记录、用户账号、关注关系与动态内容统一写入本地 MySQL，图片结果以记录形式长期保存。",
    },
    {
        "title": "问答服务说明",
        "text": "问答模块优先走远程模型服务；未配置密钥时会使用内置知识模式，保证识别后依然可以继续查询。",
    },
]

REFERENCE_LINKS = [
    {"label": "Apache ECharts 地图文档", "url": "https://echarts.apache.org/handbook/en/how-to/chart-types/map/basic-map/"},
    {"label": "阿里云 DataV 中国 GeoJSON", "url": "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"},
    {"label": "Britannica | Bee", "url": "https://www.britannica.com/animal/bee"},
    {"label": "Britannica | Butterfly", "url": "https://www.britannica.com/animal/butterfly-insect"},
    {"label": "National Geographic | Cicadas", "url": "https://www.nationalgeographic.com/animals/invertebrates/facts/cicadas/"},
    {"label": "Britannica | Dragonfly", "url": "https://www.britannica.com/animal/dragonfly"},
    {"label": "Britannica | Katydid", "url": "https://www.britannica.com/animal/long-horned-grasshopper"},
    {"label": "National Geographic | Praying Mantis", "url": "https://www.nationalgeographic.com/animals/invertebrates/facts/praying-mantis"},
    {"label": "Britannica | Antlion", "url": "https://www.britannica.com/animal/antlion"},
    {"label": "Britannica | Leaf Insect", "url": "https://www.britannica.com/animal/leaf-insect"},
    {"label": "San Diego Zoo | Stick Insect", "url": "https://animals.sandiegozoo.org/animals/stick-insect"},
]

ASSISTANT_QUICK_QUESTIONS = [
    "它属于害虫还是益虫？",
    "这种昆虫通常在哪些环境里出现？",
    "在校园或田间遇到它时应如何处理？",
    "它和哪些近似种最容易混淆？",
]

NEARBY_SITES = [
    {"title": "林下落叶带", "subtitle": "叶拟态观察点", "sample_key": "mantis", "x": 18, "y": 24},
    {"title": "池塘边缘", "subtitle": "蜻蜓活动带", "sample_key": "dragonfly", "x": 72, "y": 18},
    {"title": "草地样带", "subtitle": "螽斯与蝗虫", "sample_key": "katydid", "x": 62, "y": 42},
    {"title": "乔木树干区", "subtitle": "蝉类羽化观察区", "sample_key": "cicada", "x": 28, "y": 52},
    {"title": "灌丛边缘", "subtitle": "竹节虫样点", "sample_key": "stick_insect", "x": 78, "y": 68},
    {"title": "花灌木区", "subtitle": "蝶类活动区", "sample_key": "butterfly", "x": 38, "y": 74},
]

ARTICLE_LIBRARY = [
    {
        "title": "Evolutionary genomics of camouflage innovation in the orchid mantis",
        "summary": "这篇 Nature Communications 论文把兰花螳螂和枯叶螳螂放到基因组与转录组框架下比较，解释了花拟态色彩、腿部叶状扩展和体型二型性背后的进化与发育机制。",
        "category": "拟态基因组",
        "meta": "Nature Communications · 2023",
        "source": "Guangping Huang et al.",
        "url": "https://www.nature.com/articles/s41467-023-40355-1",
    },
    {
        "title": "Motion camouflage in dragonflies",
        "summary": "Nature 的这篇短文用三维轨迹重建说明蜻蜓在空中追逐时会主动采用“运动伪装”，让目标在视网膜上感觉自己几乎静止，从而提高接近成功率。",
        "category": "运动伪装",
        "meta": "Nature · 2003",
        "source": "Akiko Mizutani et al.",
        "url": "https://www.nature.com/articles/423604a",
    },
    {
        "title": "Gradual and contingent evolutionary emergence of leaf mimicry in butterfly wing patterns",
        "summary": "这项 BMC 研究以枯叶蝶类群为对象，支持叶拟态不是突然出现，而是通过一系列可追踪的翅纹变化逐步积累形成。",
        "category": "叶拟态进化",
        "meta": "BMC Evolutionary Biology · 2014",
        "source": "Takao K. Suzuki et al.",
        "url": "https://bmcecolevol.biomedcentral.com/articles/10.1186/s12862-014-0229-5",
    },
    {
        "title": "Coloration in a Praying Mantis: Color Change, Sexual Color Dimorphism, and Possible Camouflage Strategies",
        "summary": "这篇 Ecology and Evolution 论文直接测试螳螂在不同背景中的颜色变化与栖位策略，结果显示其发育期颜色变化有限，但雌雄在体色与活动性上存在不同的隐蔽策略。",
        "category": "螳螂颜色策略",
        "meta": "Ecology and Evolution · 2025",
        "source": "Leah Y. Rosenheim et al.",
        "url": "https://doi.org/10.1002/ece3.70398",
    },
    {
        "title": "Bogong Moths Are Well Camouflaged by Effectively Decolourized Wing Scales",
        "summary": "Frontiers in Physiology 的这篇文章从翅鳞光学和反射光谱出发，证明澳洲 Bogong 蛾的翅面颜色确实与树皮类背景高度匹配，是很典型的背景匹配案例。",
        "category": "蛾类隐蔽色",
        "meta": "Frontiers in Physiology · 2020",
        "source": "Doekele G. Stavenga et al.",
        "url": "https://www.frontiersin.org/articles/10.3389/fphys.2020.00095/full",
    },
    {
        "title": "The role of colour patterns for the recognition of flowers by bees",
        "summary": "这篇 Royal Society B 的论文结合多光谱成像和蜂视觉模型，说明花朵图案本身会显著影响蜜蜂的识别效率，不只是颜色本身在起作用。",
        "category": "蜂类视觉",
        "meta": "Philosophical Transactions of the Royal Society B · 2022",
        "source": "Natalie Hempel de Ibarra et al.",
        "url": "https://doi.org/10.1098/rstb.2021.0284",
    },
    {
        "title": "Floral Trait Preferences of Three Common wild Bee Species",
        "summary": "这篇 Insects 论文用标准化人工花测试三种常见野蜂的花部偏好，结果显示高饱和颜色和更大的花展示面对它们都更有吸引力。",
        "category": "野蜂花偏好",
        "meta": "Insects · 2024",
        "source": "Kim C. Heuel et al.",
        "url": "https://www.mdpi.com/2075-4450/15/6/427",
    },
]

IDENTIFY_HIGHLIGHTS = [
    {
        "title": "快速识别建议",
        "summary": "先看结构，再看颜色；先看前足、触角、翅形，再看背景中的拟态效果。",
    },
    {
        "title": "移动端结果策略",
        "summary": "移动端只保留分类结果、指标摘要和生态解读，减少中间过程信息对现场决策的干扰。",
    },
    {
        "title": "桌面端可视化策略",
        "summary": "桌面端保留分割弹窗、证据四宫格和指标卡，适合汇报、答辩和后台复核。",
    },
    {
        "title": "识别后追问",
        "summary": "识别完成后可直接继续提问，查询危害性、易混种、分布带和处理建议。",
    },
]

SEED_POSTS = [
    {
        "author": "林下观察站",
        "username": "forest_watch",
        "content": "今天在林下样带补拍到一只螳螂，落叶背景里轮廓几乎被打散，经过分割后结构线索明显更稳定。",
        "tag_label": "样区记录",
        "sample_key": "mantis",
        "created_at": "2 分钟前",
    },
    {
        "author": "湿地巡查组",
        "username": "wetland_patrol",
        "content": "池塘边蜻蜓活动明显增多，白天光照稳定时拍摄，模型对头胸部和腹部的关注会更集中。",
        "tag_label": "样点快讯",
        "sample_key": "dragonfly",
        "created_at": "9 分钟前",
    },
    {
        "author": "林缘记录员",
        "username": "edge_recorder",
        "content": "今天在灌丛边缘观察到一只竹节虫，停驻枝条与体态方向几乎完全一致，肉眼识别比想象中更困难。",
        "tag_label": "现场观察",
        "sample_key": "stick_insect",
        "created_at": "18 分钟前",
    },
    {
        "author": "花灌木监测点",
        "username": "flower_monitor",
        "content": "蝶类在花灌木区的活动仍然最活跃，建议拍摄时保留宿主植物和停驻角度，便于后续复核。",
        "tag_label": "监测更新",
        "sample_key": "butterfly",
        "created_at": "26 分钟前",
    },
    {
        "author": "乔木样带组",
        "username": "tree_belt",
        "content": "树干上的蝉类羽化壳和成虫都较容易拍到，保留树皮纹理有助于解释模型为什么会出现局部高热区域。",
        "tag_label": "结构线索",
        "sample_key": "cicada",
        "created_at": "34 分钟前",
    },
    {
        "author": "夜间观察队",
        "username": "night_watch",
        "content": "蛾类在灯下聚集明显，但受环境光影响较大。夜间拍摄建议控制曝光，避免亮斑遮挡翅脉细节。",
        "tag_label": "夜间记录",
        "sample_key": "moth",
        "created_at": "47 分钟前",
    },
]

DISTRIBUTION_SPECIES = [
    {
        "key": "bee",
        "name_cn": "蜜蜂",
        "name_en": "Bee",
        "summary": "花源丰富的农田、果园与山地灌丛都常见，主要活动区随花期和温度变化。",
        "major_regions": ["华北果园带", "长江中下游平原", "华南丘陵", "西南山地"],
        "points": [
            {"name": "山东半岛", "lng": 120.4, "lat": 36.1},
            {"name": "长江中下游", "lng": 116.4, "lat": 31.3},
            {"name": "华南丘陵", "lng": 113.2, "lat": 23.1},
            {"name": "滇黔高原边缘", "lng": 103.8, "lat": 25.0},
        ],
    },
    {
        "key": "butterfly",
        "name_cn": "蝴蝶",
        "name_en": "Butterfly",
        "summary": "从东北到华南都有分布，暖湿地区和植被过渡带的种类更丰富。",
        "major_regions": ["东北林缘", "华东丘陵", "华中山地", "华南热带亚热带区"],
        "points": [
            {"name": "长白山南麓", "lng": 127.4, "lat": 42.4},
            {"name": "浙闽丘陵", "lng": 119.5, "lat": 27.7},
            {"name": "秦巴山区", "lng": 107.4, "lat": 32.7},
            {"name": "海南岛", "lng": 110.3, "lat": 19.8},
        ],
    },
    {
        "key": "cicada",
        "name_cn": "蝉",
        "name_en": "Cicada",
        "summary": "常见于有成熟乔木和夏季高温条件的区域，华北、华东和华中最容易观测到。",
        "major_regions": ["华北平原", "黄淮海地区", "长江中下游", "华南城郊林带"],
        "points": [
            {"name": "北京平原林带", "lng": 116.4, "lat": 39.9},
            {"name": "河南中东部", "lng": 114.3, "lat": 34.7},
            {"name": "南京周边", "lng": 118.8, "lat": 32.0},
            {"name": "珠三角北缘", "lng": 113.3, "lat": 23.2},
        ],
    },
    {
        "key": "dragonfly",
        "name_cn": "蜻蜓",
        "name_en": "Dragonfly",
        "summary": "紧贴水体环境分布，湖泊、池塘、稻田、河漫滩和湿地周边都常见。",
        "major_regions": ["东北湿地", "江淮湖群", "长江中下游稻区", "华南河网湿地"],
        "points": [
            {"name": "三江平原", "lng": 133.5, "lat": 47.4},
            {"name": "洪泽湖周边", "lng": 118.5, "lat": 33.3},
            {"name": "洞庭湖平原", "lng": 112.9, "lat": 29.4},
            {"name": "珠江三角洲", "lng": 113.5, "lat": 22.8},
        ],
    },
    {
        "key": "grasshopper",
        "name_cn": "蝗虫",
        "name_en": "Grasshopper",
        "summary": "多见于草地、农田边缘与裸地过渡区，北方旱地和草原农牧交错区密度更高。",
        "major_regions": ["内蒙古草原", "华北旱地", "黄土高原", "西北绿洲边缘"],
        "points": [
            {"name": "呼伦贝尔草原", "lng": 119.7, "lat": 49.2},
            {"name": "冀鲁豫旱地", "lng": 115.7, "lat": 36.3},
            {"name": "陕北黄土区", "lng": 109.5, "lat": 37.9},
            {"name": "河西走廊", "lng": 98.5, "lat": 39.8},
        ],
    },
    {
        "key": "katydid",
        "name_cn": "螽斯",
        "name_en": "Katydid",
        "summary": "偏爱植被较高、灌丛和林缘过渡地带，在华东、华中和西南山地更常见。",
        "major_regions": ["华东丘陵", "江南林缘", "西南山地", "华南灌丛带"],
        "points": [
            {"name": "皖南山地", "lng": 118.3, "lat": 30.2},
            {"name": "赣闽交界", "lng": 117.6, "lat": 26.8},
            {"name": "黔东南山地", "lng": 108.2, "lat": 26.6},
            {"name": "广西北部", "lng": 109.3, "lat": 25.1},
        ],
    },
    {
        "key": "mantis",
        "name_cn": "螳螂",
        "name_en": "Mantis",
        "summary": "全国多数地区都有记录，以农田、林缘、灌木丛和园林绿地最易观察。",
        "major_regions": ["华北农田林网", "长江中下游", "西南丘陵", "华南园林绿地"],
        "points": [
            {"name": "河北平原", "lng": 114.7, "lat": 38.0},
            {"name": "苏皖平原", "lng": 117.8, "lat": 32.2},
            {"name": "成都平原", "lng": 104.1, "lat": 30.7},
            {"name": "粤北丘陵", "lng": 113.0, "lat": 24.8},
        ],
    },
    {
        "key": "moth",
        "name_cn": "蛾",
        "name_en": "Moth",
        "summary": "分布极广，林地、农田、居民区周边都能出现，夜间灯光周围更容易观察到。",
        "major_regions": ["东北林地", "华北农田", "华东居民区", "华南山地"],
        "points": [
            {"name": "辽东林地", "lng": 123.8, "lat": 40.8},
            {"name": "华北平原", "lng": 116.7, "lat": 37.6},
            {"name": "杭州湾周边", "lng": 121.0, "lat": 30.1},
            {"name": "南岭北坡", "lng": 112.8, "lat": 24.4},
        ],
    },
    {
        "key": "antlion",
        "name_cn": "蚁蛉",
        "name_en": "Antlion",
        "summary": "成虫和幼虫多与干燥沙地、疏林和裸露地表相关，华北、华中与西北边缘地带较常见。",
        "major_regions": ["华北沙地", "豫鄂过渡区", "西北干旱边缘", "华南疏林地"],
        "points": [
            {"name": "冀北沙地", "lng": 117.5, "lat": 41.3},
            {"name": "豫西丘陵", "lng": 111.2, "lat": 34.6},
            {"name": "宁夏东部", "lng": 106.4, "lat": 37.7},
            {"name": "桂北疏林", "lng": 110.2, "lat": 25.3},
        ],
    },
    {
        "key": "phyllium",
        "name_cn": "叶䗛",
        "name_en": "Leaf Insect",
        "summary": "偏热带、亚热带森林环境，国内主要见于华南及西南南部的暖湿地区。",
        "major_regions": ["云南南部", "广西南部", "海南岛", "粤西山地"],
        "points": [
            {"name": "西双版纳", "lng": 100.8, "lat": 22.0},
            {"name": "南宁周边", "lng": 108.3, "lat": 22.8},
            {"name": "海南中部", "lng": 109.8, "lat": 19.3},
            {"name": "雷州半岛北缘", "lng": 110.1, "lat": 21.2},
        ],
    },
    {
        "key": "stick_insect",
        "name_cn": "竹节虫",
        "name_en": "Stick Insect",
        "summary": "更偏向南方暖湿森林和灌丛带，在华南与西南山地较容易遇到。",
        "major_regions": ["闽南山地", "广东北缘", "广西西部", "云南东南部"],
        "points": [
            {"name": "武夷山南段", "lng": 117.8, "lat": 26.1},
            {"name": "清远山地", "lng": 113.0, "lat": 24.7},
            {"name": "百色周边", "lng": 106.6, "lat": 23.9},
            {"name": "文山州", "lng": 104.3, "lat": 23.4},
        ],
    },
]
