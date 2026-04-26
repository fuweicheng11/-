from __future__ import annotations

import re


FLOW_STEPS = [
    {"index": "01", "title": "主体分割", "text": "先把昆虫从复杂背景中提取出来，减少枝叶纹理对识别结果的干扰。"},
    {"index": "02", "title": "分类识别", "text": "将清理后的主体区域送入分类模型，保留原有识别链路，同时提升输入稳定性。"},
    {"index": "03", "title": "结果解释", "text": "结果页同时展示分割图、分类证据、生态信息和 AI 问答，便于继续分析与研判。"},
]

HOME_ACTIONS = [
    {
        "target": "identify",
        "eyebrow": "识别入口",
        "title": "上传一张照片",
        "text": "支持手机相册与现场拍照，两种方式都可以直接进入识别流程。",
    },
    {
        "target": "samples",
        "eyebrow": "样例库",
        "title": "查看 11 类样例",
        "text": "快速进入内置样例，查看完整的分割、分类和证据展示效果。",
    },
    {
        "target": "assistant",
        "eyebrow": "智能问答",
        "title": "继续追问结果",
        "text": "识别完成后可继续询问危害、习性、益害属性和现场处理建议。",
    },
    {
        "target": "guide",
        "eyebrow": "资料参考",
        "title": "查看来源与说明",
        "text": "汇总使用方式、部署提示和公开参考资料，便于交接与引用。",
    },
]

FEED_TABS = ["动态", "鉴定", "文章", "百科"]

DISCOVER_TOOLS = [
    {
        "title": "昆虫检索",
        "subtitle": "按名称快速跳转到百科、GBIF、iNaturalist 等资料站点。",
        "target": "search",
        "accent": "sky",
        "icon": "搜",
    },
    {
        "title": "类别图鉴",
        "subtitle": "集中浏览 11 类目标昆虫的图像、线索和自然观察信息。",
        "target": "catalog",
        "accent": "mint",
        "icon": "鉴",
    },
    {
        "title": "智能问答",
        "subtitle": "围绕当前识别结果继续追问，可配置 DeepSeek 等大模型。",
        "target": "assistant",
        "accent": "gold",
        "icon": "问",
    },
    {
        "title": "资料参考",
        "subtitle": "查看公开资料来源、运行方式和模型使用说明。",
        "target": "guide",
        "accent": "rose",
        "icon": "资",
    },
]

MINE_ACTIONS = [
    {"title": "识别记录", "subtitle": "查看最近识别历史", "target": "history"},
    {"title": "样例库", "subtitle": "快速浏览演示样例", "target": "samples"},
    {"title": "智能问答", "subtitle": "继续追问识别结果", "target": "assistant"},
    {"title": "资料参考", "subtitle": "查看说明与来源", "target": "guide"},
]

GUIDE_CARDS = [
    {
        "title": "管理平台",
        "text": "电脑端用于统一管理识别、历史、账号和模型配置；手机端走更短的识别和追问流程，适合现场直接使用。",
    },
    {
        "title": "手机使用",
        "text": "手机端支持相册导入和拍照上传，打开网址即可直接使用，不需要额外安装封装应用。",
    },
    {
        "title": "AI 问答",
        "text": "问答模块默认支持本地知识回答；配置 DeepSeek 等兼容接口后，可切换到大模型增强问答。",
    },
]

REFERENCE_LINKS = [
    {"label": "Britannica | Bee", "url": "https://www.britannica.com/animal/bee"},
    {"label": "Britannica | Butterfly", "url": "https://www.britannica.com/animal/butterfly-insect"},
    {"label": "National Geographic | Cicadas", "url": "https://www.nationalgeographic.com/animals/invertebrates/facts/cicadas/"},
    {"label": "Britannica | Dragonfly", "url": "https://www.britannica.com/animal/dragonfly"},
    {"label": "Britannica | Katydid", "url": "https://www.britannica.com/animal/long-horned-grasshopper"},
    {"label": "National Geographic | Praying mantis", "url": "https://www.nationalgeographic.com/animals/invertebrates/facts/praying-mantis"},
    {"label": "Britannica | Antlion", "url": "https://www.britannica.com/animal/antlion"},
    {"label": "Britannica | Leaf insect", "url": "https://www.britannica.com/animal/leaf-insect"},
    {"label": "San Diego Zoo | Stick insect", "url": "https://animals.sandiegozoo.org/animals/stick-insect"},
    {"label": "Britannica | Moths vs. butterflies", "url": "https://www.britannica.com/video/258692/moth-versus-butterfly-order-lepidoptera-video"},
]

ASSISTANT_QUICK_QUESTIONS = [
    "这个虫有什么危害？",
    "它是害虫还是益虫？",
    "田间遇到它一般怎么处理？",
    "它和相似种最容易混淆的地方是什么？",
]

