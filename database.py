import sqlite3
import os

DB_NAME = 'english_hero.db'

def init_db():
    # 建立或連結你個人的專屬題庫
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立動詞時態與變化題庫表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammar_quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verb_base TEXT NOT NULL,      -- 動詞原型 (例如: take)
            verb_past TEXT NOT NULL,      -- 過去式 (例如: took)
            verb_ing TEXT NOT NULL,       -- 現在分詞 (例如: taking)
            verb_vpp TEXT NOT NULL,       -- 過去分詞 (例如: taken)
            chinese_meaning TEXT NOT NULL,-- 中文意思
            tense_category TEXT NOT NULL, -- 時態大類: 現在/過去/未來
            aspect_category TEXT NOT NULL,-- 狀態大類: 簡單/進行/完成
            sentence_question TEXT NOT NULL, -- 挖空題目
            correct_answer TEXT NOT NULL, -- 正確填空答案
            wrong_option1 TEXT NOT NULL,  -- 故意干擾你的錯誤動詞變化 1
            wrong_option2 TEXT NOT NULL,  -- 故意干擾你的錯誤動詞變化 2
            wrong_option3 TEXT NOT NULL,  -- 故意干擾你的錯誤動詞變化 3
            detailed_analysis TEXT NOT NULL -- 寫錯時，你專屬的隨身文法老師詳細解析
        )
    ''')
    
    # 幫你注入 4 題涵蓋「進行式、完成式、動詞三態變化」的經典私人特訓題
    quiz_data = [
        (
            'take', 'took', 'taking', 'taken', '拿、花費時間',
            '過去', '進行',
            'Yesterday at 3 PM, I ___ (take) a very important English test.',
            'was taking', 'took', 'taking', 'had taken',
            '【💡 你的專屬文法特訓解析】\n'
            '1. 觀察時態：句中明確指出「Yesterday at 3 PM」（昨天下午三點整），這是一個【過去的特定時間點】。\n'
            '2. 狀態判斷：在過去特定時間點「正在進行」的動作，必須使用【過去進行式】（was/were + V-ing）。\n'
            '3. 動詞變化：take 的現在分詞（V-ing）要【去 e 加 ing】變成 taking。主詞為 I，Be 動詞用 was，故選 was taking。\n'
            '4. 三態複習：take (原型) -> took (過去式) -> taken (V-pp)。'
        ),
        (
            'write', 'wrote', 'writing', 'written', '寫',
            '現在', '完成',
            'Wow! You ___ (write) three English essays since this morning.',
            'have written', 'wrote', 'writing', 'has written',
            '【💡 你的專屬文法特訓解析】\n'
            '1. 觀察時態：句中出現了關鍵字「since this morning」（自從今天早上以來），表示動作從過去持續到現在，要用【現在完成式】（have/has + V-pp）。\n'
            '2. 動詞變化：write 的過去分詞（V-pp）是【不規則變化】的 written（注意是雙寫 t）。\n'
            '3. 主詞搭配：主詞是 You，助動詞必須搭配 have 而非 has，因此正確答案是 have written。'
        ),
        (
            'finish', 'finished', 'finishing', 'finished', '完成',
            '未來', '完成',
            'By the time you wake up tomorrow, I ___ (finish) all my revision.',
            'will have finished', 'will finishing', 'finished', 'have finished',
            '【💡 你的專屬文法特訓解析】\n'
            '1. 觀察時態：句首有「By the time + 明天（未來時間）」，代表「到未來某個時間點為止，某個動作將會完成」，這是經典的【未來完成式】（will have + V-pp）。\n'
            '2. 動詞變化：finish 是規則動詞，過去式與過去分詞（V-pp）皆為 finished。\n'
            '3. 答案結構：未來完成式固定結構為 will have + V-pp，故選 will have finished。'
        ),
        (
            'run', 'ran', 'running', 'run', '跑步、經營',
            '現在', '進行',
            'Look! The criminal ___ (run) away from the police right now!',
            'is running', 'ran', 'running', 'runs',
            '【💡 你的專屬文法特訓解析】\n'
            '1. 觀察時態：句首有驚嘆號「Look!」加上句尾的「right now」，表示【說話當下正在發生】的事情，要用【現在進行式】（am/is/are + V-ing）。\n'
            '2. 動詞變化：run 的現在分詞（V-ing）屬於「短母音+單子音」，必須【重複字尾再加 ing】變成 running。\n'
            '3. 答案結構：主詞 The criminal 是單數，搭配 is，故選 is running。'
        )
    ]
    
    cursor.execute("DELETE FROM grammar_quiz")
    cursor.executemany('''
        INSERT INTO grammar_quiz (
            verb_base, verb_past, verb_ing, verb_vpp, chinese_meaning,
            tense_category, aspect_category, sentence_question, correct_answer,
            wrong_option1, wrong_option2, wrong_option3, detailed_analysis
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', quiz_data)
    
    conn.commit()
    conn.close()
    print("Database grammar_quiz initialized successfully with tense patterns!")

if __name__ == '__main__':
    # 如果已存在舊的資料庫，我們先將其刪除以重新套用新 Schema 和 Seed 資料
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"Removed existing {DB_NAME} to apply new schema.")
        except Exception as e:
            print(f"Could not remove database file: {e}")
            
    init_db()
