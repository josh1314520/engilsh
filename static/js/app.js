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

let currentQuestion = null;
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
    // 預先載入第一題
    loadNewQuestion();
});

// 2. 隨機更換新怪物
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

// 3. 載入單個題目 (API 1)
async function loadNewQuestion() {
    const levelVal = document.getElementById("filterLevel").value;
    const promptText = document.getElementById("questionPrompt");
    promptText.innerText = "正在召喚怪物與題庫中...";

    try {
        const url = `/api/get_question?level=${levelVal}`;
        const res = await fetch(url);
        
        if (res.status === 404) {
            document.getElementById("questionCategory").innerText = "EMPTY";
            document.getElementById("questionPrompt").innerText = "目前此難度沒有單字資料。";
            document.getElementById("questionDetail").innerText = "⚠️ 題庫無資料";
            document.getElementById("optionsGrid").innerHTML = "";
            document.getElementById("feedbackPanel").style.display = "none";
            return;
        }

        currentQuestion = await res.json();
        isAnswered = false;
        
        displayQuestion(currentQuestion);
    } catch (e) {
        console.error("載入題庫出錯:", e);
        promptText.innerText = "載入失敗，請確認後端伺服器是否正常啟動。";
    }
}

// 4. 顯示題目
function displayQuestion(q) {
    isAnswered = false;
    document.getElementById("feedbackPanel").style.display = "none";

    // 顯示類別標籤與提示文字
    const levelVal = document.getElementById("filterLevel").value;
    document.getElementById("questionCategory").innerText = levelVal.toUpperCase();
    document.getElementById("questionPrompt").innerText = `請選出英文單字 [ ${q.word} ] 的正確中文意思：`;
    document.getElementById("questionDetail").innerText = q.word;

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
        btn.onclick = () => selectOption(opt, q.id, btn);
        optionsGrid.appendChild(btn);
    });
}

// 5. 玩家選擇答案並驗證 (API 2)
async function selectOption(selectedOpt, wordId, selectedBtn) {
    if (isAnswered) return;
    isAnswered = true;

    // 禁用所有按鈕
    const buttons = document.querySelectorAll(".option-btn");
    buttons.forEach(btn => btn.disabled = true);

    try {
        // 呼叫 API 2 驗證答案
        const checkRes = await fetch('/api/check_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: wordId,
                answer: selectedOpt
            })
        });

        const result = await checkRes.json();
        
        const isCorrect = result.correct;
        const correctOpt = result.correct_answer;
        const analysis = result.analysis;

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
                
                // 勇者扣血：每次扣除 20 點 HP
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
        
    } catch (e) {
        console.error("答案檢查出錯:", e);
    }
}

// 6. 怪物死亡重獲邏輯
function playMonsterDefeated() {
    score += 100; // 擊殺怪物大獎分
    xp += 50;     // 額外 XP
    
    const monsterNameEl = document.getElementById("monsterName");
    monsterNameEl.innerText = "☠️ 已擊敗怪物！";
    
    setTimeout(() => {
        checkXpLevelUp();
        spawnNewMonster();
    }, 1000);
}

// 7. 升級機制
function checkXpLevelUp() {
    if (xp >= xpToLevelUp) {
        level++;
        xp = xp - xpToLevelUp;
        xpToLevelUp = Math.round(100 + level * 20);
        
        // 勇者等級提升，生命值全部回復！
        heroHp = maxHeroHp;
        
        alert(`🎉 恭喜！英文勇者等級提升到 Lv.${level}！ HP 已完全回復！`);
    }
}

// 8. 更新進度條 UI
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

// 9. 更新數據面板
function updateUiStats() {
    document.getElementById("statLevel").innerText = `Lv.${level}`;
    document.getElementById("statXp").innerText = `${xp} / ${xpToLevelUp} XP`;
    document.getElementById("statStreak").innerText = `${streak} 🔥`;
    document.getElementById("statScore").innerText = score;
    updateHpProgress();
}

// 10. 遊戲結束 modal 彈窗
function triggerGameOver() {
    document.getElementById("modalLevel").innerText = `Lv.${level}`;
    document.getElementById("modalScore").innerText = score;
    document.getElementById("gameOverModal").classList.add("active");
}

// 11. 重新開始遊戲
function restartGame() {
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
    loadNewQuestion();
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
