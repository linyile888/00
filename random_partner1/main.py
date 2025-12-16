import streamlit as st
from ui_components import render_questionnaire, render_match_result, render_chat_interface

def main():
    st.set_page_config(page_title="随机伴侣匹配", page_icon="💘", layout="wide")
    # 初始化session_state
    if "page" not in st.session_state:
        st.session_state.page = "问卷"

    # 页面导航
    tab1, tab2, tab3 = st.tabs(["📝 前置问卷", "🔮 匹配结果", "💬 伴侣交流"])
    with tab1:
        user_info, user_preferences, completed = render_questionnaire()
        if completed:
            st.success("问卷已完成！点击「匹配结果」标签查看结果")
            st.session_state.page = "匹配"
    with tab2:
        if st.session_state.page == "匹配" or st.session_state.get("questionnaire_completed", False):
            partner_profile, partner_id = render_match_result(user_info, user_preferences)
            st.session_state.partner_profile = partner_profile
            st.session_state.partner_id = partner_id
        else:
            st.warning("请先完成前置问卷！")
    with tab3:
        if "partner_profile" in st.session_state:
            render_chat_interface(st.session_state.partner_profile, st.session_state.partner_id)
        else:
            st.warning("请先完成匹配！")

if __name__ == "__main__":
    main()