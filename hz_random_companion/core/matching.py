from models.user import User
from models.companion import Companion
from config import settings
import random
import uuid

# 杭州跨时代伴侣数据库（宋/民国/现代/未来+特色职业）
HZ_COMPANION_DB: list[Companion] = [
    Companion(
        name="柳梦荷",
        era="song",
        hz_scene="west_lake",
        occupation="poet",
        occupation_feature="南宋西湖边的女词人，善写荷花词，熟悉苏堤、雷峰塔典故",
        personality="gentle",
        vroid_model_url="https://your-server/vroid/song/poet_liumenghe.vrm",
        voice_style="ancient_song"
    ),
    Companion(
        name="沈茂昌",
        era="republic",
        hz_scene="qian_tang",
        occupation="businessman",
        occupation_feature="民国杭州清河坊的绸缎商，懂杭绣，熟悉钱塘江航运",
        personality="bold",
        vroid_model_url="https://your-server/vroid/republic/businessman_shenmaochang.vrm",
        voice_style="republic_mandarin"
    ),
    Companion(
        name="林晓茜",
        era="modern",
        hz_scene="tech_city",
        occupation="programmer",
        occupation_feature="杭州未来科技城的算法工程师，参与过云栖大会项目，爱喝龙井",
        personality="creative",
        vroid_model_url="https://your-server/vroid/modern/programmer_linxiaoma.vrm",
        voice_style="modern_hangzhou"
    ),
    Companion(
        name="夜汐",
        era="future",
        hz_scene="tech_city",
        occupation="cyber_engineer",
        occupation_feature="未来杭州元宇宙西湖的搭建工程师，熟悉钱塘数字城的霓虹网络",
        personality="calm",
        vroid_model_url="https://your-server/vroid/future/cyber_engineer_yexi.vrm",
        voice_style="future_cyber"
    )
]

def hz_multi_dim_match(user: User) -> Companion:
    """杭州跨时代多维度加权匹配"""
    weighted_companions = []
    for companion in HZ_COMPANION_DB:
        # 1. 杭州场景匹配分：用户偏好场景与伴侣场景的重合数
        scene_score = len(set(user.hz_scene_prefer) & {companion.hz_scene})
        # 2. 时代匹配分：用户偏好时代与伴侣时代的重合数
        era_score = len(set(user.era_prefer) & {companion.era})
        # 3. 职业匹配分：用户偏好职业与伴侣职业的重合数
        occupation_score = len(set(user.occupation_prefer) & {companion.occupation})
        # 4. 性格匹配分：用户性格标签与伴侣性格的重合数
        personality_score = len(set(user.personality_tags) & {companion.personality})
        
        # 计算总权重（按配置的维度占比）
        total_weight = (
            scene_score * settings.MATCH_WEIGHTS["hangzhou_scene"] +
            era_score * settings.MATCH_WEIGHTS["era"] +
            occupation_score * settings.MATCH_WEIGHTS["occupation"] +
            personality_score * settings.MATCH_WEIGHTS["personality"]
        )
        weighted_companions.append((companion, total_weight))
    
    # 权重筛选：优先选权重>0的，无则随机
    valid_companions = [c for c, w in weighted_companions if w > 0]
    if valid_companions:
        # 加权随机（权重越高，被选中概率越大）
        weights = [w for c, w in weighted_companions if w > 0]
        return random.choices(valid_companions, weights=weights)[0]
    return random.choice(HZ_COMPANION_DB)