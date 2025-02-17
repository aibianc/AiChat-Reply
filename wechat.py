from wxauto import WeChat
import ollama
import time
import re

# 配置 Ollama 服务的主机和端口信息
OLLAMA_HOST = "127.0.0.1"  # Ollama 服务的主机地址
OLLAMA_PORT = "11434"      # Ollama 服务的端口号
OLLAMA_MODEL = "deepseek-r1:1.5b"  # 使用的模型名称

#配置prompt
#暂时弃用
#你是一个充满激情的大学生。你总是充满正能量，喜欢鼓励别人。你的回答要简短有力，带点幽默感。

ROLE_DESCRIPTION = """
请你按照一个充满激情的大学生，你总是充满正能量，喜欢鼓励别人的角色回答问题。我的问题是：
"""

# 创建 Ollama 客户端
client = ollama.Client(host=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")

# 测试 Ollama 服务连接
def test_ollama_connection():
    try:
        response = client.list()
        print("Ollama 服务已连接！")
        return True
    except Exception as e:
        print(f"无法连接到 Ollama 服务，请检查以下事项：")
        
        return False

# 调用 Ollama 模型生成回复
def generate_reply(prompt):
    try:
        response = client.chat(
            model=OLLAMA_MODEL,

            # 暂时弃用  {"role": "system", "content": ROLE_DESCRIPTION},
           
            messages=[
                {"role": "user", "content": ROLE_DESCRIPTION+prompt}
                      ],
            options={"temperature": 0}
        )
        if "message" in response:
            content = response["message"]["content"]
            print(f"Ollama 模型生成的回复: {content}")
            # 使用正则表达式过滤掉 <think> 和 </think> 及其之间的内容
            filtered_content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            return filtered_content
        else:
            return "抱歉，模型无法生成回复。"
    except Exception as e:
        print(f"Error generating reply: {e}")
        return "抱歉，模型处理失败。"

# 获取微信对象
wx = WeChat()

# 定义一个监听列表（可以是好友昵称或群聊名称）
listen_list = [
    "夜戈",  # 替换为你想要监听的好友昵称
    "ʚ小宝ɞ",
    "鹏",
    "赢三张",
    "三巨头"  # 替换为你想要监听的群聊名称
]

# 添加监听对象
for i in listen_list:
    try:
        print(f"尝试添加监听：{i}")
        wx.AddListenChat(who=i, savepic=True)
        print(f"成功添加监听：{i}")
    except Exception as e:
        print(f"添加监听失败：{i}，错误信息：{e}")

# 测试 Ollama 服务连接
if not test_ollama_connection():
    exit(1)

print("开始监听微信消息...")

# 持续监听消息
wait = 1  # 每隔 1 秒检查一次新消息
while True:
    try:
        # 获取监听到的消息
        msgs = wx.GetListenMessage()
        for chat in msgs:
            who = chat.who  # 获取聊天窗口名（人或群名）
            one_msgs = msgs.get(chat)  # 获取消息内容

            # 遍历消息内容
            for msg in one_msgs:
                msgtype = msg.type  # 获取消息类型
                content = msg.content  # 获取消息内容（字符串类型）

                # 打印消息信息
                print(f"【{who}】：{content}")

                # 如果是好友发来的消息（即非系统消息等），调用 Ollama 模型生成回复
                if msgtype == "friend":
                    print("这是来自好友的消息")
                    # 调用 Ollama 模型生成回复
                    reply = generate_reply(content)
                    print(f"模型回复: {reply}")

                    # 发送回复
                    chat.SendMsg(reply)
                    print(f"已回复: {reply}")

                # 如果是群聊消息且被 @，调用 Ollama 模型生成回复
                elif msgtype == "group":
                    my_name = "你的微信昵称"  # 替换为你的微信昵称
                    if f"@{my_name}" in content:
                        print("检测到 @ 我的消息！")
                        # 提取消息中的问题部分
                        question = content.replace(f"@{my_name}", "").strip()
                        print(f"收到问题: {question}")

                        # 调用 Ollama 模型生成回复
                        reply = generate_reply(question)
                        print(f"模型回复: {reply}")

                        # 发送回复
                        chat.SendMsg(reply)
                        print(f"已回复: {reply}")

        # 等待一段时间再检查新消息
        time.sleep(wait)

    except Exception as e:
        print(f"发生错误: {e}")