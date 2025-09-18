import pygame
import json
import config

def load_lessons_data():
    """Tải dữ liệu bài học từ file JSON"""
    try:
        with open(config.LESSON_DATA_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get("lessons", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def wrap_text(content, font, max_width):
    """Chia văn bản thành các dòng vừa với max_width"""
    words = content.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] > max_width:
            if current_line.strip():
                lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line

    if current_line.strip():
        lines.append(current_line.strip())

    return lines

def wrap_title_text(title_text, font, max_width):
    """Tự động xuống dòng tiêu đề nếu quá dài"""
    return wrap_text(title_text, font, max_width)

def get_page_count(game_state):
    """Lấy tổng số trang của bài học hiện tại"""
    if hasattr(game_state, 'lesson_pages'):
        return len(game_state.lesson_pages)
    return 0

def draw_knowledge_page(screen, font_title, font, colors, game_state, handle_button_click_callback, switch_screen_callback):
    """Vẽ màn hình kiến thức với chức năng phân trang"""
    lessons_data = load_lessons_data()
    if not lessons_data:
        error_text = font.render("Không tải được dữ liệu bài học", True, colors["text"])
        screen.blit(error_text, (config.WIDTH//2 - error_text.get_width()//2, config.HEIGHT//2))
        return

    lesson_id = game_state.current_lesson_id
    page_index = game_state.current_page_index

    if not (1 <= lesson_id <= len(lessons_data)):
        error_text = font.render("Bài học không tồn tại", True, colors["text"])
        screen.blit(error_text, (config.WIDTH//2 - error_text.get_width()//2, config.HEIGHT//2))
        return

    current_lesson = lessons_data[lesson_id - 1]
    content_area_width = config.WIDTH - 240

    # cache nội dung để không tính lại nhiều lần
    if not hasattr(game_state, 'lesson_lines_dict'):
        game_state.lesson_lines_dict = {}

    if lesson_id not in game_state.lesson_lines_dict:
        # Tách nội dung thành từng dòng theo chiều ngang
        all_lines = []
        for paragraph in current_lesson["content"].split("\n"):
            if paragraph.strip():
                all_lines.extend(wrap_text(paragraph, font, content_area_width))
                all_lines.append("")  # thêm dòng trống giữa đoạn

        game_state.lesson_lines_dict[lesson_id] = all_lines
        game_state.current_page_index = 0

    all_lines = game_state.lesson_lines_dict[lesson_id]

    # Tính chiều cao tiêu đề (chỉ trang đầu mới có)
    title_height = 0
    title_lines = []
    if page_index == 0:
        title_text = f"{current_lesson['name']}: {current_lesson['title']}"
        title_lines = wrap_title_text(title_text, font_title, config.WIDTH - 260)
        title_height = len(title_lines) * (font_title.get_linesize() + 5) + 20

    # Tính số dòng có thể hiển thị trong 1 trang
    line_height = font.get_linesize() + 5
    usable_height = config.HEIGHT - (30 + title_height) - 100  # chừa 100px cho footer & nút
    max_lines = max(1, usable_height // line_height)

    # cache các trang đã chia
    if not hasattr(game_state, 'lesson_pages_dict'):
        game_state.lesson_pages_dict = {}

    if lesson_id not in game_state.lesson_pages_dict:
        pages = []
        idx = 0
        while idx < len(all_lines):
            pages.append(all_lines[idx:idx + max_lines])
            idx += max_lines
        game_state.lesson_pages_dict[lesson_id] = pages

    pages = game_state.lesson_pages_dict[lesson_id]
    game_state.lesson_pages = pages  # để main.py còn dùng get_page_count

    if page_index >= len(pages):
        page_index = len(pages) - 1
        game_state.current_page_index = page_index

    # Vẽ tiêu đề (chỉ trang đầu)
    if page_index == 0:
        for i, line in enumerate(title_lines):
            title_surface = font_title.render(line, True, colors["text"])
            screen.blit(title_surface, (230, 30 + i * (font_title.get_linesize() + 5)))

    y_offset = 30 + title_height

    # Vẽ nội dung trang
    for i, line in enumerate(pages[page_index]):
        if line.strip():
            text_surface = font.render(line, True, colors["text"])
            y_pos = y_offset + i * line_height
            screen.blit(text_surface, (230, y_pos))

    # Hiển thị số trang
    page_text = f"Trang {page_index + 1}/{len(pages)}"
    page_surface = font.render(page_text, True, colors["text"])
    screen.blit(page_surface, (config.WIDTH - 160, config.HEIGHT - 50))

def finish_lesson_and_start_quiz(game_state, lesson_id, switch_screen_callback):
    """Kết thúc bài học và chuyển sang màn hình quiz"""
    lessons_data = load_lessons_data()
    if not (1 <= lesson_id <= len(lessons_data)):
        return

    current_lesson = lessons_data[lesson_id - 1]
    quiz_questions = current_lesson.get("questions", [])

    if quiz_questions:
        game_state.quiz_state = {
            "bai": lesson_id,
            "index": 0,
            "answered": False,
            "selected": None,
            "feedback": ""
        }
        switch_screen_callback(config.SCREEN_QUIZ_SCREEN)
    else:
        game_state.point += 50
        if lesson_id not in game_state.completed_lessons:
            game_state.completed_lessons.append(lesson_id)
        game_state.show_message("Bạn đã hoàn thành bài học!")
        switch_screen_callback(config.SCREEN_LESSON)
