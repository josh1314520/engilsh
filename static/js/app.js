// 遊戲狀態 state
let score = 0;
let streak = 0;
let heroHp = 100;
let maxHeroHp = 100;
let monsterHp = 100;
let maxMonsterHp = 100;
let level = 1;
let xp = 0;
let xpToLevelUp = 100;

let questions = [];
let currentQuestionIndex = 0;
let isAnswered = false;

// 怪物清單 (隨機生成)
const monsterList = [
    { name: "單字小惡魔", avatar: "👹", hp: 60 },
    { name: "詞彙石巨人", avatar: "🗿", hp: 80 },
    { name: "時態幽靈", avatar: "👻", hp: 70 },
    { name: "語法巨龍", avatar: "🐉", hp: 120 },
    { name: "動詞史萊姆", avatar: "🤢", hp: 50 },
    { name: "被動機甲", avatar: "🤖", hp: 100 }
];
let currentMonster = monsterList[0];

// 1. 初始化載入
document.addEventListener("DOMContentLoaded", () => {
    // 預先載入題目
    loadNewQuestionSet();
    // 監聽模式選擇切換過濾器顯示
    const filterMode = document.getElementById("filterMode");
    filterMode.addEventListener("change", toggleFilterFields);
});

// 2. 切換主要分頁 (Tabs)
function switchTab(tabId) {
    // 切換導覽按鈕 active
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
    if (tabId === 'arena') document.getElementById("tabBtnArena").classList.add("active");
    if (tabId === 'mgmt') {
        document.getElementById("tabBtnMgmt").classList.add("active");
        // 切換到管理頁時，載入列表資料
        fetchWords();
        fetchGrammar();
    }
    if (tabId === 'guide') document.getElementById("tabBtnGuide").classList.add("active");

    // 切換分頁內容顯示
    document.querySelectorAll(".tab-content").forEach(tab => tab.classList.remove("active"));
    const targetTab = document.getElementById(`tab${tabId.charAt(0).toUpperCase() + tabId.slice(1)}`);
    if (targetTab) {
        targetTab.classList.add("active");
    }
}

// 3. 切換管理頁子分頁 (Words vs Grammar)
function switchMgmtTab(subTab) {
    document.querySelectorAll(".sub-tab-btn").forEach(btn => btn.classList.remove("active"));
    if (subTab === 'words') {
        document.getElementById("subTabBtnWords").classList.add("active");
        document.getElementById("mgmtWordsSection").style.display = "block";
        document.getElementById("mgmtGrammarSection").style.display = "none";
        fetchWords();
    } else {
        document.getElementById("subTabBtnGrammar").classList.add("active");
        document.getElementById("mgmtWordsSection").style.display = "none";
        document.getElementById("mgmtGrammarSection").style.display = "block";
        fetchGrammar();
    }
}

// 4. 動態顯示與隱藏難度/時態過濾器
function toggleFilterFields() {
    const mode = document.getElementById("filterMode").value;
    const levelGroup = document.getElementById("filterLevelGroup");
    const tenseGroup = document.getElementById("filterTenseGroup");

    if (mode === "vocab") {
        levelGroup.style.display = "flex";
        tenseGroup.style.display = "none";
    } else if (mode === "grammar") {
        levelGroup.style.display = "none";
        tenseGroup.style.display = "flex";
    } else {
        // mixed
        levelGroup.style.display = "flex";
        tenseGroup.style.display = "flex";
    }
}

// 5. 隨機更換新怪物
function spawnNewMonster() {
    const randomIndex = Math.floor(Math.random() * monsterList.length);
    const template = monsterList[randomIndex];
    
    // 依關卡等級等比例增強怪物的血量
    const scaledHp = Math.round(template.hp * (1 + (level - 1) * 0.15));
    
    currentMonster = {
        name: template.name,
        avatar: template.avatar,
        maxHp: scaledHp,
        hp: scaledHp
    };

    maxMonsterHp = scaledHp;
    monsterHp = scaledHp;

    document.getElementById("monsterAvatar").innerText = currentMonster.avatar;
    document.getElementById("monsterName").innerText = `${currentMonster.name} (Lv.${level})`;
    updateHpProgress();
}

