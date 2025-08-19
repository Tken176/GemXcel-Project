import os
import json
import re
import time
import hashlib
import signal
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Thư viện AI (giữ nguyên theo dự án của bạn)
from g4f.client import Client
from g4f.models import gpt_4o_mini

import config


class TimeoutException(Exception):
    """Custom timeout exception"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutException("Operation timed out")


class ContentProcessor:
    def __init__(self, lessons_count: int = 5, questions_per_lesson: int = 6, quiz_questions: int = 10):
        """
        Khởi tạo ContentProcessor với cấu hình linh hoạt

        Args:
            lessons_count: Số lượng bài học (mặc định 5, có thể tăng lên 20)
            questions_per_lesson: Số câu hỏi mỗi bài (mặc định 6, có thể tăng lên 15)
            quiz_questions: Số câu hỏi quiz tổng hợp (mặc định 10, có thể tăng lên 50)
        """
        self.client = Client()
        self.lessons_path = config.LESSON_DATA_FILE_PATH
        self.quiz_path = config.QUIZ_DATA_FILE_PATH

        self.supported_formats = ['.txt', '.docx', '.md', '.pdf']
        self.max_retries = 3
        self.timeout = 45  # Giảm timeout xuống 45s cho mỗi request
        self.total_timeout = 300  # Timeout tổng cho toàn bộ quá trình: 5 phút

        # Cấu hình linh hoạt
        self.lessons_count = max(1, min(lessons_count, 20))
        self.questions_per_lesson = max(3, min(questions_per_lesson, 15))
        self.quiz_questions = max(5, min(quiz_questions, 50))

        # Cache đơn giản
        self.content_cache = {}

        # Đảm bảo thư mục tồn tại
        os.makedirs(config.ASSETS_DIR, exist_ok=True)

        # Flags for graceful shutdown
        self.should_stop = False

    # =========================
    # Helpers
    # =========================

    def is_supported(self, file_path: str) -> bool:
        """Kiểm tra xem file có được hỗ trợ không"""
        return any(file_path.lower().endswith(ext) for ext in self.supported_formats)

    def process_file(self, file_path: str) -> Tuple[bool, str]:
        """Xử lý file chính với timeout và error handling toàn diện"""
        start_time = time.time()
        
        # Set up timeout cho toàn bộ quá trình
        if hasattr(signal, 'SIGALRM'):  # Unix systems
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.total_timeout)

        try:
            # Kiểm tra định dạng file
            if not self.is_supported(file_path):
                return False, f"Định dạng file không được hỗ trợ. Các định dạng hỗ trợ: {', '.join(self.supported_formats)}"

            # Kiểm tra file tồn tại
            if not os.path.exists(file_path):
                return False, f"File không tồn tại: {file_path}"

            # Đọc và validate file
            content = self.read_file_content(file_path)
            if not content:
                return False, "Không thể đọc nội dung từ file."

            if len(content.strip()) < 200:
                return False, "Nội dung file quá ngắn để xử lý (cần ít nhất 200 ký tự)."

            # Tiền xử lý nội dung
            content = self._preprocess_content(content)

            # Kiểm tra cache
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            if content_hash in self.content_cache:
                lessons, quiz_questions = self.content_cache[content_hash]
            else:
                # Chia nội dung thành các phần
                chunks = self._intelligent_chunking(content, target_chunks=self.lessons_count)

                # Tạo bài học với timeout
                lessons = self.generate_lessons_with_timeout(chunks)
                
                if not lessons:
                    return False, "Không thể tạo bài học từ nội dung này."

                # Lọc None và validate
                lessons = [lesson for lesson in lessons if lesson is not None]
                if not lessons:
                    return False, "Không thể tạo bài học hợp lệ từ nội dung này."

                # Tạo quiz với timeout
                quiz_questions = self.generate_quiz_with_timeout(lessons, total_questions=self.quiz_questions)

                # Cache kết quả
                self.content_cache[content_hash] = (lessons, quiz_questions)

            # Lưu file với error handling
            success = self._safe_save_data_files(lessons, quiz_questions)
            if not success:
                return False, "Không thể lưu dữ liệu. Vui lòng kiểm tra quyền ghi file."

            elapsed_time = time.time() - start_time
            total_questions = sum(len(lesson.get('questions', [])) for lesson in lessons)
            total_quiz = sum(len(q) for q in quiz_questions.values()) if isinstance(quiz_questions, dict) else 0

            return True, f"Xử lý thành công trong {elapsed_time:.1f}s! Đã tạo {len(lessons)} bài học ({total_questions} câu hỏi) và {total_quiz} câu hỏi quiz."

        except TimeoutException:
            elapsed_time = time.time() - start_time
            return False, f"Timeout sau {elapsed_time:.1f}s! Quá trình xử lý mất quá nhiều thời gian. Vui lòng thử lại với nội dung ngắn hơn."
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return False, f"Timeout sau {elapsed_time:.1f}s! Server AI phản hồi chậm. Vui lòng thử lại."
            else:
                return False, f"Lỗi sau {elapsed_time:.1f}s: {error_msg}"
        
        finally:
            # Cancel timeout alarm
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)

    # =========================
    # Đọc & Tiền xử lý nội dung
    # =========================

    def _preprocess_content(self, content: str) -> str:
        """Tiền xử lý nội dung nhưng giữ ký tự đặc biệt cần thiết"""
        # Gom khoảng trắng: giữ lại xuống dòng 2 dấu cách tối thiểu giữa đoạn
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)

        # Loại bỏ control characters nhưng giữ \n, \t
        cleaned_chars = []
        for ch in content:
            if ch == '\n' or ch == '\t' or ch.isprintable():
                cleaned_chars.append(ch)
        content = ''.join(cleaned_chars)

        return content.strip()

    def read_file_content(self, file_path: str) -> Optional[str]:
        """Đọc nội dung từ file với xử lý lỗi tốt hơn"""
        try:
            if not self.is_supported(file_path):
                raise ValueError(f"Định dạng file không được hỗ trợ: {file_path}")

            if file_path.lower().endswith('.txt'):
                # Thử nhiều encoding
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            return f.read()
                    except UnicodeDecodeError:
                        continue
                raise ValueError("Không thể đọc file .txt với các encoding thông dụng")

            elif file_path.lower().endswith('.docx'):
                try:
                    import docx
                    doc = docx.Document(file_path)
                    content = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
                    if not content.strip():
                        raise ValueError("File DOCX trống hoặc không có text")
                    return content
                except ImportError:
                    raise ValueError("Cần cài đặt python-docx để đọc file .docx")

            elif file_path.lower().endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Loại bỏ markdown syntax cơ bản nhưng giữ text
                    content = re.sub(r'(^|\n)#{1,6}\s*', r'\1', content)  # Headers
                    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)    # Bold
                    content = re.sub(r'\*(.*?)\*', r'\1', content)        # Italic
                    content = re.sub(r'`{1,3}([^`]+)`{1,3}', r'\1', content)  # Inline code
                    return content

            elif file_path.lower().endswith('.pdf'):
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        pages_text = []
                        for page in reader.pages:
                            try:
                                t = page.extract_text()
                                if t and t.strip():
                                    pages_text.append(t)
                            except Exception:
                                continue
                        content = "\n".join(pages_text)
                        if not content.strip():
                            raise ValueError("Không thể trích xuất text từ PDF")
                        return content
                except ImportError:
                    raise ValueError("Cần cài đặt PyPDF2 để đọc file .pdf")

        except Exception:
            return None

    # =========================
    # Chunking
    # =========================

    def _intelligent_chunking(self, content: str, target_chunks: int = 5) -> List[str]:
        """Chia content thành các phần thông minh hơn, ưu tiên theo đoạn văn"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if len(paragraphs) <= target_chunks:
            # Nếu ít đoạn văn, chia theo từ
            words = content.split()
            chunk_size = max(80, len(words) // max(1, target_chunks))  # Tối thiểu 80 từ/chunk
            chunks = []
            for i in range(target_chunks):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, len(words))
                if start_idx < len(words):
                    chunk = ' '.join(words[start_idx:end_idx])
                    if chunk.strip():
                        chunks.append(chunk)
            return chunks
        else:
            # Gom số đoạn văn về gần target_chunks
            base = len(paragraphs) // target_chunks
            rem = len(paragraphs) % target_chunks
            chunks = []
            start = 0
            for i in range(target_chunks):
                take = base + (1 if i < rem else 0)
                end = start + take
                chunk = '\n\n'.join(paragraphs[start:end]).strip()
                if chunk:
                    chunks.append(chunk)
                start = end
            return chunks

    # =========================
    # Sinh bài học với timeout
    # =========================

    def generate_lessons_with_timeout(self, chunks: List[str]) -> List[Dict]:
        """Tạo bài học với timeout và error handling toàn diện"""
        results = [None] * len(chunks)
        completed_count = 0

        def _lesson_callback(future, lesson_num):
            nonlocal completed_count
            try:
                result = future.result(timeout=self.timeout)
                results[lesson_num - 1] = result
                completed_count += 1
            except Exception as e:
                results[lesson_num - 1] = self._create_fallback_lesson(
                    lesson_num,
                    chunks[lesson_num - 1] if lesson_num - 1 < len(chunks) else ""
                )
                completed_count += 1

        with ThreadPoolExecutor(max_workers=min(3, len(chunks))) as executor:
            futures = []
            for i, chunk in enumerate(chunks):
                if self.should_stop:
                    break
                future = executor.submit(self._generate_single_lesson_safe, chunk, i + 1)
                future.add_done_callback(lambda f, num=i + 1: _lesson_callback(f, num))
                futures.append(future)

            # Chờ với timeout
            try:
                for _ in as_completed(futures, timeout=self.timeout * len(chunks)):
                    if self.should_stop:
                        break
            except TimeoutError:
                pass

        return [r for r in results if r is not None]

    def _generate_single_lesson_safe(self, chunk: str, lesson_number: int) -> Dict:
        """Tạo một bài học với timeout và error handling an toàn"""
        for attempt in range(self.max_retries):
            try:
                if self.should_stop:
                    break

                # Giới hạn độ dài chunk để tránh vượt quá token limit
                max_chunk_length = 1200  # Giảm xuống để tăng tốc độ
                chunk_for_prompt = (chunk[:max_chunk_length] + "...") if len(chunk) > max_chunk_length else chunk

                prompt = f"""
Tạo bài học số {lesson_number} từ nội dung sau:
{chunk_for_prompt}

Yêu cầu:
0. không bị lỗi charmap
1. Tiêu đề ngắn gọn, phản ánh nội dung chính
2. Nội dung tóm tắt 150-250 từ, tập trung vào ý quan trọng
3. {self.questions_per_lesson} câu hỏi với độ khó phân bổ đều:
   - {self.questions_per_lesson // 3} câu dễ (easy)
   - {self.questions_per_lesson // 3} câu trung bình (medium)
   - {self.questions_per_lesson - 2 * (self.questions_per_lesson // 3)} câu khó (hard)
4. Mỗi câu hỏi có:
   - Câu hỏi rõ ràng, liên quan trực tiếp đến nội dung
   - 4 lựa chọn A, B, C, D
   - Đáp án đúng là chỉ số 0-3 (0 = A, 1 = B, 2 = C, 3 = D)
   - KHÔNG tạo câu hỏi mẫu hay placeholder

Trả về **chỉ JSON** hợp lệ theo mẫu:
{{
  "name": "Bài {lesson_number}",
  "title": "[Tiêu đề cụ thể về nội dung]",
  "content": "[Nội dung tóm tắt chi tiết]",
  "questions": [
    {{
      "question": "[Câu hỏi chi tiết về nội dung]",
      "choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": 0,
      "difficulty": "easy"
    }}
  ]
}}
"""

                # Gọi API với timeout
                response = self.client.chat.completions.create(
                    model=gpt_4o_mini,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6,  # Giảm temperature để tăng độ ổn định
                )

                response_text = (response.choices[0].message.content or "").strip()

                if not response_text:
                    raise ValueError("Response rỗng từ AI")

                # Parse JSON an toàn
                lesson = self._safe_parse_json(response_text)
                if not lesson:
                    raise ValueError("Không parse được JSON từ response")

                return self._validate_lesson(lesson, lesson_number, chunk)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self._create_fallback_lesson(lesson_number, chunk)
                time.sleep(min(2 ** attempt, 5))  # Exponential backoff với max 5s

    def _safe_parse_json(self, text: str) -> Optional[Dict]:
        """Parse JSON an toàn với nhiều phương pháp"""
        # Method 1: Thử parse trực tiếp
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Method 2: Tìm JSON object trong text
        json_candidates = self._extract_json_objects(text)
        for candidate in json_candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and self._is_valid_lesson_structure(parsed):
                    return parsed
            except json.JSONDecodeError:
                continue

        # Method 3: Thử clean up text và parse lại
        try:
            # Loại bỏ markdown code blocks
            cleaned = re.sub(r'```json\s*', '', text)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            # Loại bỏ các ký tự không cần thiết đầu/cuối
            cleaned = cleaned.strip().strip('`').strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        return None

    def _is_valid_lesson_structure(self, data: Dict) -> bool:
        """Kiểm tra cấu trúc lesson có hợp lệ không"""
        required_fields = ['name', 'title', 'content', 'questions']
        if not all(field in data for field in required_fields):
            return False
        
        if not isinstance(data['questions'], list):
            return False
            
        return True

    def _extract_json_objects(self, text: str) -> List[str]:
        """
        Quét chuỗi để trích xuất các JSON object cấp cao nhất bằng cách đếm dấu ngoặc.
        """
        results = []
        stack = 0
        in_string = False
        escape = False
        start_idx = None

        for i, ch in enumerate(text):
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            else:
                if ch == '"':
                    in_string = True
                    continue
                if ch == '{':
                    if stack == 0:
                        start_idx = i
                    stack += 1
                elif ch == '}':
                    if stack > 0:
                        stack -= 1
                        if stack == 0 and start_idx is not None:
                            results.append(text[start_idx:i + 1])
                            start_idx = None

        return results

    # =========================
    # Validate & Fallback
    # =========================

    def _validate_lesson(self, lesson: Dict, lesson_number: int, chunk: str) -> Dict:
        """Đảm bảo bài học có đủ câu hỏi và dữ liệu hợp lệ"""
        # Trường bắt buộc
        lesson.setdefault("name", f"Bài {lesson_number}")
        lesson.setdefault("title", f"Bài học {lesson_number}")
        lesson.setdefault("content", chunk[:300] + "..." if len(chunk) > 300 else chunk)

        # Câu hỏi
        if "questions" not in lesson or not isinstance(lesson["questions"], list):
            lesson["questions"] = []

        # Đảm bảo đủ số câu hỏi
        while len(lesson["questions"]) < self.questions_per_lesson:
            lesson["questions"].append(self._create_default_question(
                len(lesson["questions"]) + 1,
                lesson_number,
                chunk
            ))

        # Giới hạn số câu hỏi
        lesson["questions"] = lesson["questions"][:self.questions_per_lesson]

        # Validate từng câu hỏi
        for i, q in enumerate(lesson["questions"]):
            if not isinstance(q, dict):
                lesson["questions"][i] = self._create_default_question(i + 1, lesson_number, chunk)
                continue

            q.setdefault("question", f"Câu hỏi {i + 1} bài {lesson_number}")
            q.setdefault("choices", ["A. Lựa chọn A", "B. Lựa chọn B", "C. Lựa chọn C", "D. Lựa chọn D"])
            q.setdefault("correct_answer", 0)
            q.setdefault("difficulty", "medium")

            # Đảm bảo có đủ 4 lựa chọn
            if not isinstance(q["choices"], list) or len(q["choices"]) != 4:
                q["choices"] = ["A. Lựa chọn A", "B. Lựa chọn B", "C. Lựa chọn C", "D. Lựa chọn D"]

            # Đảm bảo correct_answer hợp lệ
            if not isinstance(q["correct_answer"], int) or q["correct_answer"] < 0 or q["correct_answer"] > 3:
                q["correct_answer"] = 0

            # Chuẩn hoá difficulty
            if q.get("difficulty") not in {"easy", "medium", "hard"}:
                q["difficulty"] = "medium"

        return lesson

    def _create_default_question(self, q_num: int, lesson_num: int, content: str) -> Dict:
        """Tạo câu hỏi mặc định từ nội dung"""
        difficulties = ["easy", "medium", "hard"]
        difficulty = difficulties[(q_num - 1) % 3]

        # Lấy mẫu nội dung để ghép vào câu hỏi
        words = content.split()
        sample = " ".join(words[:15]) if words else ""

        return {
            "question": f"Theo nội dung bài {lesson_num}, điều gì được nhấn mạnh về '{sample[:40]}...'?",
            "choices": [
                "A. Đây là thông tin quan trọng nhất",
                "B. Đây là thông tin bổ sung",
                "C. Đây là ví dụ minh họa",
                "D. Đây là kết luận chính"
            ],
            "correct_answer": 0,
            "difficulty": difficulty
        }

    def _create_fallback_lesson(self, lesson_number: int, chunk: str) -> Dict:
        """Tạo bài học dự phòng chất lượng ổn"""
        content = chunk[:350] + "..." if len(chunk) > 350 else chunk

        # Tạo tiêu đề từ 8 từ đầu tiên
        words = chunk.split()[:8]
        title = " ".join(words) if words else f"Bài học {lesson_number}"
        if len(title) > 45:
            title = title[:42] + "..."

        questions = [self._create_default_question(i + 1, lesson_number, chunk) for i in range(self.questions_per_lesson)]

        return {
            "name": f"Bài {lesson_number}",
            "title": title,
            "content": content,
            "questions": questions
        }

    # =========================
    # Quiz tổng hợp với timeout
    # =========================

    def generate_quiz_with_timeout(self, lessons: List[Dict], total_questions: int = 10) -> Dict:
        """Tạo quiz tổng hợp với timeout"""
        try:
            return self.generate_quiz(lessons, total_questions)
        except Exception as e:
            return self._create_fallback_quiz(lessons, total_questions)

    def generate_quiz(self, lessons: List[Dict], total_questions: int = 10) -> Dict:
        """Tạo quiz tổng hợp với phân bổ độ khó hợp lý (40/40/20)"""
        quiz = {"easy": [], "medium": [], "hard": []}

        # Phân bổ câu hỏi theo tỷ lệ: 40% dễ, 40% trung bình, 20% khó
        easy_count = int(total_questions * 0.4)
        medium_count = int(total_questions * 0.4)
        hard_count = total_questions - easy_count - medium_count

        question_id = 1

        # Tạo câu hỏi dễ
        for _ in range(easy_count):
            quiz["easy"].append(self._generate_quiz_question(question_id, "easy", lessons))
            question_id += 1

        # Tạo câu hỏi trung bình
        for _ in range(medium_count):
            quiz["medium"].append(self._generate_quiz_question(question_id, "medium", lessons))
            question_id += 1

        # Tạo câu hỏi khó
        for _ in range(hard_count):
            quiz["hard"].append(self._generate_quiz_question(question_id, "hard", lessons))
            question_id += 1

        return quiz

    def _generate_quiz_question(self, q_id: int, difficulty: str, lessons: List[Dict]) -> Dict:
        """Tạo một câu hỏi quiz từ các bài học"""
        import random
        lesson = random.choice(lessons) if lessons else None

        if not lesson:
            return {
                "id": q_id,
                "question": f"Câu hỏi {q_id} ({difficulty})",
                "choices": ["A. Lựa chọn A", "B. Lựa chọn B", "C. Lựa chọn C", "D. Lựa chọn D"],
                "correct_answer": 0,
                "difficulty": difficulty
            }

        content = (lesson.get("content") or "")[:80]
        title = lesson.get("title", f"Bài {q_id}")

        return {
            "id": q_id,
            "question": f"Trong {title}, nội dung chính đề cập đến điều gì?",
            "choices": [
                f"A. {content[:25]}..." if content else "A. Thông tin chính",
                "B. Thông tin bổ sung",
                "C. Ví dụ minh họa",
                "D. Kết luận tổng quát"
            ],
            "correct_answer": 0,
            "difficulty": difficulty
        }

    def _create_fallback_quiz(self, lessons: List[Dict], total_questions: int) -> Dict:
        """Tạo quiz dự phòng từ lessons"""
        quiz = {"easy": [], "medium": [], "hard": []}
        
        easy_count = int(total_questions * 0.4)
        medium_count = int(total_questions * 0.4)
        hard_count = total_questions - easy_count - medium_count

        for i in range(easy_count):
            quiz["easy"].append(self._generate_quiz_question(i + 1, "easy", lessons))
            
        for i in range(medium_count):
            quiz["medium"].append(self._generate_quiz_question(easy_count + i + 1, "medium", lessons))
            
        for i in range(hard_count):
            quiz["hard"].append(self._generate_quiz_question(easy_count + medium_count + i + 1, "hard", lessons))
            
        return quiz

    # =========================
    # Lưu dữ liệu an toàn
    # =========================

    def _safe_save_data_files(self, lessons: List[Dict], quiz: Dict) -> bool:
        """Lưu dữ liệu vào file với error handling toàn diện"""
        try:
            # Tính toán thống kê
            total_lesson_questions = sum(len(lesson.get('questions', [])) for lesson in lessons)
            total_quiz_questions = sum(len(q) for q in quiz.values()) if isinstance(quiz, dict) else 0

            # Tạo backup paths
            lessons_backup = self.lessons_path + '.backup'
            quiz_backup = self.quiz_path + '.backup'

            # Backup files cũ nếu tồn tại
            if os.path.exists(self.lessons_path):
                try:
                    import shutil
                    shutil.copy2(self.lessons_path, lessons_backup)
                except Exception:
                    pass  # Ignore backup errors

            if os.path.exists(self.quiz_path):
                try:
                    import shutil
                    shutil.copy2(self.quiz_path, quiz_backup)
                except Exception:
                    pass  # Ignore backup errors

            # Chuẩn bị dữ liệu lessons
            lessons_data = {
                "metadata": {
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_lessons": len(lessons),
                    "total_questions": total_lesson_questions,
                    "questions_per_lesson": self.questions_per_lesson,
                    "settings": {
                        "lessons_count": self.lessons_count,
                        "questions_per_lesson": self.questions_per_lesson,
                        "quiz_questions": self.quiz_questions
                    }
                },
                "lessons": lessons
            }

            # Chuẩn bị dữ liệu quiz
            quiz_data = {
                "metadata": {
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_questions": total_quiz_questions,
                    "difficulty_distribution": {
                        "easy": len(quiz.get("easy", [])),
                        "medium": len(quiz.get("medium", [])),
                        "hard": len(quiz.get("hard", []))
                    }
                },
                **quiz
            }

            # Kiểm tra JSON serializable trước khi lưu
            try:
                json.dumps(lessons_data, ensure_ascii=False)
                json.dumps(quiz_data, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                return False

            # Lưu lessons với atomic write
            temp_lessons_path = self.lessons_path + '.tmp'
            with open(temp_lessons_path, 'w', encoding='utf-8') as f:
                json.dump(lessons_data, f, ensure_ascii=False, indent=2)
            
            # Atomic rename
            if os.name == 'nt':  # Windows
                if os.path.exists(self.lessons_path):
                    os.remove(self.lessons_path)
            os.rename(temp_lessons_path, self.lessons_path)

            # Lưu quiz với atomic write
            temp_quiz_path = self.quiz_path + '.tmp'
            with open(temp_quiz_path, 'w', encoding='utf-8') as f:
                json.dump(quiz_data, f, ensure_ascii=False, indent=2)
            
            # Atomic rename
            if os.name == 'nt':  # Windows
                if os.path.exists(self.quiz_path):
                    os.remove(self.quiz_path)
            os.rename(temp_quiz_path, self.quiz_path)

            # Kiểm tra files đã được tạo và có dữ liệu
            if not os.path.exists(self.lessons_path) or os.path.getsize(self.lessons_path) == 0:
                raise Exception("File lessons không được tạo hoặc rỗng")

            if not os.path.exists(self.quiz_path) or os.path.getsize(self.quiz_path) == 0:
                raise Exception("File quiz không được tạo hoặc rỗng")

            # Xóa backup files nếu save thành công
            try:
                if os.path.exists(lessons_backup):
                    os.remove(lessons_backup)
                if os.path.exists(quiz_backup):
                    os.remove(quiz_backup)
            except Exception:
                pass  # Ignore cleanup errors

            return True

        except Exception as e:
            
            # Restore from backup nếu có
            try:
                if os.path.exists(lessons_backup):
                    import shutil
                    shutil.copy2(lessons_backup, self.lessons_path)
                if os.path.exists(quiz_backup):
                    import shutil
                    shutil.copy2(quiz_backup, self.quiz_path)
            except Exception:
                pass

            return False

    # =========================
    # Utility methods
    # =========================

    def stop_processing(self):
        """Dừng quá trình xử lý"""
        self.should_stop = True

    def get_progress_info(self) -> Dict:
        """Lấy thông tin tiến trình (có thể mở rộng sau)"""
        return {
            "lessons_count": self.lessons_count,
            "questions_per_lesson": self.questions_per_lesson,
            "quiz_questions": self.quiz_questions,
            "timeout": self.timeout,
            "total_timeout": self.total_timeout
        }

    def validate_config(self) -> Tuple[bool, str]:
        """Kiểm tra cấu hình hệ thống"""
        try:
            # Kiểm tra thư mục assets
            if not os.path.exists(config.ASSETS_DIR):
                try:
                    os.makedirs(config.ASSETS_DIR)
                except Exception as e:
                    return False, f"Không thể tạo thư mục {config.ASSETS_DIR}: {e}"

            # Kiểm tra quyền ghi
            test_file = os.path.join(config.ASSETS_DIR, 'test_write.tmp')
            try:
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                return False, f"Không có quyền ghi trong {config.ASSETS_DIR}: {e}"

            # Kiểm tra client AI
            try:
                if not hasattr(self.client, 'chat'):
                    return False, "Client AI không hợp lệ"
            except Exception as e:
                return False, f"Lỗi client AI: {e}"

            return True, "Cấu hình hệ thống OK"

        except Exception as e:
            return False, f"Lỗi kiểm tra cấu hình: {e}"

    def cleanup_cache(self):
        """Dọn dẹp cache"""
        self.content_cache.clear()

    def get_cache_info(self) -> Dict:
        """Lấy thông tin cache"""
        return {
            "cache_size": len(self.content_cache),
            "cache_keys": list(self.content_cache.keys())[:5]  # Show first 5 keys only
        }