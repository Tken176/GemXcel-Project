import json
import os
from config import LESSON_DATA_FILE_PATH

quiz_data = {}
try:
    with open(LESSON_DATA_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if "lessons" in data:
            # Sửa lại cách xử lý dữ liệu để phù hợp với cấu trúc thực tế
            quiz_data = {
                index + 1: [  # Sử dụng index + 1 làm ID bài học
                    {
                        "id": q_index,  # Sử dụng chỉ số câu hỏi làm id
                        "question": q["question"],
                        "choices": q["choices"],
                        "answer": q["correct_answer"],
                        "explanation": "",  # Thêm trường explanation mặc định
                        "difficulty": q.get("difficulty", "medium")  # Thêm độ khó nếu có
                    } 
                    for q_index, q in enumerate(lesson["questions"])
                    if "choices" in q  # Đảm bảo chỉ lấy câu hỏi MCQ
                ]
                for index, lesson in enumerate(data["lessons"])
            }
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file dữ liệu câu hỏi tại {LESSON_DATA_FILE_PATH}.")
    quiz_data = {}
except json.JSONDecodeError:
    print(f"Lỗi: Không thể giải mã dữ liệu từ {LESSON_DATA_FILE_PATH}.")
    quiz_data = {}
except Exception as e:
    print(f"Lỗi không xác định khi tải dữ liệu: {str(e)}")
    quiz_data = {}