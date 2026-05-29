from flask import Flask, jsonify, request, render_template
import sqlite3
import random

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')

DB_NAME = 'english_hero.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 1. 頁面路由：渲染主頁
@app.route('/')
def index():
    return render_template('index.html')

# 2. 隨機取得題目 API
@app.route('/api/questions', methods=['GET'])
def get_questions():
    mode = request.args.get('mode', 'mixed')  # vocab, grammar, mixed
    level = request.args.get('level', 'all')  # all, Elementary, Junior, Senior
    tense = request.args.get('tense', 'all')  # all or specific tense
    limit = int(request.args.get('limit', 10))

    questions = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 取得單字題目
        if mode in ['vocab', 'mixed']:
            query = "SELECT * FROM words"
            params = []
            if level != 'all':
                query += " WHERE level = ?"
                params.append(level)
            
            cursor.execute(query, params)
            words = cursor.fetchall()
            
            for w in words:
                opts = [w['definition'], w['option1'], w['option2'], w['option3']]
                random.shuffle(opts)
                questions.append({
                    'id': w['id'],
                    'type': 'vocab',
                    'category': w['level'],
                    'prompt': f"請選出英文單字 [ {w['word']} ] 的正確中文意思：",
                    'detail': w['word'],
                    'correct': w['definition'],
                    'options': opts,
                    'analysis': w['analysis']
                })

        # 取得文法題目
        if mode in ['grammar', 'mixed']:
            query = "SELECT * FROM grammar_questions"
            params = []
            if tense != 'all':
                query += " WHERE tense = ?"
                params.append(tense)

            cursor.execute(query, params)
            grammar = cursor.fetchall()

            for g in grammar:
                opts = [g['correct_answer'], g['option1'], g['option2'], g['option3']]
                random.shuffle(opts)
                questions.append({
                    'id': g['id'],
                    'type': 'grammar',
                    'category': g['tense'],
                    'prompt': "請選擇最適合的單字完成句子：",
                    'detail': g['question'],
                    'correct': g['correct_answer'],
                    'options': opts,
                    'analysis': g['analysis']
                })

    # 隨機打亂並限制數量
    random.shuffle(questions)
    return jsonify(questions[:limit])

# 3. 單字庫管理 API (CRUD)
@app.route('/api/words', methods=['GET'])
def list_words():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words ORDER BY id DESC")
        words = [dict(row) for row in cursor.fetchall()]
    return jsonify(words)

@app.route('/api/words', methods=['POST'])
def add_word():
    data = request.json
    required_fields = ['word', 'definition', 'level', 'option1', 'option2', 'option3', 'analysis']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': '欄位填寫不完整'}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO words (word, definition, level, option1, option2, option3, analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['word'], data['definition'], data['level'], 
                  data['option1'], data['option2'], data['option3'], data['analysis']))
            conn.commit()
        return jsonify({'message': '單字新增成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/words/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
            conn.commit()
        return jsonify({'message': '單字刪除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. 文法題庫管理 API (CRUD)
@app.route('/api/grammar', methods=['GET'])
def list_grammar():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM grammar_questions ORDER BY id DESC")
        grammar = [dict(row) for row in cursor.fetchall()]
    return jsonify(grammar)

@app.route('/api/grammar', methods=['POST'])
def add_grammar():
    data = request.json
    required_fields = ['question', 'correct_answer', 'option1', 'option2', 'option3', 'tense', 'analysis']

    if not all(field in data for field in required_fields):
        return jsonify({'error': '欄位填寫不完整'}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO grammar_questions (question, correct_answer, option1, option2, option3, tense, analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['question'], data['correct_answer'], 
                  data['option1'], data['option2'], data['option3'], data['tense'], data['analysis']))
            conn.commit()
        return jsonify({'message': '文法題目新增成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/grammar/<int:q_id>', methods=['DELETE'])
def delete_grammar(q_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM grammar_questions WHERE id = ?", (q_id,))
            conn.commit()
        return jsonify({'message': '文法題目刪除成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 5. 學習數據 API
@app.route('/api/stats', methods=['GET'])
def get_stats():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM words")
        total_words = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM grammar_questions")
        total_grammar = cursor.fetchone()[0]
        
        # 難度分佈
        cursor.execute("SELECT level, COUNT(*) FROM words GROUP BY level")
        levels = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 時態分佈
        cursor.execute("SELECT tense, COUNT(*) FROM grammar_questions GROUP BY tense")
        tenses = {row[0]: row[1] for row in cursor.fetchall()}
        
    return jsonify({
        'total_words': total_words,
        'total_grammar': total_grammar,
        'levels': levels,
        'tenses': tenses
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