NEARBY_SITES = [
    {"title": "林下落叶带", "subtitle": "叶拟态观察点", "sample_key": "mantis", "x": 18, "y": 24},
    {"title": "池塘边缘", "subtitle": "蜻蜓活动带", "sample_key": "dragonfly", "x": 72, "y": 18},
    {"title": "草地样带", "subtitle": "蝈斯与蝗虫", "sample_key": "katydid", "x": 62, "y": 42},
    {"title": "乔木树干区", "subtitle": "蝉类羽化观察", "sample_key": "cicada", "x": 28, "y": 52},
    {"title": "灌丛边缘", "subtitle": "竹节虫样点", "sample_key": "stick_insect", "x": 78, "y": 68},
    {"title": "花灌木区", "subtitle": "蝶蛾活动区", "sample_key": "butterfly", "x": 38, "y": 74},
]

CLASS_CATALOG = [
    {
        "key": "bee",
        "sample_dir": "bee",
        "name_cn": "蜜蜂",
        "name_en": "Bee",
        "science": {
            "title": "蜜蜂 (Bee)",
            "camouflage": "多数蜜蜂并不是通过强拟态隐藏，而是依靠花枝、花影与体色关系压低存在感，近花停留时不容易第一眼被发现。",
            "clue": "胸部绒毛较多，身体厚实，前后两对透明翅叠在背部，靠近花面时黄黑相间的体节很稳定。",
            "observation": "蜜蜂常在晴暖、少风时段活动，频繁访问花朵采集花粉和花蜜，体表绒毛常能沾附明显花粉。",
            "role": "典型益虫，以传粉价值为主。",
            "impact": "对农作物和野生植物授粉非常重要，通常不会主动危害作物；但在靠近蜂巢或受到惊扰时可能蜇人。",
            "advice": "观察时保持距离，不要拍打或堵住飞行路径；若靠近蜂群区域，建议缓慢后退而不是挥手驱赶。",
        },
    },
    {
        "key": "butterfly",
        "sample_dir": "butterfly",
        "name_cn": "蝴蝶",
        "name_en": "Butterfly",
        "science": {
            "title": "蝴蝶 (Butterfly)",
            "camouflage": "合翅停在树皮、枯叶或枝条边缘时，翅面纹理会把轮廓拆散，看起来像一片旧叶或斑驳背景。",
            "clue": "棒状触角、宽阔鳞翅、左右翅纹大体对称，近看时结构特征比颜色更稳定。",
            "observation": "多在晴朗时段活动，常见于花丛、林缘和向阳空地，翅面颜色来自密集鳞粉。",
            "role": "多数成虫偏中性或益虫，幼虫阶段部分种类可能啃食植物。",
            "impact": "成虫本身通常不构成明显危害，部分毛虫会对叶片造成取食损失，但很多种类在生态系统中也承担授粉与食物链角色。",
            "advice": "若用于科普展示，可区分成虫与幼虫阶段的生态作用；遇到少量个体通常无需处理。",
        },
    },
    {
        "key": "cicada",
        "sample_dir": "cicada",
        "name_cn": "蝉",
        "name_en": "Cicada",
        "science": {
            "title": "蝉 (Cicada)",
            "camouflage": "蝉常贴着树干静止，灰褐到青褐的体色配合半透明翅面，能较自然地融进树皮纹理。",
            "clue": "头宽眼大，膜质翅透明且翅脉清楚，身体敦实，停栖时整体轮廓多顺着树干方向展开。",
            "observation": "若虫长期在地下生活，成虫羽化后停留在树干或枝条表面，雄蝉依靠发声器产生持续鸣声。",
            "role": "多为中性偏轻度害虫。",
            "impact": "通常不会造成毁灭性危害，但若虫吸食根部汁液、成虫产卵划伤嫩枝，数量大时会影响部分林木或果树长势。",
            "advice": "单个或少量个体一般不必处理；若在苗木区高密度发生，可结合修剪受伤嫩枝和栖息监测来管理。",
        },
    },
    {
        "key": "dragonfly",
        "sample_dir": "dragonfly",
        "name_cn": "蜻蜓",
        "name_en": "Dragonfly",
        "science": {
            "title": "蜻蜓 (Dragonfly)",
            "camouflage": "并不依赖强拟态，而是用细长身体和水边背景降低存在感，停在芦苇、枝条边缘时尤为明显。",
            "clue": "复眼很大，腹部细长，四翅分开平展，前后翅形不完全相同，是很稳定的识别依据。",
            "observation": "常见于池塘、溪流、湿地与稻田边，飞行能力强，善于在空中捕食蚊虫等小型昆虫。",
            "role": "典型益虫，是重要捕食者。",
            "impact": "对控制蚊虫和小型飞虫有积极作用，一般不会对作物本身形成危害。",
            "advice": "适合保育和观察，不建议人为驱赶；若在水边调查，可将其视作生态质量较好的辅助指示物种。",
        },
    },
    {
        "key": "grasshopper",
        "sample_dir": "grasshopper",
        "name_cn": "蝗虫",
        "name_en": "Grasshopper",
        "science": {
            "title": "蝗虫 (Grasshopper)",
            "camouflage": "绿色或褐色体表很容易和草丛、裸土混在一起，静止时身体边界常会被背景吃掉。",
            "clue": "后足粗壮善跳，胸背板明显，整体轮廓较敦实，触角通常不如蝈斯那样细长。",
            "observation": "多见于草地、农田边与开阔地，受惊时先跳后飞，常以植物叶片和嫩茎为食。",
            "role": "典型植食性害虫类群。",
            "impact": "密度升高时会啃食叶片、嫩梢和禾本科作物，对农田和草地都可能造成明显损失。",
            "advice": "单个个体以监测为主；若田间密度快速上升，应尽早结合人工清理、生态调控或农事管理进行防控。",
        },
    },
    {
        "key": "katydid",
        "sample_dir": "katydid",
        "name_cn": "蝈斯",
        "name_en": "Katydid",
        "science": {
            "title": "蝈斯 (Katydid)",
            "camouflage": "很多蝈斯直接把翅面做成叶片质感，连叶脉、缺刻边缘甚至老化感都模仿得很像。",
            "clue": "触角极长，身体偏扁，翅面常像整片绿叶，和蝗虫相比通常更纤细、更有叶片感。",
            "observation": "多在夜间活动，白天常潜伏在树叶、灌丛和草尖间；雄虫会通过前翅摩擦发声。",
            "role": "多为中性到轻度害虫，不同种差异较大。",
            "impact": "很多种以叶片为食，少量个体通常影响不大，但在园艺植物或局部密度偏高时可能造成取食痕迹。",
            "advice": "展示时可强调它与叶片拟态的关系；若在园艺区发生偏多，优先采用人工监测与定点清理。",
        },
    },
    {
        "key": "mantis",
        "sample_dir": "mantis",
        "name_cn": "螳螂",
        "name_en": "Mantis",
        "science": {
            "title": "螳螂 (Mantis)",
            "camouflage": "站在枝叶之间时，螳螂更像被背景打散的细长轮廓，不是完全消失，而是让观察者忽略过去。",
            "clue": "捕捉型前足、可转动的三角形头部和明显拉长的前胸，是最稳定的识别点。",
            "observation": "属于伏击型捕食者，常停在叶缘、枝梢和花序附近，等待其他昆虫靠近后迅速扑抓。",
            "role": "偏益虫，是重要捕食者。",
            "impact": "对蚜虫、蛾类幼虫等多种小型昆虫具有抑制作用；虽然偶尔也会捕食其他益虫，但整体仍以有利于生态控制为主。",
            "advice": "野外遇到通常无需处理，适合保留作为自然天敌；教学中可结合姿态、前足和头部转动来讲解识别要点。",
        },
    },
    {
        "key": "moth",
        "sample_dir": "moth",
        "name_cn": "蛾",
        "name_en": "Moth",
        "science": {
            "title": "蛾 (Moth)",
            "camouflage": "很多蛾类停在树皮、墙面或落叶上时，翅面斑纹会顺着底色融进去，夜间尤其不容易被注意到。",
            "clue": "身体通常比蝴蝶更厚，触角形态变化更大，停歇时两翅常平铺或屋脊状搭在背上。",
            "observation": "不少蛾类在夜间活动，容易被灯光吸引；翅和体表同样覆盖鳞片。",
            "role": "种类差异很大，成虫多偏中性，幼虫阶段部分为明显害虫。",
            "impact": "若对应种类的幼虫取食叶片、果实或储藏物，就可能形成经济危害；但并非所有蛾类都等同于害虫。",
            "advice": "遇到蛾类时需要区分成虫与幼虫、以及具体寄主植物；现场判断时不要仅凭“蛾”这一大类直接下结论。",
        },
    },
    {
        "key": "antlion",
        "sample_dir": "myrmeleonmicans",
        "name_cn": "蚁蛉",
        "name_en": "Antlion",
        "science": {
            "title": "蚁蛉 (Antlion)",
            "camouflage": "成虫常伏在干燥枝叶、砂石边和低矮灌丛上，灰褐色细长轮廓不抢眼，远看容易漏掉。",
            "clue": "两对翅狭长透明，翅脉成网，触角末端略膨大，这一点能和蜻蜓、豆娘拉开差别。",
            "observation": "幼虫阶段比成虫更著名，常在松散沙地里挖漏斗状陷阱捕食小型昆虫。",
            "role": "偏益虫，尤其幼虫阶段是小型昆虫捕食者。",
            "impact": "对环境中的小型昆虫有控制作用，一般不会对农作物造成直接危害。",
            "advice": "如果在沙地或裸地观察到陷阱，可作为自然行为展示案例；通常不需要人为干预。",
        },
    },
    {
        "key": "phyllium",
        "sample_dir": "Phyllium",
        "name_cn": "叶䗛",
        "name_en": "Phyllium",
        "science": {
            "title": "叶䗛 (Phyllium)",
            "camouflage": "这是非常典型的叶拟态，体缘、翅形和色泽都在朝叶片靠近，远看像一片挂着的嫩叶。",
            "clue": "体形扁宽，腿部边缘常有叶裂样扩展，身体上还能看到类似主脉和侧脉的线条。",
            "observation": "多生活在植被茂密的环境中，以叶片为食；幼体刚孵化时颜色可能偏褐，随后逐渐转绿。",
            "role": "多为中性到轻度植食性昆虫。",
            "impact": "一般数量不大时影响有限，但在封闭饲养或高密度条件下会啃食叶片。",
            "advice": "适合做拟态展示对象；如果在栽培环境中数量偏多，可通过人工转移和定期巡查控制。",
        },
    },
    {
        "key": "stick_insect",
        "sample_dir": "stickInsect",
        "name_cn": "竹节虫",
        "name_en": "Stick Insect",
        "science": {
            "title": "竹节虫 (Stick Insect)",
            "camouflage": "竹节虫依靠细长杆状体形和长时间静止，把自己伪装成一截小枝，是非常典型的枝拟态。",
            "clue": "胸腹细长近似木枝，四肢像分叉枝节，整体宽度很窄，轮廓干净而连续。",
            "observation": "多在傍晚或夜间取食叶片，白天通常几乎不动；不少种类走动时会轻轻摇晃，像枝条在风中摆动。",
            "role": "多为中性到轻度害虫。",
            "impact": "数量较少时通常只造成轻微取食痕迹，但在高密度饲养或局部暴发时会明显啃食叶片。",
            "advice": "自然环境下以观察为主；若在苗圃或温室中数量偏多，可优先人工摘除和夜间巡查。",
        },
    },
]


