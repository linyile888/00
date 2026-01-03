from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # SQLite必填参数
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 用户表（存储问卷数据）
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    personality = Column(String(50))  # 性格（如：开朗、内向）
    hobby = Column(String(100))       # 喜好（如：游戏、读书、运动）
    age = Column(Integer)             # 年龄
    height = Column(Float)            # 身高（cm）
    weight = Column(Float)            # 体重（kg）
    preferred_era = Column(String(20))# 偏好时代（如：古代、现代、未来）
    matched_partner_id = Column(Integer)  # 匹配的伴侣ID

# 创建数据库表（首次运行自动生成）
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话（独立函数，解耦调用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 测试数据库连接（可选，运行后查看是否生成database.db文件）
if __name__ == "__main__":
    create_tables()
    print("数据库表创建成功！")