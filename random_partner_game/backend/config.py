import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置（SQLite本地存储，无需额外安装）
DATABASE_URL = "sqlite:///database.db"

# 智谱API配置（直接使用用户提供的密钥）
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "bc3f84880c14455eac5f1b7a60116cf9.2P90IhQ3elPk09fR")
ZHIPU_API_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 匹配算法配置（可改动：调整各维度权重）
MATCH_WEIGHTS = {
    "personality": 0.3,  # 性格权重
    "hobby": 0.25,       # 喜好权重
    "age": 0.15,         # 年龄权重
    "height": 0.15,      # 身高权重
    "weight": 0.1,       # 体重权重
    "era": 0.05          # 时代权重
}

# 伴侣池配置（可改动：新增/修改伴侣类型）
PARTNER_POOL = [
    {
        "id": 1,
        "name": "古风侠客",
        "era": "古代",
        "occupation": "侠客",
        "personality": "豪迈仗义",
        "hobby": "习武、饮酒、游历",
        "age": 25,
        "height": 185,
        "weight": 75,
        "pixel_image": "warrior.png",  # 对应frontend/assets/images/下的文件
        "dialogue_style": "说话豪爽，带古风词汇，喜欢鼓励他人"
    },
    {
        "id": 2,
        "name": "未来科学家",
        "era": "未来",
        "occupation": "科学家",
        "personality": "理性冷静",
        "hobby": "实验、编程、星空观测",
        "age": 30,
        "height": 178,
        "weight": 68,
        "pixel_image": "scientist.png",
        "dialogue_style": "说话简洁，逻辑清晰，偶尔带科技术语"
    },
    {
        "id": 3,
        "name": "民国文人",
        "era": "民国",
        "occupation": "作家",
        "personality": "温柔儒雅",
        "hobby": "读书、写作、品茶",
        "age": 28,
        "height": 180,
        "weight": 70,
        "pixel_image": "writer.png",
        "dialogue_style": "说话温和，带文学气息，喜欢引用诗句"
    },
    # 可继续添加更多伴侣...
]