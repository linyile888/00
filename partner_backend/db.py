# db.py （Windows专属路径适配，完整代码无省略，直接复制）
import sqlite3
import os

# Windows专属：自动获取Cursor项目根目录，避免路径权限问题，无需改动
DB_PATH = os.path.join(os.getcwd(), "partner_match.db")

def init_db():
    """初始化数据库：用户表+伴侣人设库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 1. 用户表（存储问卷数据，字段完整无省略）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            height INTEGER NOT NULL,
            weight INTEGER NOT NULL,
            personality TEXT NOT NULL,
            hobby TEXT NOT NULL,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 2. 伴侣人设库（预设不同时代/职业/性格，可扩展，完整数据无省略）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partner_lib (
            partner_id INTEGER PRIMARY KEY AUTOINCREMENT,
            era TEXT NOT NULL,
            occupation TEXT NOT NULL,
            age INTEGER NOT NULL,
            height INTEGER NOT NULL,
            weight INTEGER NOT NULL,
            personality TEXT NOT NULL,
            hobby TEXT NOT NULL,
            style TEXT NOT NULL
        )
    ''')
    # 插入初始伴侣数据（完整4组人设，无省略，【需改动】处可新增，格式统一即可）
    init_partners = [
        ("古代", "书生", 22, 180, 65, "沉稳内敛", "书法/吟诗", "温润如玉"),
        ("民国", "教师", 20, 165, 50, "温柔知性", "教书/养花", "温婉恬静"),
        ("现代", "程序员", 25, 178, 70, "开朗幽默", "代码/电竞", "阳光开朗"),
        ("未来", "宇航员", 28, 175, 62, "果敢坚毅", "星际探索/科研", "飒爽干练")
    ]
    cursor.executemany("INSERT OR IGNORE INTO partner_lib VALUES (NULL,?,?,?,?,?,?,?,?)", init_partners)
    conn.commit()
    conn.close()

# 调用初始化，完整执行无省略
if __name__ == "__main__":
    init_db()
    print("数据库初始化成功，伴侣库已导入（Windows路径：", DB_PATH, "）")