import sqlite3
import os

DB_NAME = 'english_hero.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立升級版單字與文法題庫表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,         -- 動詞原型 (例如: eat)
            definition TEXT NOT NULL,   -- 中文意思
            level TEXT NOT NULL,        -- 難度 (Elementary/Junior/Senior)
            option1 TEXT NOT NULL,      -- 錯誤選項 1
            option2 TEXT NOT NULL,      -- 錯誤選項 2
            option3 TEXT NOT NULL,      -- 錯誤選項 3
            verb_ing TEXT,              -- 現在分詞 (例如: eating)
            verb_vpp TEXT,              -- 過去分詞 (例如: eaten)
            grammar_type TEXT,          -- 測試的文法時態類型 (例如: 現在完成式)
            sentence_q TEXT,            -- 文法挖空題目 (例如: I have already ___ dinner.)
            analysis TEXT NOT NULL      -- 寫錯時的超級詳細解析（含時態與變化說明）
        )
    ''')
    
    # 塞入帶有文法與時態變化的核心體驗單字
    sample_data = [
        (
            'eat', '吃', 'Elementary', '喝', '玩', '跑',
            'eating', 'eaten', '現在完成式',
            'I have already ___ (eat) my dinner, so I am full now.',
            '【文法大解析】\n'
            '1. 時態：本題為「現在完成式」（Have/Has + V-pp），用來表示過去已經完成且對現在造成影響的動作。\n'
            '2. 動詞變化：動詞原型 eat，現在分詞為 eating，過去分詞（V-pp）為 eaten。\n'
            '3. 答案解析：因為句中有 have 與 already，空格處必須填入過去分詞，故答案為 eaten。'
        ),
        (
            'write', '寫', 'Junior', '讀', '聽', '說',
            'writing', 'written', '過去進行式',
            'Yesterday at 8 PM, Mary ___ (write) a letter to her friend.',
            '【文法大解析】\n'
            '1. 時態：本題為「過去進行式」（Was/Were + V-ing），用來表示在過去某個特定時間點（Yesterday at 8 PM）正在發生的動作。\n'
            '2. 動詞變化：動詞原型 write，現在分詞（V-ing）去 e 加 ing 變成 writing，過去分詞為 written。\n'
            '3. 答案解析：主詞 Mary 為單數，搭配過去式 Be 動詞 was，加上 V-ing，故答案為 was writing。'
        ),
        (
            'achieve', '達成', 'Senior', '放棄', '破壞', '避開',
            'achieving', 'achieved', '未來完成式',
            'By the end of this year, Ken ___ (achieve) his learning goals.',
            '【文法大解析】\n'
            '1. 時態：本題為「未來完成式」（Will have + V-pp），用來表示在未來某個時間點之前（By the end of this year）將會完成的動作。\n'
            '2. 動詞變化：動詞原型 achieve，現在分詞（V-ing）去 e 加 ing 變成 achieving，過去分詞為 achieved。\n'
            '3. 答案解析：由 By + 未來時間引導，後方須接未來完成式，故答案為 will have achieved。'
        )
    ]
    
    cursor.execute("DELETE FROM words")
    cursor.executemany('''
        INSERT INTO words (word, definition, level, option1, option2, option3, verb_ing, verb_vpp, grammar_type, sentence_q, analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    print("Database english_hero.db initialized successfully with grammar and verb patterns!")

if __name__ == '__main__':
    # 如果已存在舊的資料庫，我們先將其刪除以重新套用新 Schema 和 Seed 資料
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"Removed existing {DB_NAME} to apply new schema.")
        except Exception as e:
            print(f"Could not remove database file: {e}")

    init_db()
