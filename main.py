from flask import Flask, jsonify, request, render_template
import sqlite3
import random

app = Flask(__name__)

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
    level = request.args.get('level', 'Elementary')
    conn = get_db_connection()
    row = conn.execute(
        'SELECT * FROM words WHERE level = ? ORDER BY RANDOM() LIMIT 1', 
        (level,)
    ).fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': '資料庫裡沒有題目囉'}), 404
        
    # 隨機決定這一題要考「單字意思」還是「文法時態」
    quiz_type = random.choice(['vocabulary', 'grammar'])
    
    if quiz_type == 'vocabulary':
        # 題型一：考中文意思
        question_text = f"請問單字 【 {row['word']} 】 的中文意思是什麼？"
        correct_answer = row['definition']
        options = [row['definition'], row['option1'], row['option2'], row['option3']]
    else:
        # 題型二：考文法時態與動詞變化
        question_text = f"【文法時態題 - {row['grammar_type']}】<br><br>{row['sentence_q']}"
        
        # 根據不同的題目動態抓取正確答案
        if row['grammar_type'] == '現在完成式':
            correct_answer = row['verb_vpp']
        elif row['grammar_type'] == '過去進行式':
            # 這裡簡單依據主詞 Mary 加上 Be 動詞
            correct_answer = f"was {row['verb_ing']}"
        elif row['grammar_type'] == '未來完成式':
            correct_answer = f"will have {row['verb_vpp']}"
        else:
            correct_answer = row['word']
            
        # 建立文法干擾選項（把原型、V-ing、V-pp 還有其他時態混在一起考你）
        options = [
            correct_answer, 
            row['word'], 
            row['verb_ing'], 
            f"had {row['verb_vpp']}"
        ]
        
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
    row = conn.execute('SELECT * FROM words WHERE id = ?', (word_id,)).fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': '找不到該單字'}), 404
        
    # 再次計算正確答案來比對
    if quiz_type == 'vocabulary':
        correct_answer = row['definition']
    else:
        if row['grammar_type'] == '現在完成式':
            correct_answer = row['verb_vpp']
        elif row['grammar_type'] == '過去進行式':
            correct_answer = f"was {row['verb_ing']}"
        elif row['grammar_type'] == '未來完成式':
            correct_answer = f"will have {row['verb_vpp']}"
        else:
            correct_answer = row['word']
            
    is_correct = (correct_answer.strip() == user_answer.strip())
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct_answer,
        'analysis': row['analysis']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