LABEL_ALIASES = {}
for item in CLASS_CATALOG:
    LABEL_ALIASES[item["key"]] = item["key"]
    LABEL_ALIASES[item["sample_dir"].lower()] = item["key"]
    LABEL_ALIASES[item["name_cn"]] = item["key"]
    LABEL_ALIASES[item["name_en"].lower()] = item["key"]
    LABEL_ALIASES[item["science"]["title"].lower()] = item["key"]

LABEL_ALIASES["antlion"] = "antlion"
LABEL_ALIASES["myrmeleon micans"] = "antlion"
LABEL_ALIASES["myrmeleonmicans"] = "antlion"
LABEL_ALIASES["phyllium"] = "phyllium"
LABEL_ALIASES["叶䗛"] = "phyllium"
LABEL_ALIASES["stick insect"] = "stick_insect"


def resolve_class_key(label: str) -> str | None:
    if not label:
        return None

    cleaned = label.strip().lower()
    if cleaned in LABEL_ALIASES:
        return LABEL_ALIASES[cleaned]

    match = re.search(r"[(（]([A-Za-z\s]+)[)）]", label)
    if match:
        english = match.group(1).strip().lower()
        if english in LABEL_ALIASES:
            return LABEL_ALIASES[english]

    for item in CLASS_CATALOG:
        if item["name_cn"] in label or item["name_en"].lower() in cleaned:
            return item["key"]
    return None


def get_class_meta(key: str | None) -> dict:
    default_science = {
        "title": "识别信息",
        "camouflage": "该结果更适合结合分割轮廓、热力分布与局部证据一起判断，重点关注主体结构与背景之间的差异。",
        "clue": "建议先看轮廓、触角、足部和翅型等稳定结构，再参考颜色纹理与背景贴合程度。",
        "observation": "这类结果目前没有单独补充说明，可以结合拍摄环境、停驻位置和周边植物继续判断。",
        "role": "生态角色信息仍在补充中，可先结合常见栖息环境与取食方式进行初步理解。",
        "impact": "风险与影响会因种类和场景不同而变化，建议结合寄主植物、出现位置和数量综合评估。",
        "advice": "现场以拍照留存、放大比对和谨慎确认为主，确认前尽量不要急于下结论。",
    }

    if not key:
        return {"science": default_science}

    for item in CLASS_CATALOG:
        if item["key"] == key:
            merged = dict(default_science)
            merged.update(item["science"])
            result = dict(item)
            result["science"] = merged
            return result

    return {"science": default_science}
