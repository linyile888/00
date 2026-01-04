# ========== 新增：修复模块路径 ==========
import sys
import os

# 将项目根目录加入 Python 搜索路径（关键）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# ========== 原有导入调整 ==========
# 注意：particle_effect 和 transition_animation 的导入将在下面根据 pygame 可用性条件导入
import streamlit as st

# ========== 新增：兼容 pygame 缺失 ==========
# 延迟并有条件导入 pygame（避免在无 pygame 环境直接抛错）
try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception as e:
    pygame = None
    PYGAME_AVAILABLE = False
    print(f"[警告] pygame 未安装或不可用，已降级为无动画模式。异常：{e!r}")

# 根据 pygame 是否可用，条件导入或提供降级占位实现
# 定义占位类（当导入失败时使用）
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

# 如果 pygame 可用，尝试导入实际的类（如果文件存在且包含类定义）
if PYGAME_AVAILABLE:
    # 尝试导入 ParticleEffect
    try:
        # 先尝试绝对导入
        from particle_effect import ParticleEffect as _ParticleEffect
        ParticleEffect = _ParticleEffect
    except (ImportError, AttributeError):
        try:
            # 再尝试相对导入（当作为包导入时）
            from .particle_effect import ParticleEffect as _ParticleEffect
            ParticleEffect = _ParticleEffect
        except (ImportError, AttributeError):
            print(f"[警告] 无法导入 ParticleEffect，使用占位实现。")
    
    # 尝试导入 TransitionAnimation
    try:
        # 先尝试绝对导入
        from transition_animation import TransitionAnimation as _TransitionAnimation
        TransitionAnimation = _TransitionAnimation
    except (ImportError, AttributeError):
        try:
            # 再尝试相对导入（当作为包导入时）
            from .transition_animation import TransitionAnimation as _TransitionAnimation
            TransitionAnimation = _TransitionAnimation
        except (ImportError, AttributeError):
            print(f"[警告] 无法导入 TransitionAnimation，使用占位实现。")

import requests
import json
import numpy as np
import time

# 尝试多种方式导入配置，兼容在 Streamlit 部署时无法作为 package 导入 frontend 的情况
try:
    from frontend.config import FONT_PATH, BACKGROUND_IMAGE_PATH, BACKGROUND_IMAGE_PATHS, SURVEY_QUESTIONS
except Exception:
    try:
        from .config import FONT_PATH, BACKGROUND_IMAGE_PATH, BACKGROUND_IMAGE_PATHS, SURVEY_QUESTIONS
    except Exception:
        # 最后尝试把当前目录加入 sys.path 作为回退，然后按顶级模块导入
        _base = os.path.dirname(os.path.abspath(__file__))
        if _base not in sys.path:
            sys.path.insert(0, _base)
        try:
            from config import FONT_PATH, BACKGROUND_IMAGE_PATH, BACKGROUND_IMAGE_PATHS, SURVEY_QUESTIONS
        except Exception as e:
            print(f"[错误] 无法加载 config 模块：{e!r}，将使用内置默认值。")
            FONT_PATH = os.path.join(_base, "assets", "fonts", "PressStart2P-Regular.ttf")
            BACKGROUND_IMAGE_PATH = os.path.join(_base, "assets", "images", "background1.png")
            # 尝试加载所有背景图
            BACKGROUND_IMAGE_PATHS = []
            images_dir = os.path.join(_base, "assets", "images")
            if os.path.exists(images_dir):
                index = 1
                while True:
                    bg_path = os.path.join(images_dir, f"background{index}.png")
                    if os.path.exists(bg_path):
                        BACKGROUND_IMAGE_PATHS.append(bg_path)
                        index += 1
                    else:
                        break
            if not BACKGROUND_IMAGE_PATHS:
                BACKGROUND_IMAGE_PATHS = [BACKGROUND_IMAGE_PATH]
            SURVEY_QUESTIONS = []
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

