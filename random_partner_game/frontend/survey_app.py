import streamlit as st

# 延迟并有条件导入 pygame（避免在无 pygame 环境直接抛错）
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception as e:
    pygame = None
    PYGAME_AVAILABLE = False
    print(f"[警告] pygame 未安装或不可用，已降级为无动画模式。异常：{e!r}")

# 根据 pygame 是否可用，条件导入或提供降级占位实现
if PYGAME_AVAILABLE:
    from .particle_effect import ParticleEffect
    from frontend.transition_animation import TransitionAnimation
else:
    class ParticleEffect:
        def __init__(self, w, h): 
            pass
        def update(self): 
            pass
        def draw(self, surface): 
            pass

    class TransitionAnimation:
        def __init__(self, w, h): 
            pass
        def start(self): 
            pass
        def update(self): 
            return False
        def draw(self, surface): 
            pass

import requests
import json
import sys
import numpy as np
from frontend.config import FONT_PATH, BACKGROUND_IMAGE_PATH, SURVEY_QUESTIONS
from PIL import Image

# 初始化Pygame（用于粒子和动画）
if PYGAME_AVAILABLE:
    pygame.init()

# 加载像素字体（报错预判：字体文件缺失）
try:
    if PYGAME_AVAILABLE:
        pygame_font = pygame.font.Font(FONT_PATH, 24)
    else:
        raise FileNotFoundError()
except Exception as e:
    print(f"[警告] 像素字体未找到或 pygame 不可用，请检查路径：{FONT_PATH}，使用默认字体替代。异常：{e!r}")
    pygame_font = None

# Streamlit页面配置（星露谷风：复古像素）
st.set_page_config(
    page_title="随机伴侣 - 问卷匹配",
    page_icon="❤️",
    layout="wide"
)

# 隐藏Streamlit默认边框和菜单（美化）
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #1a1a2e;}  # 深色背景（星露谷复古风）
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# 加载像素背景（报错预判：背景图路径错误）
try:
    bg_image = Image.open(BACKGROUND_IMAGE_PATH).resize((1200, 800))
except Exception as e:
    print(f"[警告] 问卷背景图未找到或无法打开，请检查路径：{BACKGROUND_IMAGE_PATH}。异常：{e!r}")
    bg_image = None

# 全局状态管理（存储问卷答案、匹配结果）
if "survey_answers" not in st.session_state:
    st.session_state.survey_answers = {}
if "matched_partner" not in st.session_state:
    st.session_state.matched_partner = None
if "transition_running" not in st.session_state:
    st.session_state.transition_running = False

# 后端接口地址（固定，无需改动，与backend/app.py端口一致）
BACKEND_API_URL = "http://localhost:5000/api"

# 1. 绘制问卷页面
def draw_survey():
    st.markdown("<h1 style='text-align: center; color: #ffd700; font-family: Press Start 2P; font-size: 32px;'>✨ 寻找你的随机伴侣 ✨</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #ff69b4;'>", unsafe_allow_html=True)

    # 渲染问卷题目
    for question in SURVEY_QUESTIONS:
        st.markdown(f"<h3 style='color: #00ffff; font-family: Press Start 2P; font-size: 18px;'>{question['title']}</h3>", unsafe_allow_html=True)
        if question["type"] == "select":
            answer = st.selectbox(
                label=question["title"],
                options=question["options"],
                key=question["id"],
                index=0,
                label_visibility="collapsed"  # 隐藏默认标签
            )
            st.session_state.survey_answers[question["id"]] = answer
        elif question["type"] == "checkbox":
            answers = st.multiselect(
                label=question["title"],
                options=question["options"],
                key=question["id"],
                label_visibility="collapsed"
            )
            st.session_state.survey_answers[question["id"]] = ",".join(answers)  # 用逗号拼接多选结果
        elif question["type"] == "number":
            answer = st.number_input(
                label=question["title"],
                min_value=question["min"],
                max_value=question["max"],
                key=question["id"],
                label_visibility="collapsed"
            )
            st.session_state.survey_answers[question["id"]] = answer

    # 提交按钮（星露谷风样式）
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_btn = st.button(
            label="💘 提交问卷，寻找伴侣",
            type="primary",
            use_container_width=True
        )
        if submit_btn:
            # 验证所有必填字段已填写
            all_filled = True
            for question in SURVEY_QUESTIONS:
                if question["id"] not in st.session_state.survey_answers or not st.session_state.survey_answers[question["id"]]:
                    all_filled = False
                    st.error(f"请填写「{question['title']}」！")
            if all_filled:
                # 提交问卷数据到后端
                submit_survey_data()

