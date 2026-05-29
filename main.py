from flask import Flask, jsonify, request, render_template
import sqlite3
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('english_hero.db')
    conn.row_factory = sqlite3.Row  # 讓查詢結果可以像字典一樣用欄位名讀取
    return conn

@app.route('/')
def index():
    # 預設渲染前端介面
    return render_template('index.html')

# API 1：隨機取得該難度的單字
@app.route('/api/get_question')
def get_question():
    level = request.args.get('level', 'Elementary')
    conn = get_db_connection()
    
    # 根據難度隨機撈取一筆單字
    row = conn.execute(
        'SELECT * FROM words WHERE level = ? ORDER BY RANDOM() LIMIT 1', 
        (level,)
    ).fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': '該難度目前沒有單字資料'}), 404
        
    # 把正確答案與三個錯誤答案混在一起打亂
    options = [row['definition'], row['option1'], row['option2'], row['option3']]
    random.shuffle(options)
    
    return jsonify({
        'id': row['id'],
        'word': row['word'],
        'options': options
    })

# API 2：驗證答案，如果錯了就回傳解析
@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    word_id = data.get('id')
    user_answer = data.get('answer')
    
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM words WHERE id = ?', (word_id,)).fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': '找不到該單字'}), 404
        
    is_correct = (row['definition'] == user_answer)
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': row['definition'],
        'analysis': row['analysis']  # 無論對錯都回傳，但前端可以選擇在錯的時候彈出來
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