// 6. 載入題目資料集 (API)
async function loadNewQuestionSet() {
    const mode = document.getElementById("filterMode").value;
    const levelVal = document.getElementById("filterLevel").value;
    const tenseVal = document.getElementById("filterTense").value;

    const promptText = document.getElementById("questionPrompt");
    promptText.innerText = "正在召喚怪物與題庫中...";

    try {
        const url = `/api/questions?mode=${mode}&level=${levelVal}&tense=${tenseVal}&limit=12`;
        const res = await fetch(url);
        questions = await res.json();
        
        currentQuestionIndex = 0;
        isAnswered = false;
        
        if (questions.length === 0) {
            document.getElementById("questionCategory").innerText = "EMPTY";
            document.getElementById("questionPrompt").innerText = "目前題庫中沒有符合篩選條件的題目，請先到「題庫管理」新增題目喔！";
            document.getElementById("questionDetail").innerText = "⚠️ 題庫尚無資料";
            document.getElementById("optionsGrid").innerHTML = "";
            document.getElementById("feedbackPanel").style.display = "none";
        } else {
            displayQuestion(questions[currentQuestionIndex]);
        }
    } catch (e) {
        console.error("載入題庫出錯:", e);
        promptText.innerText = "載入失敗，請確認後端伺服器是否正常啟動。";
    }
}

// 7. 顯示單個題目
function displayQuestion(q) {
    isAnswered = false;
    document.getElementById("feedbackPanel").style.display = "none";

    // 顯示類別標籤與提示文字
    document.getElementById("questionCategory").innerText = q.category.toUpperCase();
    document.getElementById("questionPrompt").innerText = q.prompt;
    document.getElementById("questionDetail").innerText = q.detail;

    // 渲染選項按鈕
    const optionsGrid = document.getElementById("optionsGrid");
    optionsGrid.innerHTML = "";

    const labels = ["A", "B", "C", "D"];
    q.options.forEach((opt, idx) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.setAttribute("id", `optionBtn${labels[idx]}`);
        btn.innerHTML = `
            <span class="option-badge">${labels[idx]}</span>
            <span class="option-text">${escapeHtml(opt)}</span>
        `;
        btn.onclick = () => selectOption(opt, q.correct, q.analysis, btn);
        optionsGrid.appendChild(btn);
    });
}

// 8. 玩家選擇答案
function selectOption(selectedOpt, correctOpt, analysis, selectedBtn) {
    if (isAnswered) return;
    isAnswered = true;

    // 禁用所有按鈕
    const buttons = document.querySelectorAll(".option-btn");
    buttons.forEach(btn => btn.disabled = true);

    const isCorrect = (selectedOpt === correctOpt);
    const feedbackPanel = document.getElementById("feedbackPanel");
    const feedbackHeader = document.getElementById("feedbackHeader");
    const feedbackTitle = document.getElementById("feedbackTitle");
    const feedbackIcon = document.getElementById("feedbackIcon");
    const feedbackAnalysis = document.getElementById("feedbackAnalysis");

    // 取得戰鬥卡牌的 DOM
    const heroCard = document.getElementById("heroCard");
    const monsterCard = document.getElementById("monsterCard");

    if (isCorrect) {
        // 答對邏輯
        selectedBtn.classList.add("correct");
        
        // 戰鬥動畫：勇者攻擊，怪物受傷
        heroCard.classList.add("attack-anim");
        setTimeout(() => {
            heroCard.classList.remove("attack-anim");
            monsterCard.classList.add("hit-anim");
            
            // 怪物扣血：扣除怪物的 25%-35% 血量
            const damage = Math.round(maxMonsterHp * (0.25 + Math.random() * 0.1));
            monsterHp = Math.max(0, monsterHp - damage);
            updateHpProgress();

            setTimeout(() => {
                monsterCard.classList.remove("hit-anim");
                
                // 檢查怪物是否死亡
                if (monsterHp <= 0) {
                    playMonsterDefeated();
                }
            }, 400);
        }, 300);

        // 玩家得分與經驗值
        streak++;
        const streakBonus = Math.min(streak * 5, 25);
        const baseScore = 20;
        const earnedScore = baseScore + streakBonus;
        score += earnedScore;

        xp += 25; // 每次答對得 25 XP
        checkXpLevelUp();

        // 顯示成功反饋
        feedbackHeader.className = "feedback-header success";
        feedbackIcon.innerText = "✔️";
        feedbackTitle.innerText = `答對了！ (得分 +${earnedScore})`;
        
        // 更新連擊卡樣式
        document.getElementById("streakCard").classList.add("streak-active");
    } else {
        // 答錯邏輯
        selectedBtn.classList.add("wrong");
        
        // 顯示正確答案
        buttons.forEach(btn => {
            const textSpan = btn.querySelector(".option-text");
            if (textSpan && textSpan.innerText === correctOpt) {
                btn.classList.add("correct");
            }
        });

        // 戰鬥動畫：怪物攻擊，勇者受傷
        monsterCard.classList.add("attack-anim");
        setTimeout(() => {
            monsterCard.classList.remove("attack-anim");
            heroCard.classList.add("hit-anim");
            
            // 勇者扣血：每次扣除 20 或 25 點 HP
            const damage = 20;
            heroHp = Math.max(0, heroHp - damage);
            updateHpProgress();

            setTimeout(() => {
                heroCard.classList.remove("hit-anim");
                
                // 檢查勇者是否死亡
                if (heroHp <= 0) {
                    triggerGameOver();
                }
            }, 400);
        }, 300);

        // 重置連擊數
        streak = 0;
        document.getElementById("streakCard").classList.remove("streak-active");

        // 顯示失敗反饋
        feedbackHeader.className = "feedback-header danger";
        feedbackIcon.innerText = "❌";
        feedbackTitle.innerText = "回答錯誤！勇者受到了傷害。";
    }

    // 顯示解析內容
    feedbackAnalysis.innerHTML = `<strong>正確答案為：${escapeHtml(correctOpt)}</strong><br><br>${escapeHtml(analysis)}`;
    feedbackPanel.style.display = "block";

    // 更新面板數據
    updateUiStats();
}

