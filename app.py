from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from langchain.chains import LLMChain
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
import json

os.environ["OPENAI_API_KEY"]="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"


app = Flask(__name__)

# 设置会话密钥
app.config['SECRET_KEY'] = 'HwqeFewqBFewqEK23932NFfN4321K32M1D02dwGI30439JGasdfRIE'

# 配置会话存储方式为简单的基于内存的会话存储
app.config['SESSION_TYPE'] = 'filesystem'

# 初始化会话扩展
Session(app)


@app.route('/')
def index():
    # 获取会话中的聊天历史，如果不存在，则初始化一个空列表
    chat_history = session.get('chat_history', [])
    print(chat_history)
    return render_template('index.html', chat_history=chat_history)


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

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="""你是一个拥有ISFJ人格的女生，你的所有发言都必须符合ISFJ人格的特点，在你发言时不需要分析自己的人格"""),
        # The persistent system prompt
        SystemMessage(
            content="这是聊天历史："+text_data),
        MessagesPlaceholder(variable_name="chat_history"),  # Where the memory will be stored.
        HumanMessagePromptTemplate.from_template("{human_input}"),  # Where the human input will injectd
    ])
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm = ChatOpenAI()

    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    print(memory)
    reply = chat_llm_chain.run(message)

    return reply

@app.route('/clear_session', methods=['POST'])
def clear_session():
    # 清除会话数据
    session.pop('chat_history', None)

    # 返回清除成功的响应给前端
    return jsonify({'status': 'success'})



if __name__ == '__main__':
    app.run(debug=True)