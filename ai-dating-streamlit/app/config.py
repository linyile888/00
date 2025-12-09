import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 数据文件路径
PLAYER_DATA_PATH = os.path.join(DATA_DIR, "player_data.json")
PARTNER_DATA_PATH = os.path.join(DATA_DIR, "partner_data.json")
CHAT_RECORD_PATH = os.path.join(DATA_DIR, "chat_records.json")

# 智谱AI API配置（替换为你的密钥）
ZHIPU_API_KEY = "1ea78a95cba148e793fd870cd79aeac7.5pTp4SRIJE2BWx40"
ZHIPU_MODEL = "glm-4"

# 问卷配置（保留核心字段）
QUESTIONS = [
    {"id": 1, "type": "radio", "title": "你的性别？", "options": ["男", "女", "其他"], "key": "gender"},
    {"id": 2, "type": "number", "title": "你的身高（cm，145-220之间）？", "min": 145, "max": 220, "key": "height"},
    {"id": 3, "type": "number", "title": "你的体重（kg）？", "min": 30, "max": 150, "key": "weight"},
    {"id": 4, "type": "radio", "title": "你的年龄区间？", "options": ["18-22", "23-26", "27-30", "31+"], "key": "age"},
    {"id": 5, "type": "radio", "title": "你喜欢的性格类型？", "options": ["温柔知性", "阳光开朗", "古灵精怪", "成熟稳重"], "key": "personality_prefer"},
    {"id": 6, "type": "multiselect", "title": "你的兴趣爱好（可多选）？", "options": ["看书", "运动", "动漫游戏", "旅行", "编程", "摄影", "音乐", "手绘", "美食"], "key": "hobbies"},
    {"id": 7, "type": "radio", "title": "你喜欢的相处模式？", "options": ["安静陪伴", "热闹互动", "共同冒险", "深度交流"], "key": "interaction_mode"},
    {"id": 8, "type": "radio", "title": "你最看重伴侣的什么特质？", "options": ["三观契合", "兴趣相投", "性格互补", "外在条件"], "key": "core_value"},
]

# 伴侣池（保留核心人设字段）
PARTNER_POOL = [
    {
        "id": 1,
        "name": "林晚星",
        "gender": "女",
        "age": "23-26",
        "height": 165,
        "weight": 48,
        "personality": "温柔知性",
        "hobbies": ["看书", "摄影", "徒步", "美食"],
        "background": "文学系研究生，兼职民宿主理人",
        "match_tags": ["文艺", "安静", "热爱生活", "三观契合"],
        "avatar": "https://via.placeholder.com/100/FFB6C1/FFFFFF?text=林晚星"  # 占位头像链接
    },
    {
        "id": 2,
        "name": "江辰宇",
        "gender": "男",
        "age": "23-26",
        "height": 185,
        "weight": 75,
        "personality": "阳光开朗",
        "hobbies": ["篮球", "露营", "弹吉他", "旅行"],
        "background": "健身教练，兼职乐队吉他手",
        "match_tags": ["运动", "外向", "有趣", "共同冒险"],
        "avatar": "https://via.placeholder.com/100/87CEEB/FFFFFF?text=江辰宇"
    },
    {
        "id": 3,
        "name": "苏沐妍",
        "gender": "女",
        "age": "18-22",
        "height": 158,
        "weight": 45,
        "personality": "古灵精怪",
        "hobbies": ["cosplay", "手游", "手绘", "动漫游戏"],
        "background": "设计专业学生，自由插画师",
        "match_tags": ["二次元", "创意", "宅系", "兴趣相投"],
        "avatar": "https://via.placeholder.com/100/FFD700/FFFFFF?text=苏沐妍"
    },
    {
        "id": 4,
        "name": "顾言泽",
        "gender": "男",
        "age": "27-30",
        "height": 180,
        "weight": 70,
        "personality": "成熟稳重",
        "hobbies": ["编程", "无人机", "看纪录片", "旅行"],
        "background": "软件工程师，科技博主",
        "match_tags": ["科技", "理性", "靠谱", "深度交流"],
        "avatar": "https://via.placeholder.com/100/D3D3D3/FFFFFF?text=顾言泽"
    }
]

# 虚幻引擎配置（供跳转使用）
UNREAL_WEB_SERVER_URL = "http://localhost:8000"
UNREAL_SCENE_PATH = "/dating-scene"