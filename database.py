import sqlite3

def init_db():
    conn = sqlite3.connect('english_hero.db')
    cursor = conn.cursor()
    
    # 建立單字題庫表
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
