
import random
import re
import time

class ChatBot:
    def __init__(self):
        self.name = "小智"
        self.greetings = ["你好！", "嗨！", "很高兴见到你！", "你好呀！"]
        self.responses = {
            "你好": ["你好！有什么我可以帮助你的吗？", "嗨！今天过得怎么样？"],
            "天气": ["今天天气不错呢！", "我不太确定今天的天气，你可以查看天气预报。"],
            "名字": ["我叫小智，是一个聊天机器人。", "我是小智，很高兴认识你！"],
            "年龄": ["我是机器人，没有年龄的概念。", "我刚刚被创造出来不久。"],
            "爱好": ["我喜欢和人聊天，学习新知识。", "我的爱好是帮助人们解决问题。"],
            "再见": ["再见！希望下次再聊！", "很高兴和你聊天，再见！"]
        }
        self.end_phrases = ["再见", "拜拜", "下次聊", "结束对话", "结束", "bye", "goodbye", "see you"]
        self.conversation_count = 0
        self.max_conversation_turns = 10  # 设置最大对话轮次
        
    def get_response(self, user_input):
        """根据用户输入生成回复"""
        self.conversation_count += 1
        
        # 检查是否应该结束对话
        if self.should_end_conversation(user_input):
            return self.end_conversation()
        
        # 简单关键词匹配
        for keyword, responses in self.responses.items():
            if keyword in user_input:
                return random.choice(responses)
        
        # 默认回复
        return self.get_default_response()
    
    def should_end_conversation(self, user_input):
        """判断是否应该结束对话"""
        user_input_lower = user_input.lower()
        
        # 检查是否包含结束短语
        for phrase in self.end_phrases:
            if phrase in user_input_lower:
                return True
        
        # 检查对话是否过长
        if self.conversation_count >= self.max_conversation_turns:
            return True
            
        # 检查用户是否表现出结束意图
        if self.detect_end_intent(user_input):
            return True
            
        return False
    
    def detect_end_intent(self, user_input):
        """检测用户是否有结束对话的意图"""
        user_input_lower = user_input.lower()
        
        # 检查是否包含感谢或结束的暗示
        end_indicators = [
            r"谢谢.*聊天", r"聊天.*谢谢", r"很高兴.*聊天", r"聊天.*很高兴",
            r"就.*这样", r"没.*事.*了", r"没有.*问题.*了", r"结束.*对话",
            r"下次.*再聊", r"再联系", r"保持联系", r"我.*要.*走.*了",
            r"我.*有.*事", r"我.*忙", r"拜拜", r"再见"
        ]
        
        for pattern in end_indicators:
            if re.search(pattern, user_input_lower):
                return True
                
        return False
    
    def end_conversation(self):
        """结束对话的回复"""
        farewells = [
            "很高兴和你聊天！希望下次再聊！",
            "谢谢你的时间，期待下次对话！",
            "再见！祝你今天愉快！",
            "聊天很愉快，下次见！",
            "保重，希望很快能再和你聊天！"
        ]
        return random.choice(farewells)
    
    def get_default_response(self):
        """获取默认回复"""
        default_responses = [
            "很有趣的观点，能多告诉我一些吗？",
            "我不太确定我理解了，能换个方式说吗？",
            "这个话题很有意思，你是怎么想的？",
            "我还在学习中，能告诉我更多吗？",
            "这是个好问题，让我想想...",
            "你能详细说明一下吗？"
        ]
        return random.choice(default_responses)
    
    def get_greeting(self):
        """获取问候语"""
        return random.choice(self.greetings)
    
    def reset_conversation(self):
        """重置对话计数器"""
        self.conversation_count = 0

def main():
    bot = ChatBot()
    print(f"{bot.name}: {bot.get_greeting()}")
    
    while True:
        user_input = input("你: ").strip()
        
        if not user_input:
            print(f"{bot.name}: 你还在吗？")
            continue
            
        response = bot.get_response(user_input)
        print(f"{bot.name}: {response}")
        
        # 检查是否应该结束程序
        if bot.should_end_conversation(user_input):
            print(f"{bot.name}: 对话已结束。")
            break
        
        # 如果对话轮次过多，提示结束
        if bot.conversation_count >= bot.max_conversation_turns:
            print(f"{bot.name}: 我们已经聊了很多了，也许该休息一下了。")
            break

if __name__ == "__main__":
    main()

