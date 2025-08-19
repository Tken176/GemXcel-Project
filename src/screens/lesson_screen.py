import pygame
import json
import os
import config
import ui_elements
import screens.exercise_screen
import time

def load_lessons_data():
    """Load lesson data from JSON file"""
    if not os.path.exists(config.LESSON_DATA_FILE_PATH):
        return []  # Không in lỗi nếu file chưa tồn tại

    try:
        with open(config.LESSON_DATA_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data["lessons"]
    except Exception as e:
        print(f"Error parsing lesson data: {e}")
        return []


# Biến để theo dõi thời điểm sửa đổi file cuối cùng
last_modified_time = 0
list_lesson = []

def check_for_updates():
    """Kiểm tra xem file dữ liệu có thay đổi không"""
    global last_modified_time
    try:
        current_modified_time = os.path.getmtime(config.LESSON_DATA_FILE_PATH)
        if current_modified_time > last_modified_time:
            last_modified_time = current_modified_time
            return True
        return False
    except:
        return False

def draw_lesson(screen, font_path, font_title, font, colors, game_state, switch_screen_callback, handle_button_click_callback):
    global list_lesson

    # Kiểm tra và cập nhật dữ liệu nếu file thay đổi
    if check_for_updates():
        updated_data = load_lessons_data()
        if updated_data:  # chỉ cập nhật nếu có dữ liệu
            list_lesson = updated_data

    lessons_data = list_lesson

    if not lessons_data:
        empty_text = font.render("Chưa có bài học nào hãy đưa cho tôi bài học của bạn ở 'Nạp File'.", True, colors["text"])
        screen.blit(empty_text, (220, 210))
        return

    # Vẽ tiêu đề
    title = font_title.render("Bài học", True, colors["text"])
    screen.blit(title, (210, 30))

    # Hiển thị danh sách bài học
    for i, lesson in enumerate(lessons_data):
        x, y = 240, 100 + i * 100
        rect = pygame.Rect(x, y, 680, 90)

        # Lấy số bài học từ trường "name" (ví dụ: "Bài 1" -> 1)
        try:
            lesson_id = int(lesson["name"].split()[-1])
        except (KeyError, ValueError, IndexError):
            lesson_id = i + 1

        # Xác định màu nền dựa trên trạng thái hoàn thành
        if lesson_id in game_state.completed_lessons:
            base_color = colors["correct"]
        else:
            base_color = colors["white"]

        # Tô màu nếu hover (chỉ áp dụng nếu bài chưa hoàn thành)
        if rect.collidepoint(pygame.mouse.get_pos()) and lesson_id not in game_state.completed_lessons:
            pygame.draw.rect(screen, colors["accent"], rect, border_radius=10)
        else:
            pygame.draw.rect(screen, base_color, rect, border_radius=10)

        # Render tên bài học và tiêu đề
        name_font = pygame.font.Font(font_path, 30)
        title_font = pygame.font.Font(font_path, 24)

        name = name_font.render(lesson.get("name", f"Bài {i+1}"), True, colors["text"])
        lesson_title = lesson.get("title", "Không có tiêu đề")
        short_title = (lesson_title[:50] + "...") if len(lesson_title) > 50 else lesson_title
        title_text = title_font.render(short_title, True, colors["text"])

        screen.blit(name, (x + 20, y + 15))
        screen.blit(title_text, (x + 20, y + 55))
