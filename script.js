let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let selectedQuestions = [];

// DOM 元素
const startScreen = document.getElementById('start-screen');
const quizScreen = document.getElementById('quiz-screen');
const resultScreen = document.getElementById('result-screen');
const startBtn = document.getElementById('start-btn');
const nextBtn = document.getElementById('next-btn');
const restartBtn = document.getElementById('restart-btn');
const questionText = document.getElementById('question-text');
const optionsContainer = document.getElementById('options');
const scoreElement = document.getElementById('score');
const currentQuestionElement = document.getElementById('current-question');
const answerFeedback = document.getElementById('answer-feedback');
const correctAnswerElement = document.getElementById('correct-answer');
const finalScoreElement = document.getElementById('final-score');

// 載入題庫
async function loadQuestions() {
    try {
        const response = await fetch('all_questions.json');
        const rawQuestions = await response.json();
        
        // 清理和格式化題目
        questions = rawQuestions.map(q => ({
            ...q,
            question: formatText(q.question),
            options: Object.fromEntries(
                Object.entries(q.options).map(([k, v]) => [k, formatText(v)])
            )
        }));
        
        // 確保所有選項都被正確清理
        questions.forEach(q => {
            Object.entries(q.options).forEach(([k, v]) => {
                if (v.includes('112年度') || v.includes('資訊安全工程師')) {
                    console.log('需要清理的選項:', q.number, k, v);
                }
            });
        });
        
        console.log('題庫載入完成，共有', questions.length, '題');
    } catch (error) {
        console.error('載入題庫失敗:', error);
        alert('載入題庫失敗，請重新整理頁面');
    }
}

// 格式化文字
function formatText(text) {
    if (!text) return '';
    return text
        .replace(/\s+/g, ' ')
        .replace(/^\s+|\s+$/g, '')
        .replace(/：/g, ':')
        .replace(/，/g, ',')
        .replace(/。/g, '.')
        .replace(/\s*\n\s*/g, '\n')
        .replace(/資\s+安/g, '資安')
        .replace(/三要素/g, '3要素')
        .replace(/\(\s*/g, '(')
        .replace(/\s*\)/g, ')')
        .replace(/\s*,\s*/g, ', ')
        .replace(/\s*:\s*/g, ': ')
        // 移除選項中的檔案名稱和多餘文字
        .replace(/\s*\d{3}年度第\d次\s*/g, '')
        .replace(/\s*資訊安全[工程師]*\s*/g, '')
        .replace(/\s*能力鑑定\s*/g, '')
        .replace(/\s*初級試題\s*/g, '');
}

// 隨機選擇 25 題
function selectRandomQuestions() {
    const shuffled = [...questions].sort(() => 0.5 - Math.random());
    selectedQuestions = shuffled.slice(0, 25);
}

// 顯示當前問題
function showQuestion() {
    const question = selectedQuestions[currentQuestionIndex];
    if (!question) {
        console.error('找不到問題:', currentQuestionIndex);
        return;
    }

    // 顯示題號和問題
    questionText.textContent = `${currentQuestionIndex + 1}. ${question.question}`;
    
    // 清空並重新建立選項
    optionsContainer.innerHTML = '';
    Object.entries(question.options).forEach(([letter, text]) => {
        const option = document.createElement('div');
        option.className = 'option';
        option.textContent = `${letter}. ${text}`;
        option.dataset.letter = letter;
        option.addEventListener('click', () => selectOption(letter));
        optionsContainer.appendChild(option);
    });
    
    // 更新進度
    currentQuestionElement.textContent = currentQuestionIndex + 1;
    answerFeedback.classList.add('hidden');
    
    // 重置選項狀態
    document.querySelectorAll('.option').forEach(option => {
        option.style.pointerEvents = 'auto';
        option.classList.remove('selected', 'correct', 'incorrect');
    });
}

// 選擇選項
function selectOption(selectedLetter) {
    const question = selectedQuestions[currentQuestionIndex];
    if (!question) return;

    const options = document.querySelectorAll('.option');
    
    // 禁用所有選項
    options.forEach(option => {
        option.style.pointerEvents = 'none';
    });
    
    // 更新選項樣式
    options.forEach(option => {
        const letter = option.dataset.letter;
        option.classList.remove('selected');
        
        if (letter === selectedLetter) {
            option.classList.add('selected');
        }
        if (letter === question.answer) {
            option.classList.add('correct');
        } else if (letter === selectedLetter && selectedLetter !== question.answer) {
            option.classList.add('incorrect');
        }
    });
    
    // 顯示答案反饋
    answerFeedback.classList.remove('hidden');
    correctAnswerElement.textContent = `${question.answer}. ${question.options[question.answer]}`;
    
    // 更新分數
    if (selectedLetter === question.answer) {
        score += 4;
        scoreElement.textContent = score;
    }
}

// 下一題
function nextQuestion() {
    currentQuestionIndex++;
    
    if (currentQuestionIndex < selectedQuestions.length) {
        showQuestion();
    } else {
        showResult();
    }
}

// 顯示結果
function showResult() {
    quizScreen.classList.add('hidden');
    resultScreen.classList.remove('hidden');
    finalScoreElement.textContent = score;
}

// 重新開始測驗
function restartQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    scoreElement.textContent = score;
    selectRandomQuestions();
    resultScreen.classList.add('hidden');
    quizScreen.classList.remove('hidden');
    showQuestion();
}

// 事件監聽器
startBtn.addEventListener('click', () => {
    startScreen.classList.add('hidden');
    quizScreen.classList.remove('hidden');
    selectRandomQuestions();
    showQuestion();
});

nextBtn.addEventListener('click', nextQuestion);
restartBtn.addEventListener('click', restartQuiz);

// 初始化
loadQuestions(); 