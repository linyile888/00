from pydantic import BaseSettings

class Settings(BaseSettings):
    # 服务配置
    API_PREFIX: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # 智谱AI配置
    ZHIPU_API_KEY: str = "1ea78a95cba148e793fd870cd79aeac7.5pTp4SRIJE2BWx40"
    ZHIPU_MODEL: str = "glm-4"
    
    # 杭州匹配权重（维度占比）
    MATCH_WEIGHTS: dict = {
        "hangzhou_scene": 0.3,  # 杭州场景匹配（西湖/钱塘等）
        "era": 0.3,             # 时代匹配（宋/民国/现代/未来）
        "occupation": 0.25,     # 职业特征匹配
        "personality": 0.15     # 性格匹配
    }
    
    # 杭州场景-视觉映射（给前端/TouchDesigner）
    HZ_SCENE_VISUAL: dict = {
        "west_lake": {"bg_color": "#E6F3FF", "particle_type": "lotus", "light_intensity": 0.8},
        "qian_tang": {"bg_color": "#F5E8D3", "particle_type": "wave", "light_intensity": 0.7},
        "tech_city": {"bg_color": "#121826", "particle_type": "neon", "light_intensity": 1.2},
        "ancient_hangzhou": {"bg_color": "#F9F1E8", "particle_type": "petal", "light_intensity": 0.6}
    }

settings = Settings()