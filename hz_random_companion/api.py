from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from models.user import UserCreate, User
from core.matching import hz_multi_dim_match, HZ_COMPANION_DB
from core.chat import handle_hz_chat
from core.visual import get_hz_visual_config
from utils.vroid import parse_vroid_era_model
import uuid

router = APIRouter(prefix="/api/v1")
USER_DB = {}  # 模拟用户数据库
WS_CONNECTIONS = {}  # WebSocket连接存储

@router.post("/user/register", response_model=User)
def register_hz_user(user_create: UserCreate):
    """杭州用户注册"""
    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        **user_create.dict()
    )
    USER_DB[user_id] = user
    return user

@router.post("/match/hangzhou/{user_id}")
def match_hz_companion(user_id: str):
    """杭州跨时代伴侣匹配"""
    user = USER_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="杭州用户不存在")
    companion = hz_multi_dim_match(user)
    user.current_companion_id = companion.companion_id
    USER_DB[user_id] = user
    # 返回伴侣信息+视觉配置
    visual_config = get_hz_visual_config(companion)
    return {"companion": companion, "visual_config": visual_config}

@router.websocket("/ws/chat/hangzhou/{user_id}")
async def hz_chat_ws(user_id: str, websocket: WebSocket):
    """杭州跨时代实时对话WebSocket"""
    await websocket.accept()
    WS_CONNECTIONS[user_id] = websocket
    user = USER_DB.get(user_id)
    chat_history = []
    
    try:
        while True:
            data = await websocket.receive_json()
            user_input = data.get("user_input")
            companion_id = data.get("companion_id") or user.current_companion_id
            
            if not user_input or not companion_id:
                await websocket.send_json({"error": "缺少输入或伴侣ID"})
                continue
            
            # 处理对话
            reply, mood = handle_hz_chat(user_id, companion_id, user_input, chat_history)
            companion = next((c for c in HZ_COMPANION_DB if c.companion_id == companion_id), None)
            visual_config = get_hz_visual_config(companion)
            
            # 更新聊天历史
            chat_history.extend([{"role": "user", "content": user_input}, {"role": "assistant", "content": reply}])
            chat_history = chat_history[-20:]  # 限制历史长度
            
            # 发送回复+视觉配置
            await websocket.send_json({
                "reply": reply,
                "mood": mood,
                "visual_config": visual_config,
                "chat_history": chat_history
            })
    except WebSocketDisconnect:
        del WS_CONNECTIONS[user_id]
        await websocket.close()

@router.get("/companion/hangzhou/{companion_id}/vroid")
def get_hz_vroid_data(companion_id: str):
    """获取杭州伴侣的VRoid模型数据"""
    companion = next((c for c in HZ_COMPANION_DB if c.companion_id == companion_id), None)
    if not companion:
        raise HTTPException(status_code=404, detail="杭州伴侣不存在")
    model_data = parse_vroid_era_model(companion.vroid_model_url)
    return {"companion_id": companion_id, "vroid_data": model_data, "vroid_url": companion.vroid_model_url}