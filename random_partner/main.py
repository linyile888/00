import streamlit as st
import random
from datetime import datetime
from config import PARTNER_ERAS, PARTNER_JOBS
from utils import (
    calculate_match_probability, generate_meeting_story, get_reject_text,
    generate_partner_personality, save_chat_history, generate_partner_reply,
    generate_match_suggestion
)
from ui_components import (
    render_questionnaire, render_match_pool_preview,
    render_partner_card, render_probability科普,
    render_action_buttons, render_partner_personality,
    render_chat_history, render_chat_input, render_match_analysis
)

# ========== 页面基础设置 ==========
st.set_page_config(
    page_title="随机灵魂伴侣匹配器",
    page_icon="💘",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("💘 随机灵魂伴侣匹配器")
st.markdown("穿越时空，匹配你的专属灵魂伴侣～ 按喜好精准匹配！")

# ========== 初始化Session状态（新增问卷、玩家信息状态） ==========
if "questionnaire_step" not in st.session_state:
    st.session_state.questionnaire_step = 1
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}
if "questionnaire_completed" not in st.session_state:
    st.session_state.questionnaire_completed = False
if "current_match" not in st.session_state:
    st.session_state.current_match = None
if "match_history" not in st.session_state:
    st.session_state.match_history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_chatting" not in st.session_state:
    st.session_state.is_chatting = False

# ========== 核心流程 ==========
def main():
    # 1. 推进式问卷（核心入口）
    user_info, user_preferences, questionnaire_completed = render_questionnaire()
    
    # 2. 问卷完成后，显示匹配池和匹配按钮
    if questionnaire_completed:
        st.session_state.questionnaire_completed = True
        st.markdown("---")
        
        # 渲染匹配池预览（结合玩家信息和偏好）
        render_match_pool_preview(user_info, user_preferences)
        
        # 匹配按钮（居中显示）
        col_center = st.columns(3)[1]
        with col_center:
            match_btn = st.button("🎲 开启个性化伴侣匹配", type="primary", use_container_width=True)
        
        # 3. 执行个性化匹配逻辑
        if match_btn or st.session_state.current_match:
            # 点击匹配按钮，重新生成伴侣
            if match_btn:
                # 随机选择伴侣时代和职业（可扩展为按偏好筛选）
                selected_era, selected_era_label = random.choice(PARTNER_ERAS)
                selected_job = random.choice(PARTNER_JOBS[selected_era])
                
                # 生成伴侣人物设定（契合玩家偏好）
                partner_personality, target_personality, target_hobbies = generate_partner_personality(
                    selected_era, selected_job, user_preferences
                )
                
                # 计算匹配概率（基础概率+偏好契合度）
                base_prob, preference_fit, final_prob = calculate_match_probability(
                    user_info, user_preferences
                )
                
                # 生成相遇场景（融入玩家爱好）
                meeting_story = generate_meeting_story(
                    user_info, user_preferences,
                    selected_era, selected_job, target_personality
                )
                
                # 生成匹配建议
                match_suggestion = generate_match_suggestion(
                    user_info, user_preferences,
                    {
                        "era": selected_era,
                        "job": selected_job,
                        "target_personality": target_personality,
                        "personality": partner_personality
                    }
                )
                
                # 保存当前匹配结果
                st.session_state.current_match = {
                    "era": selected_era,
                    "era_label": selected_era_label,
                    "job": selected_job,
                    "personality": partner_personality,
                    "target_personality": target_personality,
                    "target_hobbies": target_hobbies,
                    "base_prob": base_prob,
                    "preference_fit": preference_fit,
                    "final_prob": final_prob,
                    "story": meeting_story,
                    "suggestion": match_suggestion,
                    "user_info": user_info,
                    "user_preferences": user_preferences
                }
                # 重置聊天记录
                st.session_state.chat_history = []
                st.session_state.is_chatting = False
            
            # 获取当前匹配结果
            current_match = st.session_state.current_match
            if not current_match:
                return
            
            # 4. 渲染核心内容
            # 伴侣卡片
            render_partner_card(
                partner_era=current_match["era"],
                partner_era_label=current_match["era_label"],
                partner_job=current_match["job"],
                match_prob=current_match["final_prob"],
                meeting_story=current_match["story"]
            )
            
            # 匹配分析（概率+建议）
            render_match_analysis(
                base_prob=current_match["base_prob"],
                preference_fit=current_match["preference_fit"],
                final_prob=current_match["final_prob"],
                suggestion=current_match["suggestion"]
            )
            
            # 伴侣档案
            render_partner_personality(current_match["personality"])
            
            # 操作按钮
            confirm_btn, retry_btn = render_action_buttons()
            
            # 5. 按钮交互处理
            if retry_btn:
                st.info(get_reject_text())
                st.session_state.current_match = None
                st.session_state.chat_history = []
                st.session_state.is_chatting = False
                st.rerun()
            
            if confirm_btn:
                st.session_state.is_chatting = True
                # 保存到匹配历史
                if current_match not in st.session_state.match_history:
                    st.session_state.match_history.append(current_match)
                st.success("🎉 已确认伴侣！现在可以和TA交流啦～")
            
            # 6. 交流模式
            if st.session_state.is_chatting:
                render_chat_history(st.session_state.chat_history)
                user_message = render_chat_input()
                
                if user_message:
                    # 记录用户消息
                    user_msg_item = {
                        "role": "user",
                        "content": user_message,
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.chat_history.append(user_msg_item)
                    
                    # 生成伴侣回复
                    partner_reply = generate_partner_reply(
                        current_match["user_info"],
                        current_match["user_preferences"],
                        current_match,
                        user_message
                    )
                    
                    # 记录伴侣消息
                    partner_msg_item = {
                        "role": "partner",
                        "content": partner_reply,
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.chat_history.append(partner_msg_item)
                    
                    # 保存聊天记录（含玩家信息）
                    save_path = save_chat_history(
                        partner_info={
                            "era": current_match["era"],
                            "job": current_match["job"],
                            "personality": current_match["personality"]
                        },
                        user_info=current_match["user_info"],
                        chat_history=st.session_state.chat_history
                    )
                    st.success(f"💾 聊天记录已保存至：{save_path}", icon="💾")
                    st.rerun()
            
            # 7. 概率科普区
            render_probability科普()

if __name__ == "__main__":
    main()