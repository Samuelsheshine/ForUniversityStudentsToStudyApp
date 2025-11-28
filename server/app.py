from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
# 啟用 CORS
CORS(app) 

# LMStudio 連線設定
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

@app.route('/')
def home():
    return "Study Hub Backend is running!"

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    接收前端傳來的對話歷史 (messages)，轉發給 LMStudio
    """
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # 建構請求 Payload
        payload = {
            "model": "local-model", # 使用 LM Studio 當前載入的模型
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800,      # 增加回覆長度上限
            "stream": False
        }

        # 發送請求給 LM Studio
        resp = requests.post(
            LM_STUDIO_URL, 
            json=payload, 
            headers={"Content-Type": "application/json"}
        )
        
        if resp.status_code == 200:
            ai_response = resp.json()
            reply_content = ai_response['choices'][0]['message']['content']
            return jsonify({"reply": reply_content})
        else:
            error_msg = f"LM Studio Error: {resp.status_code} - {resp.text}"
            print(error_msg)
            return jsonify({"error": error_msg}), 500

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "無法連線到 LMStudio，請確認 Local Server (Port 1234) 已啟動。"}), 503
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": f"伺服器內部錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)