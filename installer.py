import os

# 定義要建立的目錄結構
directories = [
    "client",
    "client/src",
    "server"
]

# 定義每個檔案的內容
files = {
    # --- 前端檔案 (Client) ---
    "client/package.json": """{
  "name": "study-hub-client",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "lucide-react": "^0.460.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "eslint": "^9.9.0",
    "eslint-plugin-react": "^7.35.0",
    "eslint-plugin-react-hooks": "^5.1.0-rc.0",
    "eslint-plugin-react-refresh": "^0.4.9",
    "globals": "^15.9.0",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "vite": "^5.4.1"
  }
}""",
    
    "client/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})""",

    "client/postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}""",

    "client/tailwind.config.js": """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}""",

    "client/index.html": """<!doctype html>
<html lang="zh-TW">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Study Hub</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",

    "client/src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  background-color: #e5e7eb;
}""",

    "client/src/main.jsx": """import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './index.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)""",

    "client/src/App.jsx": """import React, { useState, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Plus, Check, Edit2, RotateCw } from 'lucide-react';

const CATEGORIES = {
  EXAM: { id: 'exam', label: '考試', color: 'bg-red-500', border: 'border-l-4 border-red-500', text: 'text-red-700' },
  REPORT: { id: 'report', label: '報告', color: 'bg-green-500', border: 'border-l-4 border-green-500', text: 'text-green-700' },
  CANCEL: { id: 'cancel', label: '停課', color: 'bg-yellow-400', border: 'border-l-4 border-yellow-400', text: 'text-yellow-700' },
  OTHER: { id: 'other', label: '其他', color: 'bg-blue-400', border: 'border-l-4 border-blue-400', text: 'text-blue-700' }
};

export default function StudyHubApp() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [currentDate, setCurrentDate] = useState(new Date(2024, 10, 24)); 
  const [semesterStart, setSemesterStart] = useState(new Date(2024, 8, 1)); 
  
  const [aiSummary, setAiSummary] = useState("正在等待連線...");
  const [isLoadingAI, setIsLoadingAI] = useState(false);

  const [tasks, setTasks] = useState([
    { id: 1, date: '2024-11-24', category: 'exam', subject: '微積分', note: 'Ch1-3', completed: false },
    { id: 2, date: '2024-11-24', category: 'report', subject: '物理實驗', note: '結報', completed: true },
    { id: 3, date: '2024-11-25', category: 'cancel', subject: '體育', note: '老師請假', completed: false },
    { id: 4, date: '2024-11-26', category: 'other', subject: '社團', note: '迎新籌備', completed: false },
  ]);

  const [grades, setGrades] = useState([
    { id: 1, date: '2024-11-20', subject: '計算機概論', score: '85', note: '期中考' },
    { id: 2, date: '2024-11-22', subject: '英文', score: '92', note: '單字小考' },
  ]);

  const getWeekNumber = (date) => {
    const diff = date - semesterStart;
    const oneWeek = 1000 * 60 * 60 * 24 * 7;
    return Math.max(1, Math.ceil(diff / oneWeek));
  };

  const getWeekDays = (baseDate) => {
    const startOfWeek = new Date(baseDate);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1); 
    startOfWeek.setDate(diff);

    const days = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(startOfWeek);
      d.setDate(startOfWeek.getDate() + i);
      days.push(d);
    }
    return days;
  };

  const weekDays = useMemo(() => getWeekDays(currentDate), [currentDate]);
  const currentWeekNum = getWeekNumber(currentDate);

  const fetchAISummary = async () => {
    setIsLoadingAI(true);
    setAiSummary("正在思考中... (呼叫 Local LLM)");
    
    try {
      const response = await fetch('/api/summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tasks: tasks, current_date: currentDate.toISOString().split('T')[0] })
      });

      if (!response.ok) throw new Error("API Error");
      
      const data = await response.json();
      setAiSummary(data.summary);
    } catch (error) {
      console.warn("API Error:", error);
      setAiSummary("⚠️ 無法連線到後端 (Port 5000)。請確認 server/app.py 是否已啟動，以及 LMStudio 是否開啟。");
    } finally {
      setIsLoadingAI(false);
    }
  };

  useEffect(() => {
    fetchAISummary();
  }, []);

  const Header = () => (
    <div className="bg-white border-b border-gray-200 p-4 sticky top-0 z-10 shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <span className="bg-black text-white px-2 py-0.5 rounded text-sm">App</span>
            Study Hub
        </h1>
        <div className="flex bg-gray-100 p-1 rounded-lg">
          {['planner', 'grades', 'dashboard'].map(tab => (
             <button 
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1 rounded-md text-sm transition-all ${
                    activeTab === tab 
                    ? 'bg-white text-black font-bold shadow-sm' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
             >
                {{'planner': '聯絡簿', 'grades': '成績', 'dashboard': '行事曆'}[tab]}
             </button>
          ))}
        </div>
      </div>
      
      <div className="flex justify-between items-center bg-gray-50 p-2 rounded-lg border border-gray-100">
        <button onClick={() => {
          const newDate = new Date(currentDate);
          newDate.setDate(newDate.getDate() - 7);
          setCurrentDate(newDate);
        }} className="text-gray-400 hover:text-black flex items-center px-2">
          <ChevronLeft size={16} /> <span className="text-xs ml-1">上週</span>
        </button>
        
        <div className="text-center">
          <div className="text-sm font-bold text-gray-800">
            {weekDays[0].getMonth()+1}/{weekDays[0].getDate()} - {weekDays[6].getMonth()+1}/{weekDays[6].getDate()}
          </div>
          <div className="text-xs text-blue-600 font-medium bg-blue-50 px-2 rounded-full mt-1 inline-block">
            學期第 {currentWeekNum} 週
          </div>
        </div>

        <button onClick={() => {
          const newDate = new Date(currentDate);
          newDate.setDate(newDate.getDate() + 7);
          setCurrentDate(newDate);
        }} className="text-gray-400 hover:text-black flex items-center px-2">
          <span className="text-xs mr-1">下週</span> <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );

  const DashboardView = () => (
    <div className="p-4 space-y-4 h-full overflow-y-auto pb-24 no-scrollbar">
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
        <div className="grid grid-cols-7 text-xs text-center bg-gray-50 border-b border-gray-200 font-medium p-2">
          {weekDays.map((d, i) => (
            <div key={i} className={d.toDateString() === currentDate.toDateString() ? 'text-red-600 font-bold' : 'text-gray-500'}>
              {['一','二','三','四','五','六','日'][i]}<br/>
              <span className="text-[10px] mt-1 block">{d.getDate()}</span>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 h-16 divide-x divide-gray-100 bg-white">
           {weekDays.map((d, i) => {
             const dayTasks = tasks.filter(t => new Date(t.date).toDateString() === d.toDateString());
             return (
               <div key={i} className="p-1 flex flex-col gap-1 items-center justify-start py-2">
                 {dayTasks.map(t => (
                   <div key={t.id} className={`w-2 h-2 rounded-full ${CATEGORIES[t.category.toUpperCase()].color}`} title={t.subject}></div>
                 ))}
               </div>
             )
           })}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-indigo-100 p-5 shadow-sm relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-50 rounded-bl-full -mr-10 -mt-10 z-0 transition-transform group-hover:scale-110"></div>
        <div className="flex justify-between items-start relative z-10 mb-2">
            <h3 className="font-bold text-indigo-900 flex items-center">
            <span className="text-lg mr-2">✨</span> 本週 AI 摘要
            </h3>
            <button onClick={fetchAISummary} disabled={isLoadingAI} className="text-indigo-400 hover:text-indigo-600 transition-colors">
                <RotateCw size={14} className={isLoadingAI ? "animate-spin" : ""} />
            </button>
        </div>
        
        <p className="text-sm text-gray-600 leading-relaxed relative z-10 min-h-[60px] whitespace-pre-line">
          {aiSummary}
        </p>
        <div className="mt-3 flex justify-end relative z-10">
            <span className="text-[10px] text-gray-400 bg-gray-50 px-2 py-1 rounded">Backend: Flask + LMStudio</span>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 min-h-[250px] flex flex-col items-center justify-center text-gray-400 shadow-sm">
        <div className="text-2xl font-bold text-gray-300 mb-4">{currentDate.getMonth()+1} 月</div>
        <div className="grid grid-cols-7 gap-3 w-full text-center text-sm px-6">
           {Array.from({length: 30}).map((_, i) => (
             <div key={i} className={`aspect-square flex items-center justify-center rounded-lg text-xs 
                ${i+1 === currentDate.getDate() ? 'bg-black text-white shadow-md' : 'bg-gray-50'}`}>
                {i+1}
             </div>
           ))}
        </div>
      </div>
    </div>
  );

  const PlannerView = () => {
    const [newItem, setNewItem] = useState({ category: 'exam', subject: '', note: '' });
    
    const handleAdd = (dateStr) => {
      if (!newItem.subject) return;
      const newTask = {
        id: Date.now(),
        date: dateStr,
        category: newItem.category,
        subject: newItem.subject,
        note: newItem.note,
        completed: false
      };
      setTasks([...tasks, newTask]);
      setNewItem({ category: 'exam', subject: '', note: '' }); 
    };

    return (
      <div className="p-4 space-y-6 h-full overflow-y-auto pb-24 no-scrollbar">
        {weekDays.map((day) => {
          const dayTasks = tasks.filter(t => new Date(t.date).toDateString() === day.toDateString());
          const dateStr = day.toISOString().split('T')[0];
          
          return (
            <div key={dateStr} className="border border-gray-200 rounded-xl bg-white overflow-hidden shadow-sm">
              <div className="bg-gray-50 px-4 py-2 border-b border-gray-100 text-sm font-bold flex justify-between text-gray-700">
                <span>{day.getMonth()+1}/{day.getDate()} ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day.getDay() === 0 ? 6 : day.getDay()-1]})</span>
              </div>
              
              <div className="p-3 space-y-2">
                {dayTasks.map(task => {
                  const catStyle = CATEGORIES[task.category.toUpperCase()];
                  return (
                    <div key={task.id} className={`flex items-center justify-between text-sm ${catStyle.border} bg-white pl-3 py-2 rounded-r shadow-sm border-t border-r border-b border-gray-100 mb-1`}>
                      <div className="flex items-center gap-3 overflow-hidden flex-1">
                        <input 
                          type="checkbox" 
                          checked={task.completed}
                          onChange={() => {
                            setTasks(tasks.map(t => t.id === task.id ? {...t, completed: !t.completed} : t));
                          }}
                          className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                        />
                        <div className={`truncate flex-1 ${task.completed ? 'line-through text-gray-300 decoration-gray-400' : 'text-gray-800'}`}>
                          <span className={`font-bold mr-2 ${task.completed ? '' : 'text-black'}`}>{task.subject}</span>
                          <span className={`text-xs ${task.completed ? 'text-gray-300' : 'text-gray-500'}`}>{task.note}</span>
                        </div>
                      </div>
                      {task.completed && <Check size={14} className="text-gray-300 min-w-[14px]" />}
                    </div>
                  );
                })}

                <div className="flex items-center gap-2 mt-3 pt-2 border-t border-gray-100">
                  <select 
                    className="text-xs border border-gray-200 rounded p-1.5 bg-gray-50 outline-none focus:border-blue-500 transition-colors"
                    value={newItem.category}
                    onChange={(e) => setNewItem({...newItem, category: e.target.value})}
                  >
                    {Object.values(CATEGORIES).map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
                  </select>
                  <input 
                    type="text" 
                    placeholder="科目" 
                    className="text-xs border border-gray-200 rounded p-1.5 w-20 outline-none focus:border-blue-500 transition-colors"
                    onChange={(e) => setNewItem({...newItem, subject: e.target.value})}
                  />
                  <input 
                    type="text" 
                    placeholder="備註..." 
                    className="text-xs border border-gray-200 rounded p-1.5 flex-1 outline-none focus:border-blue-500 transition-colors"
                    onChange={(e) => setNewItem({...newItem, note: e.target.value})}
                  />
                  <button 
                    onClick={() => handleAdd(dateStr)}
                    className="p-1.5 bg-black text-white rounded hover:bg-gray-800 transition-colors"
                  >
                    <Plus size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const GradesView = () => {
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({});

    const startEdit = (grade) => {
      setEditingId(grade.id);
      setEditForm(grade);
    };

    const saveEdit = () => {
      setGrades(grades.map(g => g.id === editingId ? editForm : g));
      setEditingId(null);
    };

    return (
      <div className="p-4 h-full overflow-y-auto pb-24 no-scrollbar">
        <div className="mb-4 relative">
          <input 
            type="text" 
            placeholder="🔍 搜尋成績..." 
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm shadow-sm outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        <div className="space-y-4">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 ml-1">最近成績</div>
          {grades.map(grade => (
            <div key={grade.id} className="bg-white border-l-4 border-blue-500 shadow-sm rounded-r-xl p-4 flex flex-col gap-2 transition-transform active:scale-[0.99]">
               {editingId === grade.id ? (
                 <div className="flex flex-col gap-3 bg-blue-50 p-2 rounded-lg">
                   <div className="flex justify-between items-center gap-2">
                     <input value={editForm.subject} onChange={e=>setEditForm({...editForm, subject: e.target.value})} className="border border-blue-200 rounded p-1 text-sm font-bold w-1/2" />
                     <input value={editForm.score} onChange={e=>setEditForm({...editForm, score: e.target.value})} className="border border-blue-200 rounded p-1 text-sm font-bold w-16 text-right text-red-600" />
                   </div>
                   <input value={editForm.note} onChange={e=>setEditForm({...editForm, note: e.target.value})} className="border border-blue-200 rounded p-1 text-xs w-full" />
                   <button onClick={saveEdit} className="self-end bg-blue-600 text-white text-xs px-3 py-1.5 rounded-md font-medium">儲存</button>
                 </div>
               ) : (
                 <>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-bold text-gray-800 text-lg">{grade.subject}</h4>
                      <p className="text-xs text-gray-500 font-medium mt-0.5">{grade.date}</p>
                    </div>
                    <div className="text-2xl font-black text-gray-800">{grade.score}</div>
                  </div>
                  <div className="flex justify-between items-center text-sm text-gray-600 border-t border-gray-100 pt-3 mt-1">
                    <span className="bg-gray-100 px-2 py-0.5 rounded text-xs text-gray-600">{grade.note}</span>
                    <button onClick={() => startEdit(grade)} className="text-blue-500 text-xs flex items-center gap-1 hover:bg-blue-50 px-2 py-1 rounded transition-colors font-medium">
                      <Edit2 size={12} /> 編輯
                    </button>
                  </div>
                 </>
               )}
            </div>
          ))}
          <button className="w-full border-2 border-dashed border-gray-300 rounded-xl p-4 flex flex-col items-center justify-center text-gray-400 cursor-pointer hover:bg-gray-50 hover:border-gray-400 transition-colors group">
            <Plus size={24} className="group-hover:text-gray-600 transition-colors" />
            <span className="text-xs mt-2 font-medium group-hover:text-gray-600 transition-colors">新增成績紀錄</span>
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-gray-200 min-h-screen w-full flex justify-center items-center font-sans">
        <div className="w-full max-w-md bg-white h-[95vh] md:h-[850px] md:rounded-[3rem] md:border-8 md:border-gray-800 flex flex-col shadow-2xl overflow-hidden relative">
            <div className="hidden md:block absolute top-0 left-1/2 transform -translate-x-1/2 w-32 h-6 bg-gray-800 rounded-b-xl z-50"></div>
            
            <Header />
            
            <div className="flex-1 overflow-hidden relative bg-gray-50">
                {activeTab === 'dashboard' && <DashboardView />}
                {activeTab === 'planner' && <PlannerView />}
                {activeTab === 'grades' && <GradesView />}
            </div>
        </div>
    </div>
  );
}""",

    # --- 後端檔案 (Server) ---
    "server/requirements.txt": """flask
flask-cors
requests""",

    "server/app.py": """from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app) 

# LMStudio 設定
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

@app.route('/')
def home():
    return "Study Hub Backend is running!"

@app.route('/api/summary', methods=['POST'])
def generate_summary():
    try:
        data = request.json
        tasks = data.get('tasks', [])
        current_date = data.get('current_date', 'Unknown Date')
        
        task_desc = []
        for t in tasks:
            status = "已完成" if t.get('completed') else "未完成"
            cat_map = {'exam': '考試', 'report': '報告', 'cancel': '停課', 'other': '其他'}
            cat = cat_map.get(t.get('category'), '事項')
            task_desc.append(f"- {t['date']} [{cat}] {t['subject']}: {t['note']} ({status})")
        
        task_text = "\\n".join(task_desc) if task_desc else "本週無行程"

        system_prompt = "你是一個大學生私人助理。請根據行程表，用繁體中文生成一段簡短的『本週摘要』(100字內)。語氣自然。優先提醒未完成的考試與報告。"
        user_prompt = f"今天是 {current_date}。行程：\\n{task_text}"

        payload = {
            "model": "llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        resp = requests.post(LM_STUDIO_URL, json=payload, headers={"Content-Type": "application/json"})
        
        if resp.status_code == 200:
            return jsonify({"summary": resp.json()['choices'][0]['message']['content']})
        else:
            return jsonify({"summary": f"AI 回應錯誤: {resp.status_code}"}), 500

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"summary": f"伺服器錯誤: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""
}

def create_project():
    print("🚀 開始建立 StudyHub 專案...")
    
    # 1. 建立目錄
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📂 建立目錄: {directory}")

    # 2. 寫入檔案
    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📝 建立檔案: {filepath}")

    print("\\n✅ 安裝完成！請依照以下步驟啟動：")
    print("====================================")
    print("1. 開啟第一個終端機 (後端):")
    print("   cd server")
    print("   pip install -r requirements.txt")
    print("   python app.py")
    print("")
    print("2. 開啟第二個終端機 (前端):")
    print("   cd client")
    print("   npm install")
    print("   npm run dev")
    print("====================================")

if __name__ == "__main__":
    create_project()