// 9. 怪物死亡重獲邏輯
function playMonsterDefeated() {
    score += 100; // 擊殺怪物大獎分
    xp += 50;     // 額外 XP
    
    // 小飄字或動畫提示
    const monsterNameEl = document.getElementById("monsterName");
    const oldName = monsterNameEl.innerText;
    monsterNameEl.innerText = "☠️ 已擊敗怪物！";
    
    setTimeout(() => {
        checkXpLevelUp();
        spawnNewMonster();
    }, 1000);
}

// 10. 升級機制
function checkXpLevelUp() {
    if (xp >= xpToLevelUp) {
        level++;
        xp = xp - xpToLevelUp;
        // 每級所需 XP 略微增多
        xpToLevelUp = Math.round(100 + level * 20);
        
        // 勇者等級提升，生命值全部回復！
        heroHp = maxHeroHp;
        
        // 炫麗特效或通知
        alert(`🎉 恭喜！英文勇者等級提升到 Lv.${level}！ HP 已完全回復！`);
    }
}

// 11. 更新進度條 UI
function updateHpProgress() {
    const heroBar = document.getElementById("heroHpBar");
    const heroText = document.getElementById("heroHpText");
    const heroPercent = Math.max(0, (heroHp / maxHeroHp) * 100);
    heroBar.style.width = `${heroPercent}%`;
    heroText.innerText = `${heroHp} / ${maxHeroHp} HP`;

    const monsterBar = document.getElementById("monsterHpBar");
    const monsterText = document.getElementById("monsterHpText");
    const monsterPercent = Math.max(0, (monsterHp / maxMonsterHp) * 100);
    monsterBar.style.width = `${monsterPercent}%`;
    monsterText.innerText = `${monsterHp} / ${maxMonsterHp} HP`;
}

// 12. 更新數據面板
function updateUiStats() {
    document.getElementById("statLevel").innerText = `Lv.${level}`;
    document.getElementById("statXp").innerText = `${xp} / ${xpToLevelUp} XP`;
    document.getElementById("statStreak").innerText = `${streak} 🔥`;
    document.getElementById("statScore").innerText = score;
    updateHpProgress();
}

// 13. 前往下一題
function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        displayQuestion(questions[currentQuestionIndex]);
    } else {
        // 已答完此輪題目，重新取得新題庫
        loadNewQuestionSet();
    }
}

// 14. 遊戲結束 modal 彈窗
function triggerGameOver() {
    document.getElementById("modalLevel").innerText = `Lv.${level}`;
    document.getElementById("modalScore").innerText = score;
    document.getElementById("gameOverModal").classList.add("active");
}

// 15. 重新開始遊戲
function restartGame() {
    // 隱藏 modal
    document.getElementById("gameOverModal").classList.remove("active");
    
    // 重置狀態
    score = 0;
    streak = 0;
    heroHp = 100;
    level = 1;
    xp = 0;
    xpToLevelUp = 100;
    
    spawnNewMonster();
    updateUiStats();
    loadNewQuestionSet();
}

/* ==========================================================================
   後端 API 串接與題庫 CRUD 管理
   ========================================================================== */

