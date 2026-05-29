import sqlite3
import os

DB_NAME = 'english_hero.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 建立動詞時態與變化題庫表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammar_quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verb_base TEXT NOT NULL,      -- 動詞原型
            verb_past TEXT NOT NULL,      -- 過去式
            verb_ing TEXT NOT NULL,       -- 現在分詞
            verb_vpp TEXT NOT NULL,       -- 過去分詞
            chinese_meaning TEXT NOT NULL,-- 中文意思
            tense_category TEXT NOT NULL, -- 時態大類: 現在/過去/未來
            aspect_category TEXT NOT NULL,-- 狀態大類: 簡單/進行/完成
            sentence_question TEXT NOT NULL, -- 挖空題目
            correct_answer TEXT NOT NULL, -- 正確填空答案
            wrong_option1 TEXT NOT NULL,  -- 錯誤動詞變化 1
            wrong_option2 TEXT NOT NULL,  -- 錯誤動詞變化 2
            wrong_option3 TEXT NOT NULL,  -- 錯誤動詞變化 3
            detailed_analysis TEXT NOT NULL -- 詳細解析
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # 執行題庫自動生成植入
    seed_data()

def seed_data():
    # 112 個常用動詞及其變化與中文意思
    verbs = [
        ('take', 'took', 'taking', 'taken', '拿、花費時間'),
        ('write', 'wrote', 'writing', 'written', '寫'),
        ('finish', 'finished', 'finishing', 'finished', '完成'),
        ('run', 'ran', 'running', 'run', '跑步、經營'),
        ('eat', 'ate', 'eating', 'eaten', '吃'),
        ('drink', 'drank', 'drinking', 'drunk', '喝'),
        ('speak', 'spoke', 'speaking', 'spoken', '說、說話'),
        ('break', 'broke', 'breaking', 'broken', '打破、折斷'),
        ('choose', 'chose', 'choosing', 'chosen', '選擇'),
        ('do', 'did', 'doing', 'done', '做'),
        ('drive', 'drove', 'driving', 'driven', '駕駛、開車'),
        ('forget', 'forgot', 'forgetting', 'forgotten', '忘記'),
        ('give', 'gave', 'giving', 'given', '給、給予'),
        ('go', 'went', 'going', 'gone', '去、前往'),
        ('know', 'knew', 'knowing', 'known', '知道、認識'),
        ('ride', 'rode', 'riding', 'ridden', '騎、乘'),
        ('see', 'saw', 'seeing', 'seen', '看見、明白'),
        ('sing', 'sang', 'singing', 'sung', '唱歌'),
        ('steal', 'stole', 'stealing', 'stolen', '偷竊'),
        ('swim', 'swam', 'swimming', 'swum', '游泳'),
        ('wear', 'wore', 'wearing', 'worn', '穿著、戴著'),
        ('begin', 'began', 'beginning', 'begun', '開始'),
        ('fly', 'flew', 'flying', 'flown', '飛、飛行'),
        ('grow', 'grew', 'growing', 'grown', '成長、種植'),
        ('throw', 'threw', 'throwing', 'thrown', '丟、投擲'),
        ('draw', 'drew', 'drawing', 'drawn', '畫、繪製'),
        ('hide', 'hid', 'hiding', 'hidden', '躲藏、隱藏'),
        ('bite', 'bit', 'biting', 'bitten', '咬'),
        ('blow', 'blew', 'blowing', 'blown', '吹、吹氣'),
        ('shake', 'shook', 'shaking', 'shaken', '搖晃、握手'),
        ('wake', 'woke', 'waking', 'woken', '喚醒、醒來'),
        ('rise', 'rose', 'rising', 'risen', '上升、升起'),
        ('beat', 'beat', 'beating', 'beaten', '擊打、打敗'),
        ('show', 'showed', 'showing', 'shown', '展示、顯示'),
        ('fall', 'fell', 'falling', 'fallen', '落下、跌倒'),
        ('forgive', 'forgave', 'forgiving', 'forgiven', '原諒'),
        ('freeze', 'froze', 'freezing', 'frozen', '結冰、冷凍'),
        ('study', 'studied', 'studying', 'studied', '學習'),
        ('read', 'read', 'reading', 'read', '閱讀'),
        ('learn', 'learned', 'learning', 'learned', '學習'),
        ('make', 'made', 'making', 'made', '製作、製造'),
        ('build', 'built', 'building', 'built', '建造'),
        ('buy', 'bought', 'buying', 'bought', '購買'),
        ('sell', 'sold', 'selling', 'sold', '販賣'),
        ('bring', 'brought', 'bringing', 'brought', '帶來'),
        ('catch', 'caught', 'catching', 'caught', '接住、捕捉'),
        ('teach', 'taught', 'teaching', 'taught', '教、教學'),
        ('think', 'thought', 'thinking', 'thought', '思考、想'),
        ('find', 'found', 'finding', 'found', '尋找、發現'),
        ('lose', 'lost', 'losing', 'lost', '失去、輸掉'),
        ('keep', 'kept', 'keeping', 'kept', '保持、維持'),
        ('sleep', 'slept', 'sleeping', 'slept', '睡記、睡覺'),
        ('leave', 'left', 'leaving', 'left', '離開、留下'),
        ('meet', 'met', 'meeting', 'met', '遇見、見面'),
        ('send', 'sent', 'sending', 'sent', '發送、寄送'),
        ('spend', 'spent', 'spending', 'spent', '花費時間/金錢'),
        ('tell', 'told', 'telling', 'told', '告訴、講述'),
        ('say', 'said', 'saying', 'said', '說'),
        ('hear', 'heard', 'hearing', 'heard', '聽見'),
        ('pay', 'paid', 'paying', 'paid', '付款、支付'),
        ('win', 'won', 'winning', 'won', '贏得、獲勝'),
        ('understand', 'understood', 'understanding', 'understood', '理解、明白'),
        ('feel', 'felt', 'feeling', 'felt', '感覺、覺得'),
        ('hold', 'held', 'holding', 'held', '拿著、舉辦'),
        ('stand', 'stood', 'standing', 'stood', '站立'),
        ('cut', 'cut', 'cutting', 'cut', '剪、切'),
        ('put', 'put', 'putting', 'put', '放置'),
        ('hurt', 'hurt', 'hurting', 'hurt', '受傷、傷害'),
        ('cost', 'cost', 'costing', 'cost', '花費價值'),
        ('shut', 'shut', 'shutting', 'shut', '關閉'),
        ('let', 'let', 'letting', 'let', '讓、允許'),
        ('hit', 'hit', 'hitting', 'hit', '打擊、碰撞'),
        ('play', 'played', 'playing', 'played', '玩耍、彈奏'),
        ('work', 'worked', 'working', 'worked', '工作'),
        ('live', 'lived', 'living', 'lived', '居住、生活'),
        ('love', 'loved', 'loving', 'loved', '喜愛、愛'),
        ('like', 'liked', 'liking', 'liked', '喜歡'),
        ('help', 'helped', 'helping', 'helped', '幫助'),
        ('open', 'opened', 'opening', 'opened', '打開'),
        ('close', 'closed', 'closing', 'closed', '關閉'),
        ('watch', 'watched', 'watching', 'watched', '觀看、注視'),
        ('listen', 'listened', 'listening', 'listened', '聆聽'),
        ('talk', 'talked', 'talking', 'talked', '談話、聊天'),
        ('walk', 'walked', 'walking', 'walked', '散步、行走'),
        ('stop', 'stopped', 'stopping', 'stopped', '停止'),
        ('hope', 'hoped', 'hoping', 'hoped', '希望'),
        ('wish', 'wished', 'wishing', 'wished', '祝福、希望'),
        ('call', 'called', 'calling', 'called', '打電話、呼喊'),
        ('ask', 'asked', 'asking', 'asked', '詢問、要求'),
        ('answer', 'answered', 'answering', 'answered', '回答'),
        ('clean', 'cleaned', 'cleaning', 'cleaned', '清潔、打掃'),
        ('cook', 'cooked', 'cooking', 'cooked', '烹飪、煮飯'),
        ('wash', 'washed', 'washing', 'washed', '洗滌、清洗'),
        ('brush', 'brushed', 'brushing', 'brushed', '刷、刷洗'),
        ('paint', 'painted', 'painting', 'painted', '繪畫、油漆'),
        ('visit', 'visited', 'visiting', 'visited', '拜訪、參觀'),
        ('travel', 'traveled', 'traveling', 'traveled', '旅行'),
        ('enjoy', 'enjoyed', 'enjoying', 'enjoyed', '享受、喜愛'),
        ('happen', 'happened', 'happening', 'happened', '發生'),
        ('arrive', 'arrived', 'arriving', 'arrived', '抵達、到達'),
        ('decide', 'decided', 'deciding', 'decided', '決定'),
        ('explain', 'explained', 'explaining', 'explained', '解釋、說明'),
        ('remember', 'remembered', 'remembering', 'remembered', '記得、記住'),
        ('borrow', 'borrowed', 'borrowing', 'borrowed', '借入'),
        ('lend', 'lent', 'lending', 'lent', '借出'),
        ('worry', 'worried', 'worrying', 'worried', '擔心、憂慮'),
        ('agree', 'agreed', 'agreeing', 'agreed', '同意'),
        ('believe', 'believed', 'believing', 'believed', '相信'),
        ('prepare', 'prepared', 'preparing', 'prepared', '準備'),
        ('expect', 'expected', 'expecting', 'expected', '期待、預期'),
        ('receive', 'received', 'receiving', 'received', '接收、收到'),
        ('accept', 'accepted', 'accepting', 'accepted', '接受'),
        ('refuse', 'refused', 'refusing', 'refused', '拒絕'),
        ('avoid', 'avoided', 'avoiding', 'avoided', '避免'),
        ('prefer', 'preferred', 'preferring', 'preferred', '偏好、更喜歡'),
        ('describe', 'described', 'describing', 'described', '描述、形容'),
        ('imagine', 'imagined', 'imagining', 'imagined', '想像'),
        ('protect', 'protected', 'protecting', 'protected', '保護'),
        ('improve', 'improved', 'improving', 'improved', '改善、增進'),
        ('increase', 'increased', 'increasing', 'increased', '增加'),
        ('decrease', 'decreased', 'decreasing', 'decreased', '減少'),
        ('develop', 'developed', 'developing', 'developed', '發展、開發'),
        ('discover', 'discovered', 'discovering', 'discovered', '發現、探索'),
        ('create', 'created', 'creating', 'created', '創造、創建'),
        ('invent', 'invented', 'inventing', 'invented', '發明'),
        ('solve', 'solved', 'solving', 'solved', '解決'),
        ('promise', 'promised', 'promising', 'promised', '承諾、答應'),
        ('suggest', 'suggested', 'suggesting', 'suggested', '建議'),
        ('require', 'required', 'requiring', 'required', '要求、需要'),
        ('achieve', 'achieved', 'achieving', 'achieved', '達成、取得'),
        ('design', 'designed', 'designing', 'designed', '設計'),
        ('follow', 'followed', 'following', 'followed', '跟隨、遵守'),
        ('support', 'supported', 'supporting', 'supported', '支持、扶助'),
        ('carry', 'carried', 'carrying', 'carried', '攜帶、運送'),
        ('destroy', 'destroyed', 'destroying', 'destroyed', '破壞、毀滅'),
        ('repair', 'repaired', 'repairing', 'repaired', '修理、修復'),
        ('share', 'shared', 'sharing', 'shared', '分享'),
        ('introduce', 'introduced', 'introducing', 'introduced', '介紹'),
        ('compare', 'compared', 'comparing', 'compared', '比較'),
        ('invite', 'invited', 'inviting', 'invited', '邀請'),
        ('experience', 'experienced', 'experiencing', 'experienced', '體驗、經歷'),
        ('complete', 'completed', 'completing', 'completed', '完成'),
        ('organize', 'organized', 'organizing', 'organized', '組織、籌辦'),
        ('encourage', 'encouraged', 'encouraging', 'encouraged', '鼓勵'),
        ('provide', 'provided', 'providing', 'provided', '提供')
    ]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grammar_quiz")

    quiz_data = []

    # 針對每一個動詞產生 9 種不同時態與狀態組合，共 112 * 9 = 1008 題
    for v in verbs:
        v_base, v_past, v_ing, v_vpp, chinese = v
        
        # 1. 現在簡單式
        q1 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '現在', '簡單',
            f"Often, they ___ ({v_base}) at this place.",
            v_base, v_past, v_ing, f"has {v_vpp}",
            f"【現在簡單式解析】\n1. 時態：描述常規或習慣使用現在簡單式。\n2. 動詞變化：主詞為複數複人稱 they，動詞應使用原型 {v_base}。\n3. 三態複習：{v_base} (原型) -> {v_past} (過去式) -> {v_vpp} (過去分詞)。"
        )
        
        # 2. 現在進行式
        q2 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '現在', '進行',
            f"Look! The student ___ ({v_base}) right now.",
            f"is {v_ing}", f"was {v_ing}", v_base, v_past,
            f"【現在進行式解析】\n1. 時態：句中提示 Look! / right now 代表「說話當下正在發生」的動作，要用現在進行式 (am/is/are + V-ing)。\n2. 動詞變化：主詞為單數 student，搭配 Be 動詞 is 加上 V-ing ({v_ing})，答案為 is {v_ing}。"
        )
        
        # 3. 現在完成式
        q3 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '現在', '完成',
            f"I ___ ({v_base}) already since this morning.",
            f"have {v_vpp}", f"has {v_vpp}", v_past, v_ing,
            f"【現在完成式解析】\n1. 時態：由 since（自從...以來）引導時間副詞，表示動作從過去持續到現在，使用現在完成式 (have/has + V-pp)。\n2. 動詞變化：第一人稱主詞 I 搭配 have 加上過去分詞 {v_vpp}，答案為 have {v_vpp}。"
        )

        # 4. 過去簡單式
        q4 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '過去', '簡單',
            f"Yesterday, she ___ ({v_base}) this task.",
            v_past, v_base, v_ing, f"is {v_ing}",
            f"【過去簡單式解析】\n1. 時態：句中有過去時間副詞 Yesterday，表示過去已經發生的事件，使用過去簡單式。\n2. 動詞變化：動詞改用過去式形式，答案為 {v_past}。"
        )

        # 5. 過去進行式
        q5 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '過去', '進行',
            f"At 9 PM last night, we ___ ({v_base}) together.",
            f"were {v_ing}", f"was {v_ing}", v_base, f"have {v_vpp}",
            f"【過去進行式解析】\n1. 時態：描述過去特定時間點（At 9 PM last night）正在進行的動作，使用過去進行式 (was/were + V-ing)。\n2. 動詞變化：主詞為複數 we，Be 動詞過去式使用 were，加上 V-ing ({v_ing})，答案為 were {v_ing}。"
        )

        # 6. 過去完成式
        q6 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '過去', '完成',
            f"By the time he left, we ___ ({v_base}) it.",
            f"had {v_vpp}", f"have {v_vpp}", f"has {v_vpp}", v_past,
            f"【過去完成式解析】\n1. 時態：By the time 引導過去時間點子句，代表主要子句是「在此過去時間點前已完成的事」，使用過去完成式 (had + V-pp)。\n2. 動詞變化：結構為 had + V-pp，答案為 had {v_vpp}。"
        )

        # 7. 未來簡單式
        q7 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '未來', '簡單',
            f"Tomorrow, they ___ ({v_base}) to the city.",
            f"will {v_base}", f"would {v_base}", v_past, v_ing,
            f"【未來簡單式解析】\n1. 時態：出現未來時間副詞 Tomorrow，表示即將發生的未來計畫，使用未來簡單式。\n2. 動詞變化：助動詞 will 後方接原型動詞，答案為 will {v_base}。"
        )

        # 8. 未來進行式
        q8 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '未來', '進行',
            f"This time tomorrow, she ___ ({v_base}) in her office.",
            f"will be {v_ing}", f"will {v_base}", f"is {v_ing}", f"was {v_ing}",
            f"【未來進行式解析】\n1. 時態：描述未來特定時間點（This time tomorrow）正在進行的動作，使用未來進行式 (will be + V-ing)。\n2. 動詞變化：結構為 will be + V-ing，答案為 will be {v_ing}。"
        )

        # 9. 未來完成式
        q9 = (
            v_base, v_past, v_ing, v_vpp, chinese,
            '未來', '完成',
            f"By next year, Ken ___ ({v_base}) his goals.",
            f"will have {v_vpp}", f"will have {v_base}", f"has {v_vpp}", v_past,
            f"【未來完成式解析】\n1. 時態：由 By + 未來時間點引導，代表到此未來時間點為止動作將會完成，使用未來完成式 (will have + V-pp)。\n2. 動詞變化：結構為 will have + V-pp，答案為 will have {v_vpp}。"
        )

        quiz_data.extend([q1, q2, q3, q4, q5, q6, q7, q8, q9])

    cursor.executemany('''
        INSERT INTO grammar_quiz (
            verb_base, verb_past, verb_ing, verb_vpp, chinese_meaning,
            tense_category, aspect_category, sentence_question, correct_answer,
            wrong_option1, wrong_option2, wrong_option3, detailed_analysis
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', quiz_data)

    conn.commit()
    conn.close()
    print(f"Database grammar_quiz generated successfully with {len(quiz_data)} questions!")

if __name__ == '__main__':
    # 如果已存在舊的資料庫，我們先將其刪除以重新套用新 Schema 和 Seed 資料
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"Removed existing {DB_NAME} to apply new schema.")
        except Exception as e:
            print(f"Could not remove database file: {e}")
            
    init_db()
