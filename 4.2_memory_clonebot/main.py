from roles import get_portrait, ROLE_MEMORY_MAP
from logic import init_memory_folder
from chat import get_chat_response
import time

def print_separator():
    """打印分隔线"""
    print("\n" + "="*50 + "\n")

def main():
    # 初始化记忆文件夹
    init_memory_folder()
    
    # 欢迎界面
    print("="*60)
    print("🎭 角色聊天助手（命令行版）")
    print(get_portrait())
    print("="*60)
    print("输入 'exit' 或 'quit' 退出程序")
    print("输入 'clear' 清空聊天历史")
    print("="*60 + "\n")
    
    # 角色选择
    print("📋 可选角色：")
    for idx, role in enumerate(ROLE_MEMORY_MAP.keys(), 1):
        print(f"   {idx}. {role}")
    
    while True:
        try:
            role_idx = input("\n请输入角色编号（1-5）：")
            if not role_idx.isdigit():
                print("❌ 请输入有效的数字！")
                continue
            role_idx = int(role_idx)
            if 1 <= role_idx <= len(ROLE_MEMORY_MAP):
                selected_role = list(ROLE_MEMORY_MAP.keys())[role_idx-1]
                break
            else:
                print(f"❌ 编号超出范围！请输入1-{len(ROLE_MEMORY_MAP)}之间的数字")
        except Exception as e:
            print(f"❌ 选择角色失败：{e}")
    
    print(f"\n✅ 已选择角色：{selected_role}")
    print_separator()
    
    # 初始化聊天历史
    chat_history = []
    
    # 聊天循环
    while True:
        # 获取用户输入
        user_input = input(f"你（{time.strftime('%H:%M:%S')}）：").strip()
        
        # 命令处理
        if user_input.lower() in ["exit", "quit"]:
            print(f"\n👋 感谢使用{selected_role}聊天助手，再见！")
            break
        if user_input.lower() == "clear":
            chat_history = []
            print("\n🗑️  聊天历史已清空")
            print_separator()
            continue
        if not user_input:
            print("❌ 输入不能为空，请重新输入")
            continue
        
        # 显示加载状态
        print(f"{selected_role}（{time.strftime('%H:%M:%S')}）：正在思考...", end="\r")
        
        try:
            # 获取AI回复
            response = get_chat_response(selected_role, user_input, chat_history)
            
            # 更新聊天历史（只保留最近10轮，避免消息过长）
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
            if len(chat_history) > 20:  # 10轮对话（每轮2条消息）
                chat_history = chat_history[-20:]
            
            # 显示回复
            print(f"{selected_role}（{time.strftime('%H:%M:%S')}）：{response}")
            print_separator()
        
        except Exception as e:
            print(f"\n❌ 出错了：{e}")
            print_separator()

if __name__ == "__main__":
    main()