# 加载所有背景图（按顺序）
bg_images = []
# 确保 BACKGROUND_IMAGE_PATHS 已定义
if 'BACKGROUND_IMAGE_PATHS' not in globals() or not BACKGROUND_IMAGE_PATHS:
    # 如果未定义或为空，尝试从默认路径加载
    _base = os.path.dirname(os.path.abspath(__file__))
    BACKGROUND_IMAGE_PATHS = []
    images_dir = os.path.join(_base, "assets", "images")
    if os.path.exists(images_dir):
        index = 1
        while True:
            bg_path = os.path.join(images_dir, f"background{index}.png")
            if os.path.exists(bg_path):
                BACKGROUND_IMAGE_PATHS.append(bg_path)
                index += 1
            else:
                break
    if not BACKGROUND_IMAGE_PATHS:
        BACKGROUND_IMAGE_PATHS = [os.path.join(_base, "assets", "images", "background1.png")]

for bg_path in BACKGROUND_IMAGE_PATHS:
    try:
        if os.path.exists(bg_path):
            img = Image.open(bg_path).resize((1200, 800))
            bg_images.append(img)
        else:
            print(f"[警告] 背景图文件不存在：{bg_path}")
    except Exception as e:
        print(f"[警告] 背景图未找到或无法打开：{bg_path}。异常：{e!r}")

# 如果没有加载到任何背景图，使用 None
if not bg_images:
    bg_images = [None]
    bg_image = None
else:
    # 默认使用第一张背景图
    bg_image = bg_images[0]

