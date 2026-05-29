import sqlite3
import os

DB_NAME = 'english_hero.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. 建立單字題庫表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,         -- 英文單字
            definition TEXT NOT NULL,   -- 中文意思（正確答案）
            level TEXT NOT NULL,        -- 難度：Elementary(國小), Junior(國中), Senior(高中)
            option1 TEXT NOT NULL,      -- 錯誤選項 1
            option2 TEXT NOT NULL,      -- 錯誤選項 2
            option3 TEXT NOT NULL,      -- 錯誤選項 3
            analysis TEXT NOT NULL      -- 寫錯時的詳細解析
        )
    ''')
    
    # 2. 建立時態文法題庫表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammar_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,      -- 題目（例如: "She ___ to school every day."）
            correct_answer TEXT NOT NULL,-- 正確答案（例如: "goes"）
            option1 TEXT NOT NULL,       -- 錯誤選項 1
            option2 TEXT NOT NULL,       -- 錯誤選項 2
            option3 TEXT NOT NULL,       -- 錯誤選項 3
            tense TEXT NOT NULL,         -- 時態類型（例如: "Present Simple"）
            analysis TEXT NOT NULL       -- 寫錯時的詳細解析
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # 執行資料植入
    seed_data()

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 檢查 words 表是否已有資料
    cursor.execute('SELECT COUNT(*) FROM words')
    if cursor.fetchone()[0] == 0:
        words_data = [
            # Elementary 國小
            ('apple', '蘋果', 'Elementary', '香蕉', '貓', '狗', 'apple 是蘋果。'),
            ('elephant', '大象', 'Elementary', '獅子', '老虎', '猴子', 'elephant 是大象，字首是元音 e，常用 an elephant。'),
            ('beautiful', '美麗的', 'Elementary', '醜陋的', '生氣的', '開心的', 'beautiful 形容美麗、漂亮的。'),
            ('kitchen', '廚房', 'Elementary', '臥室', '客廳', '浴室', 'kitchen 是廚房，煮飯烹飪的地方。'),
            ('school', '學校', 'Elementary', '公園', '醫院', '商店', 'school 是學校，學生上課學習的場所。'),
            # Junior 國中
            ('fabulous', '極好的', 'Junior', '糟糕的', '平凡的', '危險的', 'fabulous 表示極好的、絕佳的，常用來形容棒極了的人事物。'),
            ('experience', '經驗', 'Junior', '實驗', '期待', '解釋', 'experience 名詞指經驗、體驗；動詞指經歷。'),
            ('volcano', '火山', 'Junior', '地震', '颱風', '海嘯', 'volcano 指火山，是會噴發岩漿和火山灰的山。'),
            ('influence', '影響', 'Junior', '流入', '流感', '資訊', 'influence 代表影響或影響力。'),
            ('decide', '決定', 'Junior', '拒絕', '延期', '描述', 'decide 是動詞，表示決定、下決心。'),
            # Senior 高中
            ('phenomenon', '現象', 'Senior', '幻覺', '哲學', '奇蹟', 'phenomenon 指現象，複數形為 phenomena。'),
            ('consequence', '後果', 'Senior', '序列', '巧合', '便利', 'consequence 意為（常指不好的）後果、結果。'),
            ('artificial', '人工的', 'Senior', '藝術的', '真實的', '古代的', 'artificial 代表人工的、人造的，例如 Artificial Intelligence (人工智慧)。'),
            ('simultaneous', '同時的', 'Senior', '相似的', '刺激的', '自發的', 'simultaneous 意為「同時發生的」、「同步的」。'),
            ('procrastinate', '拖延', 'Senior', '宣告', '保護', '推廣', 'procrastinate 為動詞，表示拖延、延宕。')
        ]
        cursor.executemany('''
            INSERT INTO words (word, definition, level, option1, option2, option3, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', words_data)
        print("Words table seeded successfully!")

    # 檢查 grammar_questions 表是否已有資料
    cursor.execute('SELECT COUNT(*) FROM grammar_questions')
    if cursor.fetchone()[0] == 0:
        grammar_data = [
            ('She ___ to school every day.', 'goes', 'go', 'going', 'gone', 'Present Simple', '主詞為單數第三人稱 She，在現在簡單式中動詞需用 goes。'),
            ('Water ___ at 100 degrees Celsius.', 'boils', 'boil', 'boiling', 'boiled', 'Present Simple', '描述客觀事實、科學真理時，使用現在簡單式，單數主詞 Water 搭配 boils。'),
            ('Yesterday, they ___ a movie at the theater.', 'watched', 'watch', 'watches', 'watching', 'Past Simple', '時間副詞 Yesterday 指過去時間，故動詞使用過去式 watched。'),
            ('He ___ to Japan last summer.', 'went', 'go', 'gone', 'goes', 'Past Simple', '句中有 last summer，表示過去發生的動作，go 的過去式為 went。'),
            ('Look! The birds ___ in the sky.', 'are flying', 'fly', 'is flying', 'flown', 'Present Continuous', 'Look!（看！）表示動作正發生在說話當下，主詞複數 birds 搭配 are flying。'),
            ('I ___ my homework right now.', 'am doing', 'do', 'doing', 'did', 'Present Continuous', 'right now（現在）搭配現在進行式 am/is/are + V-ing，主詞為 I 搭配 am doing。'),
            ('I ___ this movie three times already.', 'have seen', 'has seen', 'saw', 'see', 'Present Perfect', '句尾 have already/times 表示經驗，主詞 I 搭配現在完成式 have + p.p. (have seen)。'),
            ('She ___ in Taipei since 2018.', 'has lived', 'have lived', 'lives', 'lived', 'Present Perfect', '句中有 since + 過去時間點，表示動作從過去持續到現在，單數 She 搭配 has lived。'),
            ('We ___ a party next weekend.', 'will host', 'hosted', 'host', 'are hosting', 'Future Simple', '時間為 next weekend，使用未來簡單式 will + 原形動詞 (will host)。'),
            ('I promise I ___ you tomorrow.', 'will call', 'called', 'call', 'am calling', 'Future Simple', 'I promise（我承諾）後常接未來簡單式 will + 原形動詞 (will call)。'),
            ('While I ___ dinner, the phone rang.', 'was cooking', 'cooked', 'am cooking', 'were cooking', 'Past Continuous', 'while 引導的子句常表示過去某時間正在進行的動作，主詞 I 搭配 was cooking。'),
            ('By the time we arrived, the train ___.', 'had left', 'has left', 'left', 'leaves', 'Past Perfect', 'By the time + 過去式，主要子句表示「在過去某時間點前已發生的動作」，使用過去完成式 had + p.p. (had left)。'),
            ('This book ___ by J.K. Rowling in 1997.', 'was written', 'wrote', 'is written', 'has written', 'Passive Voice', '書是被寫的，且發生在 1997 年，故使用過去被動式 was/were + p.p. (was written)。'),
            ('If it rains tomorrow, we ___ the picnic.', 'will cancel', 'cancel', 'cancelled', 'would cancel', 'Conditional', '條件句表示對未來的真實假設 (If + 現在式, 主句 + 未來式)，主句動詞用 will cancel。'),
            ('If I ___ you, I would study harder.', 'were', 'am', 'was', 'be', 'Conditional', '與現在事實相反的假設語氣，if 子句動詞 be 動詞不論人稱皆使用 were。')
        ]
        cursor.executemany('''
            INSERT INTO grammar_questions (question, correct_answer, option1, option2, option3, tense, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', grammar_data)
        print("Grammar questions table seeded successfully!")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # 如果已存在舊的資料庫，我們先將其刪除以重新套用新 Schema 和 Seed 資料
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"Removed existing {DB_NAME} to apply new schema.")
        except Exception as e:
            print(f"Could not remove database file: {e}")
            
    init_db()
