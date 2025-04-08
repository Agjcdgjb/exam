from flask import Flask, render_template, request, jsonify, session, send_from_directory
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 請在實際部署時更改這個密鑰

# 讀取題目
with open('questions.json', 'r', encoding='utf-8') as f:
    all_questions = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions.json')
def get_questions():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'questions.json')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    # 隨機選擇25題
    selected_questions = random.sample(all_questions, 25)
    session['questions'] = selected_questions
    session['current_question'] = 0
    session['score'] = 0
    session['answers'] = []
    return jsonify({'success': True})

@app.route('/get_question')
def get_question():
    current = session.get('current_question', 0)
    questions = session.get('questions', [])
    
    if current >= len(questions):
        return jsonify({'finished': True})
    
    question = questions[current]
    return jsonify({
        'question': question['question'],
        'options': question['options'],
        'current': current + 1,
        'total': len(questions)
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    user_answer = data.get('answer')
    current = session.get('current_question', 0)
    questions = session.get('questions', [])
    
    if current >= len(questions):
        return jsonify({'finished': True})
    
    correct_answer = questions[current]['answer']
    is_correct = user_answer == correct_answer
    
    if is_correct:
        session['score'] = session.get('score', 0) + 4
    
    session['answers'].append({
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct
    })
    
    session['current_question'] = current + 1
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'score': session['score']
    })

@app.route('/get_result')
def get_result():
    score = session.get('score', 0)
    total_questions = len(session.get('questions', []))
    passed = score >= 60
    return jsonify({
        'score': score,
        'total_questions': total_questions,
        'passed': passed
    })

if __name__ == '__main__':
    app.run(debug=True) 