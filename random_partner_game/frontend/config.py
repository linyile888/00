import os

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 字体路径
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "PressStart2P-Regular.ttf")

# 背景图路径（单个背景图，用于兼容）
BACKGROUND_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "images", "background1.png")

# 背景图列表（按顺序播放）
BACKGROUND_IMAGE_PATHS = []
images_dir = os.path.join(BASE_DIR, "assets", "images")
if os.path.exists(images_dir):
    # 按顺序加载 background1.png, background2.png, ...
    index = 1
    while True:
        bg_path = os.path.join(images_dir, f"background{index}.png")
        if os.path.exists(bg_path):
            BACKGROUND_IMAGE_PATHS.append(bg_path)
            index += 1
        else:
            break

# 如果没有找到任何背景图，使用默认路径
if not BACKGROUND_IMAGE_PATHS:
    BACKGROUND_IMAGE_PATHS = [BACKGROUND_IMAGE_PATH]

# 问卷题目配置（匹配后端接口字段）
SURVEY_QUESTIONS = [
    {
        "id": "personality",
        "title": "你的性格特点？",
        "type": "select",
        "options": ["开朗活泼", "温柔内向", "豪迈仗义", "理性冷静", "幽默风趣", "沉稳内敛"]
    },
    {
        "id": "hobby",
        "title": "你的兴趣爱好？（可多选）",
        "type": "checkbox",
        "options": ["阅读", "运动", "音乐", "旅行", "游戏", "绘画", "编程", "烹饪", "摄影", "电影"]
    },
    {
        "id": "age",
        "title": "你的年龄？",
        "type": "number",
        "min": 18,
        "max": 80
    },
    {
        "id": "height",
        "title": "你的身高（cm）？",
        "type": "number",
        "min": 150,
        "max": 220
    },
    {
        "id": "weight",
        "title": "你的体重（kg）？",
        "type": "number",
        "min": 40,
        "max": 150
    },
    {
        "id": "preferred_era",
        "title": "你偏好的时代背景？",
        "type": "select",
        "options": ["古代", "民国", "现代", "未来"]
    }
]