# 2. 提交问卷数据到后端
def submit_survey_data():
    try:
        # 发送POST请求到后端
        response = requests.post(
            f"{BACKEND_API_URL}/submit_survey",
            json=st.session_state.survey_answers,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        if result["status"] == "success":
            st.session_state.matched_partner = result["matched_partner"]
            # 触发穿越动画
            st.session_state.transition_running = True
            # 延迟后跳转到游戏页面（Streamlit无页面跳转，用状态控制）
            st.rerun()
        else:
            st.error(f"提交失败：{result['message']}")
    except requests.exceptions.Timeout:
        st.error("连接后端超时，请检查后端服务是否运行！")
    except requests.exceptions.ConnectionError:
        st.error("无法连接后端，请确保backend/app.py已启动（端口5000）！")
    except Exception as e:
        st.error(f"提交失败：{str(e)}")

# 3. 绘制穿越动画和匹配结果
def draw_transition_and_result():
    if st.session_state.transition_running:
        if not PYGAME_AVAILABLE:
            # pygame 不可用时用 Streamlit 的占位提示替代动画
            with st.spinner("正在播放匹配动画（已降级，pygame 未安装）..."):
                st.sleep(2)
            st.session_state.transition_running = False
            st.rerun()

        # 以下为 pygame 可用时的原有动画逻辑
        animation_container = st.empty()
        screen = pygame.Surface((1200, 800))
        if bg_image:
            screen.blit(pygame.image.fromstring(bg_image.tobytes(), bg_image.size, bg_image.mode), (0, 0))
        else:
            screen.fill((26, 26, 46))

        particle_effect = ParticleEffect(1200, 800)
        transition_animation = TransitionAnimation(1200, 800)
        transition_animation.start()

        clock = pygame.time.Clock()
        while transition_animation.update():
            particle_effect.update()
            particle_effect.draw(screen)
            transition_animation.draw(screen)
            try:
                # 推荐使用 surfarray 将 Surface 转为 numpy 数组，再转为 PIL Image
                arr = pygame.surfarray.array3d(screen)
                arr = np.transpose(arr, (1, 0, 2))
                frame = Image.fromarray(arr)
                animation_container.image(frame, use_column_width=True)
            except Exception as e:
                print(f"[错误] Surface -> PIL 转换失败：{e!r}")
                break
            clock.tick(60)

        st.session_state.transition_running = False
        st.rerun()

    # 显示匹配结果
    if st.session_state.matched_partner:
        partner = st.session_state.matched_partner
        st.markdown("<h1 style='text-align: center; color: #ffd700; font-family: Press Start 2P; font-size: 32px;'>🎉 匹配成功！ 🎉</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #ff69b4; font-family: Press Start 2P; font-size: 24px;'>你的伴侣是：{partner['name']}</h2>", unsafe_allow_html=True)

        # 显示伴侣信息（星露谷风卡片）
        col1, col2 = st.columns([1, 2])
        with col1:
            # 加载伴侣像素图（报错预判：图片缺失）
            try:
                partner_image = Image.open(f"frontend/assets/images/{partner['pixel_image']}").resize((300, 300))
                st.image(partner_image, caption=f"{partner['era']} · {partner['occupation']}", use_column_width=True)
            except FileNotFoundError:
                st.image("https://via.placeholder.com/300x300?text=Partner", caption="伴侣形象", use_column_width=True)
                print(f"[警告] 伴侣像素图未找到：frontend/assets/images/{partner['pixel_image']}")

        with col2:
            st.markdown("<div style='background-color: #2c2c54; padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00ffff; font-family: Press Start 2P; font-size: 16px;'>性格：{partner['personality']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00ffff; font-family: Press Start 2P; font-size: 16px;'>爱好：{partner['hobby']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00ffff; font-family: Press Start 2P; font-size: 16px;'>年龄：{partner['age']}岁</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00ffff; font-family: Press Start 2P; font-size: 16px;'>身高：{partner['height']}cm</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00ffff; font-family: Press Start 2P; font-size: 16px;'>体重：{partner['weight']}kg</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #ffd700; font-family: Press Start 2P; font-size: 16px;'>匹配度：{partner['match_score']*100:.0f}%</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 进入游戏按钮
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 进入相遇场景", type="primary", use_container_width=True):
                # 启动像素游戏（独立窗口运行）
                import subprocess
                subprocess.Popen([sys.executable, "frontend/pixel_game.py", str(partner["id"])])

# 主页面逻辑
def main():
    if bg_image:
        # 显示背景图
        st.image(bg_image, use_column_width=True, caption="", output_format="PNG")
        # 叠加半透明遮罩（方便阅读文字）
        st.markdown("<div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); z-index: 1;'></div>", unsafe_allow_html=True)

    # 根据状态显示不同内容
    if st.session_state.matched_partner and not st.session_state.transition_running:
        draw_transition_and_result()
    elif st.session_state.transition_running:
        draw_transition_and_result()
    else:
        draw_survey()
if __name__ == "__main__":
    main()