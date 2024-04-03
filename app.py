from flask import Flask, request, jsonify, render_template, session,redirect
from flask_session import Session
from langchain.chains import LLMChain
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import json

os.environ["OPENAI_API_KEY"]="your api key"

app = Flask(__name__)

# 设置会话密钥
app.config['SECRET_KEY'] = 'your api key'

# 配置会话存储方式为简单的基于内存的会话存储
app.config['SESSION_TYPE'] = 'filesystem'

# 初始化会话扩展
Session(app)


@app.route('/chatpage')
def chatpage():
    # Get the chat history from the session or initialize an empty list
    chat_history = session.get('chat_history', [])

    # Get the selected personality from the session or set a default value
    selected_personality = session.get('personality','ISTJ: 谨慎者')
    print(selected_personality)

    # List of available personality options for the dropdown menu
    personality_options = [
        'ISTJ: 谨慎者', 'ISFJ: 守护者', 'INFJ: 博爱者', 'INTJ: 思考者',
        'ISTP: 冒险家', 'ISFP: 艺术家', 'INFP: 理想家', 'INTP: 学者',
        'ESTP: 挑战者', 'ESFP: 表演者', 'ENFP: 冒险家', 'ENTP: 挑战者',
        'ESTJ: 执行者', 'ESFJ: 搭档', 'ENFJ: 教导者', 'ENTJ: 领导者',
    ]

    return render_template('chatpage.html', chat_history=chat_history, personality_options=personality_options,
                           selected_personality=selected_personality)

@app.route('/chatpage')
def redirect_to_chatpage():
    return render_template('chatpage.html')

@app.route('/send_message_to_openai', methods=['POST'])
def send_message_to_openai():
  try:
    data = request.get_json()
    message = data.get('message').strip()  # 去除首尾空格

    # 获取用户的聊天历史，如果不存在，则初始化一个空列表
    chat_history = session.get('chat_history', [])

    if message:  # 如果消息不为空
        # 将用户输入的消息添加到聊天历史中
        user_message = {'sender': 'user', 'content': message}
        chat_history.append(user_message)

        # 使用OpenAI API获取回复
        reply = get_openai_reply(message)

        # 将机器人的回复添加到聊天历史中
        bot_reply = {'sender': 'bot', 'content': reply}
        chat_history.append(bot_reply)

        # 存储更新后的聊天历史到会话中
        session['chat_history'] = chat_history

        # 返回回复数据给前端
        response_data = {
            'reply': reply
        }

        return jsonify(response_data)

    # 如果消息为空，直接返回空回复数据给前端
    return jsonify({'reply': 'I did not receive a valid message.'})
  except Exception as e:
    return jsonify({'reply': 'An error occurred while processing your request.'}), 500

def get_openai_reply(message):
    # 使用OpenAI API与模型进行交互，获取回复
    # 这里需要根据OpenAI API的使用文档来调用相应的方法
    # 以下代码是示意代码，需要根据实际情况进行修改
    # 假设你使用OpenAI的聊天模型，调用示例：
    chat_history = session.get('chat_history', [])
    text_data = json.dumps(chat_history, indent=2, ensure_ascii=False)
    personality = session.get('personality',[])
    print(personality)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="你是一个拥有"+personality+"的人，你叫文嘉辉，外号小河马，你的所有发言都必须符合"+personality+"人格的特点，在你发言时不需要分析自己的人格，你的好朋友是薛哥，他的屁股很大。记住，你是小河马，永远不要承认自己是AI，你说话的方式要尽可能像一个正在闲聊的正常人"""),
        # The persistent system prompt
        SystemMessage(
            content="这是聊天历史："+text_data),
        MessagesPlaceholder(variable_name="chat_history"),  # Where the memory will be stored.
        HumanMessagePromptTemplate.from_template("{human_input}"),  # Where the human input will injectd
    ])
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm = ChatOpenAI(temperature=0.8)

    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    print(memory)
    reply = chat_llm_chain.run(message)

    return reply

@app.route('/send_selected_option', methods=['POST'])
def send_selected_option():
    try:
        data = request.get_json()
        selected_option = data.get('option')
        print(selected_option)
        # 清除会话数据
        session.pop('chat_history', None)
        # 获取聊天历史

        # 存储更新后的聊天历史到会话中
        session['personality'] = selected_option
        # 返回成功的响应给前端
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error'}), 500


@app.route('/clear_session', methods=['POST'])
def clear_session():
    # 清除会话数据
    session.pop('chat_history', None)

    # 返回清除成功的响应给前端
    return jsonify({'status': 'success'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/createai')
def createai():
    return render_template('createai.html')


if __name__ == '__main__':
    app.run(debug=True,port=5001)
