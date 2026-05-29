from flask import Flask, jsonify, request, render_template
import sqlite3
import random

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')

def get_db_connection():
    conn = sqlite3.connect('english_hero.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# API：撈取題目（隨機決定考單字還是考文法時態變化）
@app.route('/api/get_question')
def get_question():
    level = request.args.get('level', '現在')  # 接收篩選時態 (現在/過去/未來)
    conn = get_db_connection()
    row = conn.execute(
        'SELECT * FROM grammar_quiz WHERE tense_category = ? ORDER BY RANDOM() LIMIT 1', 
        (level,)
    ).fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': '資料庫裡沒有題目囉'}), 404
        
    # 隨機決定這一題要考「單字意思」還是「文法時態」
    quiz_type = random.choice(['vocabulary', 'grammar'])
    
    if quiz_type == 'vocabulary':
        # 題型一：考中文意思
        question_text = f"請問動詞 【 {row['verb_base']} 】 的中文意思是什麼？"
        correct_answer = row['chinese_meaning']
        
        # 取得其他單字的中文意思作為干擾選項
        conn = get_db_connection()
        other_rows = conn.execute('SELECT chinese_meaning FROM grammar_quiz WHERE id != ?', (row['id'],)).fetchall()
        conn.close()
        
        distractors = [r['chinese_meaning'] for r in other_rows if r['chinese_meaning'] != correct_answer]
        
        # 確保不重複且如果少於 3 個就用預設詞彙補足
        fallback = ['學習', '看見', '跳舞', '歌唱', '飛翔', '睡覺', '玩耍']
        for item in fallback:
            if len(distractors) >= 3:
                break
            if item != correct_answer and item not in distractors:
                distractors.append(item)
                
        # 隨機選出三個錯誤答案，並與正確答案組合
        options = [correct_answer] + random.sample(distractors, 3)
    else:
        # 題型二：考文法時態與動詞變化
        question_text = f"【時態文法題 - {row['tense_category']}{row['aspect_category']}式】<br><br>{row['sentence_question']}"
        correct_answer = row['correct_answer']
        options = [row['correct_answer'], row['wrong_option1'], row['wrong_option2'], row['wrong_option3']]
        
    # 去除重複選項並打亂
    options = list(set(options))
    random.shuffle(options)
    
    return jsonify({
        'id': row['id'],
        'quiz_type': quiz_type,
        'question': question_text,
        'options': options
    })

# API：驗證答案
@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    word_id = data.get('id')
    user_answer = data.get('answer')
    quiz_type = data.get('quiz_type')
    
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM grammar_quiz WHERE id = ?', (word_id,)).fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': '找不到該單字'}), 404
        
    # 再次計算正確答案來比對
    if quiz_type == 'vocabulary':
        correct_answer = row['chinese_meaning']
    else:
        correct_answer = row['correct_answer']
            
    is_correct = (correct_answer.strip() == user_answer.strip())
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct_answer,
        'analysis': row['detailed_analysis']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
