import PyPDF2
import json
import re
import os

def fix_abbreviations(text):
    # 修正常見的縮寫問題
    replacements = {
        'L ': 'LA ',
        'HIP ': 'HIPAA ',
        'HIPA ': 'HIPAA ',
        'PCI-DSS': 'PCI DSS',
        'ISO27001': 'ISO 27001',
        'ISO 27001L': 'ISO 27001 LA',
        'ISO27018': 'ISO 27018',
        'ISO27701': 'ISO 27701',
        'ISO 27001L': 'ISO 27001 LA'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def clean_text(text):
    # 移除多餘的換行符和空格
    text = re.sub(r'\s+', ' ', text)
    # 移除答案標記
    text = re.sub(r'\s*[A-D]\s*$', '', text)
    # 移除頁碼和其他無關資訊
    text = re.sub(r'\d+年度第\s*\d+\s*次.*?(?=\d+\.|\Z)', '', text, flags=re.DOTALL)
    text = re.sub(r'第\s*\d+\s*頁.*?頁', '', text)
    # 修正縮寫
    text = fix_abbreviations(text)
    return text.strip()

def extract_options_from_text(text):
    options = []
    # 使用更寬鬆的模式來匹配選項
    option_pattern = r'\(([A-D])\)\s*(.*?)(?=\s*\([A-D]\)|$)'
    option_matches = list(re.finditer(option_pattern, text, re.DOTALL))
    
    for match in option_matches:
        letter = match.group(1)
        option_text = clean_text(match.group(2))
        if option_text:  # 只有當選項文本不為空時才添加
            options.append({
                "letter": letter,
                "text": option_text
            })
    
    return options

def extract_questions_from_pdf(pdf_path):
    questions = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        full_text = ""
        # 先將所有頁面的文字合併
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        # 使用正則表達式來識別題目
        question_pattern = r'(\d+\.\s+.*?)(?=\d+\.\s+|$)'
        matches = re.finditer(question_pattern, full_text, re.DOTALL)
        
        for match in matches:
            full_question_text = match.group(1).strip()
            
            # 提取答案（在選項之後的單個字母）
            answer_match = re.search(r'\s+([A-D])\s*$', full_question_text)
            answer = answer_match.group(1) if answer_match else ""
            
            # 提取選項
            options = extract_options_from_text(full_question_text)
            
            # 提取題目文本
            # 找到第一個選項的位置
            first_option_pos = full_question_text.find('(A)') if '(A)' in full_question_text else len(full_question_text)
            question_text = full_question_text[:first_option_pos].strip()
            
            # 清理題目文本
            question_text = clean_text(question_text)
            
            # 確保所有選項都被提取出來
            if len(options) < 4 and '(A)' in full_question_text:
                # 如果選項不完整，嘗試重新提取
                option_text = full_question_text[first_option_pos:]
                options = []
                for letter in ['A', 'B', 'C', 'D']:
                    pattern = rf'\({letter}\)\s*(.*?)(?=\s*\([A-D]\)|$)'
                    match = re.search(pattern, option_text, re.DOTALL)
                    if match:
                        option_text_clean = clean_text(match.group(1))
                        if option_text_clean:
                            options.append({
                                "letter": letter,
                                "text": option_text_clean
                            })
            
            question = {
                "question": question_text,
                "options": options,
                "answer": answer,
                "source": os.path.basename(pdf_path)
            }
            questions.append(question)
    
    return questions

def main():
    pdf_files = [
        "113-2+I11資訊安全管理概論.pdf",
        "113-1+I11資訊安全管理概論.pdf",
        "112-02+I11-資訊安全管理概論.pdf",
        "11201-I11+資訊安全管理概論.pdf"
    ]
    
    all_questions = []
    
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            print(f"正在處理 {pdf_file}...")
            questions = extract_questions_from_pdf(pdf_file)
            all_questions.extend(questions)
    
    # 將所有題目保存為JSON檔案
    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=4)
    
    print(f"總共處理了 {len(all_questions)} 道題目")

if __name__ == "__main__":
    main() 