# 全局状态管理（存储问卷答案、匹配结果）
# 注意：session_state 初始化移到 main() 函数中，确保在 Streamlit 运行时正确初始化

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
    # 确保 session_state 已初始化
    if "bg_image_index" not in st.session_state:
        st.session_state.bg_image_index = 0
    if "transition_running" not in st.session_state:
        st.session_state.transition_running = False
    if "matched_partner" not in st.session_state:
        st.session_state.matched_partner = None
    
    if st.session_state.transition_running:
        if not PYGAME_AVAILABLE:
            # pygame 不可用时用 Streamlit 的占位提示替代动画
            with st.spinner("正在播放匹配动画（已降级，pygame 未安装）..."):
                time.sleep(2)
            st.session_state.transition_running = False
            st.rerun()

        # 以下为 pygame 可用时的原有动画逻辑
        animation_container = st.empty()
        screen = pygame.Surface((1200, 800))
        
        # 获取当前背景图索引（确保已初始化）
        if bg_images and len(bg_images) > 0 and all(img is not None for img in bg_images):
            current_bg_idx = st.session_state.bg_image_index % len(bg_images)
        else:
            current_bg_idx = 0

        particle_effect = ParticleEffect(1200, 800)
        transition_animation = TransitionAnimation(1200, 800)
        transition_animation.start()

        clock = pygame.time.Clock()
        animation_frame_count = 0
        frames_per_bg = 20  # 每20帧切换一张背景图
        
        # 获取有效的背景图列表
        valid_bg_images = [img for img in bg_images if img is not None] if bg_images else []
        
        while transition_animation.update():
            # 按顺序切换背景图
            if valid_bg_images and len(valid_bg_images) > 0:
                bg_idx = (current_bg_idx + animation_frame_count // frames_per_bg) % len(valid_bg_images)
                current_bg = valid_bg_images[bg_idx]
                if current_bg:
                    # 清空屏幕并绘制当前背景图
                    screen.fill((26, 26, 46))
                    try:
                        bg_surface = pygame.image.fromstring(current_bg.tobytes(), current_bg.size, current_bg.mode)
                        screen.blit(bg_surface, (0, 0))
                    except Exception as e:
                        print(f"[警告] 背景图转换失败：{e!r}")
                        screen.fill((26, 26, 46))
            else:
                screen.fill((26, 26, 46))
            
            particle_effect.update()
            particle_effect.draw(screen)
            transition_animation.draw(screen)
            
            try:
                # 推荐使用 surfarray 将 Surface 转为 numpy 数组，再转为 PIL Image
                arr = pygame.surfarray.array3d(screen)
                arr = np.transpose(arr, (1, 0, 2))
                frame = Image.fromarray(arr)
                animation_container.image(frame, use_container_width=True)
            except Exception as e:
                print(f"[错误] Surface -> PIL 转换失败：{e!r}")
                break
            
            animation_frame_count += 1
            clock.tick(60)
        
        # 动画结束后更新背景图索引
        valid_bg_images = [img for img in bg_images if img is not None] if bg_images else []
        if valid_bg_images and len(valid_bg_images) > 0:
            st.session_state.bg_image_index = (current_bg_idx + animation_frame_count // frames_per_bg) % len(valid_bg_images)

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
                st.image(partner_image, caption=f"{partner['era']} · {partner['occupation']}", use_container_width=True)
            except FileNotFoundError:
                st.image("https://via.placeholder.com/300x300?text=Partner", caption="伴侣形象", use_container_width=True)
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
    # 初始化 session_state（确保在使用前已初始化）
    # 使用 get() 方法安全地访问和初始化
    try:
        if "survey_answers" not in st.session_state:
            st.session_state.survey_answers = {}
        if "matched_partner" not in st.session_state:
            st.session_state.matched_partner = None
        if "transition_running" not in st.session_state:
            st.session_state.transition_running = False
        if "bg_image_index" not in st.session_state:
            st.session_state.bg_image_index = 0
        if "last_state" not in st.session_state:
            st.session_state.last_state = None
    except Exception as e:
        # 如果 session_state 不可用（直接运行脚本时），使用默认值
        print(f"[警告] session_state 不可用，使用默认值：{e!r}")
        # 创建本地变量作为后备
        local_state = {
            "survey_answers": {},
            "matched_partner": None,
            "transition_running": False,
            "bg_image_index": 0,
            "last_state": None
        }
        # 尝试设置到 session_state，如果失败则使用本地变量
        for key, value in local_state.items():
            try:
                if key not in st.session_state:
                    st.session_state[key] = value
            except:
                pass
    
    # 安全地获取 bg_image_index
    try:
        bg_image_index = st.session_state.get("bg_image_index", 0)
    except:
        bg_image_index = 0
    
    # 获取当前背景图（按顺序循环）
    # 确保 bg_images 存在且不为空
    if bg_images and len(bg_images) > 0:
        # 检查是否有有效的图片（不是 None）
        valid_images = [img for img in bg_images if img is not None]
        if valid_images:
            current_bg_index = bg_image_index % len(valid_images)
            current_bg_image = valid_images[current_bg_index]
        else:
            current_bg_image = None
    else:
        current_bg_image = None
    
    # 在动画或状态切换时，自动切换到下一张背景图
    try:
        transition_running = st.session_state.get("transition_running", False)
        matched_partner = st.session_state.get("matched_partner", None)
        last_state = st.session_state.get("last_state", None)
    except:
        transition_running = False
        matched_partner = None
        last_state = None
    
    if transition_running or (matched_partner and not transition_running):
        # 每次进入新状态时切换到下一张背景图
        current_state = "transition" if transition_running else "matched"
        if last_state != current_state:
            # 获取有效的背景图列表
            valid_images = [img for img in bg_images if img is not None] if bg_images else []
            if valid_images and len(valid_images) > 0:
                try:
                    bg_image_index = (bg_image_index + 1) % len(valid_images)
                    st.session_state.bg_image_index = bg_image_index
                    st.session_state.last_state = current_state
                    current_bg_index = bg_image_index % len(valid_images)
                    current_bg_image = valid_images[current_bg_index]
                except:
                    # 如果无法更新 session_state，至少更新本地变量
                    bg_image_index = (bg_image_index + 1) % len(valid_images)
                    current_bg_index = bg_image_index % len(valid_images)
                    current_bg_image = valid_images[current_bg_index]
            else:
                try:
                    st.session_state.last_state = current_state
                except:
                    pass
                current_bg_image = None
    
    if current_bg_image:
        # 显示背景图
        st.image(current_bg_image, use_container_width=True, caption="", output_format="PNG")
        # 叠加半透明遮罩（方便阅读文字）
        st.markdown("<div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); z-index: 1;'></div>", unsafe_allow_html=True)

    # 根据状态显示不同内容
    try:
        has_matched = st.session_state.get("matched_partner", None) is not None
        is_transitioning = st.session_state.get("transition_running", False)
    except:
        has_matched = False
        is_transitioning = False
    
    if has_matched and not is_transitioning:
        draw_transition_and_result()
    elif is_transitioning:
        draw_transition_and_result()
    else:
        draw_survey()
if __name__ == "__main__":
    main()