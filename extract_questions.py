import PyPDF2
import re
import os
import json
from collections import OrderedDict

def clean_text(text):
    # 移除多餘的空白和換行
    text = re.sub(r'\s+', ' ', text.strip())
    # 移除頁尾資訊
    text = re.sub(r'第 \d+ 頁.*$', '', text)
    text = re.sub(r'\d+/\d+', '', text)
    # 移除題號前的答案標記
    text = re.sub(r'^[A-D] (?=\d+\.)', '', text)
    # 統一標點符號格式
    text = text.replace('：', ':').replace('，', ',').replace('。', '.')
    # 修正特定詞彙格式
    text = re.sub(r'資\s+安', '資安', text)
    text = re.sub(r'三要素', '3要素', text)
    return text.strip()

def extract_questions_from_pdf(pdf_path):
    questions = []
    current_question = None
    current_text = ""
    answer_dict = {}
    
    # 從檔名提取年份和考試編號
    filename = os.path.basename(pdf_path)
    year_match = re.search(r'(\d{3})-?(\d)?', filename)
    year = year_match.group(1) if year_match else ""
    exam = year_match.group(2) if year_match and year_match.group(2) else ""
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # 先合併所有頁面的文字
            for page in reader.pages:
                page_text = page.extract_text()
                current_text += page_text + "\n"
            
            # 先找出所有答案
            for line in current_text.split('\n'):
                answer_match = re.match(r'^([A-D])\s+(\d+)\.', line)
                if answer_match:
                    answer_dict[int(answer_match.group(2))] = answer_match.group(1)
            
            # 分割成行並處理
            lines = current_text.split('\n')
            for i, line in enumerate(lines):
                line = clean_text(line)
                if not line:
                    continue
                
                # 匹配問題編號
                question_match = re.match(r'^(\d+)\.\s*(.+)', line)
                if question_match:
                    if current_question and current_question['question'] and len(current_question['options']) >= 4:
                        questions.append(current_question)
                    
                    number = int(question_match.group(1))
                    question_text = clean_text(question_match.group(2))
                    
                    # 檢查下一行是否為問題的延續
                    if i + 1 < len(lines) and not re.match(r'^\(?[A-D]\)?|^\d+\.', lines[i + 1].strip()):
                        next_line = clean_text(lines[i + 1])
                        if next_line:
                            question_text += " " + next_line
                    
                    current_question = {
                        'number': number,
                        'question': question_text,
                        'options': OrderedDict(),
                        'answer': answer_dict.get(number, ''),
                        'year': year,
                        'exam': exam
                    }
                    continue
                
                # 匹配選項
                option_match = re.match(r'^\(?([A-D])\)?\s*(.+)', line)
                if option_match and current_question:
                    option_letter = option_match.group(1)
                    option_text = clean_text(option_match.group(2))
                    
                    # 檢查下一行是否為選項的延續
                    if i + 1 < len(lines) and not re.match(r'^\(?[A-D]\)?|^\d+\.', lines[i + 1].strip()):
                        next_line = clean_text(lines[i + 1])
                        if next_line:
                            option_text += " " + next_line
                    
                    current_question['options'][option_letter] = option_text
            
            # 添加最後一題
            if current_question and current_question['question'] and len(current_question['options']) >= 4:
                questions.append(current_question)
    
    except Exception as e:
        print(f"處理 PDF 檔案時發生錯誤 {pdf_path}: {str(e)}")
        return []
    
    # 排序選項並驗證問題完整性
    valid_questions = []
    for q in questions:
        if q['question'] and len(q['options']) >= 4:
            q['options'] = OrderedDict(sorted(q['options'].items()))
            valid_questions.append(q)
    
    print(f"從 {pdf_path} 成功提取了 {len(valid_questions)} 個有效問題")
    return valid_questions

def main():
    all_questions = []
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and ('I11' in f or '資訊安全管理概論' in f)]
    
    for pdf_file in pdf_files:
        questions = extract_questions_from_pdf(pdf_file)
        output_file = f"{os.path.splitext(pdf_file)[0]}_questions.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        all_questions.extend(questions)
    
    # 根據年份、考試編號和問題編號排序
    all_questions.sort(key=lambda x: (x['year'], x['exam'], x['number']))
    
    with open('all_questions.json', 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    
    print(f"\n總共提取了 {len(all_questions)} 個問題並儲存到 all_questions.json")

if __name__ == '__main__':
    main() 