// 取得單字列表
async function fetchWords() {
    try {
        const res = await fetch('/api/words');
        const words = await res.json();
        const tbody = document.getElementById("wordsTableBody");
        tbody.innerHTML = "";

        words.forEach(w => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${w.id}</td>
                <td style="font-weight:bold; color:var(--secondary-light);">${escapeHtml(w.word)}</td>
                <td>${escapeHtml(w.definition)}</td>
                <td><span class="badge ${w.level.toLowerCase()}">${w.level}</span></td>
                <td style="font-size:0.85rem; color:var(--text-muted);">
                    1. ${escapeHtml(w.option1)}<br>
                    2. ${escapeHtml(w.option2)}<br>
                    3. ${escapeHtml(w.option3)}
                </td>
                <td>
                    <button class="delete-btn" onclick="deleteWord(${w.id})">刪除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("載入單字庫出錯:", e);
    }
}

// 提交新增單字表單
async function submitWordForm(e) {
    e.preventDefault();
    const word = document.getElementById("wordInput").value.trim();
    const definition = document.getElementById("definitionInput").value.trim();
    const levelVal = document.getElementById("levelInput").value;
    const option1 = document.getElementById("opt1Input").value.trim();
    const option2 = document.getElementById("opt2Input").value.trim();
    const option3 = document.getElementById("opt3Input").value.trim();
    const analysis = document.getElementById("analysisInput").value.trim();

    try {
        const res = await fetch('/api/words', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ word, definition, level: levelVal, option1, option2, option3, analysis })
        });
        
        if (res.ok) {
            alert("單字新增成功！");
            document.getElementById("addWordForm").reset();
            fetchWords();
        } else {
            const err = await res.json();
            alert(`新增失敗: ${err.error}`);
        }
    } catch (err) {
        console.error("提交單字表單出錯:", err);
    }
}

// 刪除單字
async function deleteWord(id) {
    if (!confirm("確定要刪除此單字嗎？")) return;
    try {
        const res = await fetch(`/api/words/${id}`, { method: 'DELETE' });
        if (res.ok) {
            fetchWords();
        } else {
            alert("刪除失敗");
        }
    } catch (e) {
        console.error("刪除單字出錯:", e);
    }
}

// 取得文法題庫列表
async function fetchGrammar() {
    try {
        const res = await fetch('/api/grammar');
        const grammar = await res.json();
        const tbody = document.getElementById("grammarTableBody");
        tbody.innerHTML = "";

        grammar.forEach(g => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${g.id}</td>
                <td style="color:#fff;">${escapeHtml(g.question)}</td>
                <td style="font-weight:bold; color:var(--primary-light);">${escapeHtml(g.correct_answer)}</td>
                <td><span class="badge tense">${g.tense}</span></td>
                <td style="font-size:0.85rem; color:var(--text-muted);">
                    1. ${escapeHtml(g.option1)}<br>
                    2. ${escapeHtml(g.option2)}<br>
                    3. ${escapeHtml(g.option3)}
                </td>
                <td>
                    <button class="delete-btn" onclick="deleteGrammar(${g.id})">刪除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("載入文法題庫出錯:", e);
    }
}

// 提交新增文法表單
async function submitGrammarForm(e) {
    e.preventDefault();
    const question = document.getElementById("gQuestionInput").value.trim();
    const correct_answer = document.getElementById("gCorrectInput").value.trim();
    const tense = document.getElementById("gTenseInput").value;
    const option1 = document.getElementById("gOpt1Input").value.trim();
    const option2 = document.getElementById("gOpt2Input").value.trim();
    const option3 = document.getElementById("gOpt3Input").value.trim();
    const analysis = document.getElementById("gAnalysisInput").value.trim();

    try {
        const res = await fetch('/api/grammar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, correct_answer, option1, option2, option3, tense, analysis })
        });

        if (res.ok) {
            alert("文法題目新增成功！");
            document.getElementById("addGrammarForm").reset();
            fetchGrammar();
        } else {
            const err = await res.json();
            alert(`新增失敗: ${err.error}`);
        }
    } catch (err) {
        console.error("提交文法表單出錯:", err);
    }
}

// 刪除文法題目
async function deleteGrammar(id) {
    if (!confirm("確定要刪除此文法題目嗎？")) return;
    try {
        const res = await fetch(`/api/grammar/${id}`, { method: 'DELETE' });
        if (res.ok) {
            fetchGrammar();
        } else {
            alert("刪除失敗");
        }
    } catch (e) {
        console.error("刪除文法出錯:", e);
    }
}

// 輔助函式：逸出 HTML 字元避免 XSS
function escapeHtml(text) {
    if (typeof text !== 'string') return text;
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
