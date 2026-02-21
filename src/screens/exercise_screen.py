import pygame
import ui_elements
import config
import json
import os
import time
import random
import math

# Khai báo biến toàn cục
exercise_data = None
correct_sound = None
wrong_sound = None
click_sound = None
transition_timer = None
def draw_mode_description(screen, start_y=400, max_width=600):
    lines = [
        "1.Chế độ dễ: Các câu hỏi cơ bản, giúp làm quen và ôn tập kiến thức nền tảng. Mỗi câu đúng được 10 điểm.",
        "2.Chế độ trung bình: Câu hỏi ở mức độ vận dụng, yêu cầu kết hợp lý thuyết và suy luận. Mỗi câu đúng được 15 điểm.", 
        "3.Chế độ khó: Câu hỏi nâng cao, đòi hỏi phân tích sâu và tư duy phản biện. Mỗi câu đúng được 20 điểm."
    ]
    y = start_y
    for line in lines:
        # Dùng wrap_text có sẵn
        wrapped = _wrap_text(line, config.FONT_SMALL, max_width)
        for w in wrapped:
            txt = config.FONT_SMALL.render(w, True, (60, 60, 60))
            screen.blit(txt, (540, y))
            y += config.FONT_SMALL.get_linesize()
        y += 20  # khoảng cách giữa các gạch đầu dòng


def set_sounds(correct, wrong):
    global correct_sound, wrong_sound
    correct_sound = correct
    wrong_sound = wrong

def set_click_sound(sound):
    global click_sound
    click_sound = sound

def load_exercise_data():
    global exercise_data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    data_path = config.QUIZ_DATA_FILE_PATH

    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            exercise_data = json.load(file)
            # Ensure all questions have points
            for difficulty in ["easy", "medium", "hard"]:
                if difficulty in exercise_data:
                    for question in exercise_data[difficulty]:
                        if "points" not in question:
                            # Set default points based on difficulty
                            if difficulty == "easy":
                                question["points"] = 10
                            elif difficulty == "medium":
                                question["points"] = 15
                            else:  # hard
                                question["points"] = 20
    except FileNotFoundError:
        exercise_data = {
            "easy": [{
                "id": 1,
                "question": "Câu hỏi mẫu (dễ)?",
                "choices": ["A", "B", "C", "D"],
                "correct_answer": 0,
                "points": 10
            }],
            "medium": [{
                "id": 1,
                "question": "Câu hỏi mẫu (trung bình)?",
                "choices": ["A", "B", "C", "D"],
                "correct_answer": 1,
                "points": 15
            }],
            "hard": [{
                "id": 1,
                "question": "Câu hỏi mẫu (khó)?",
                "choices": ["A", "B", "C", "D"],
                "correct_answer": 2,
                "points": 20
            }]
        }
    except Exception as e:
        print(f"Error loading exercise data: {e}")
        exercise_data = {"easy": [], "medium": [], "hard": []}

def create_difficulty_callback(difficulty, game_state, switch_screen_callback):
    def callback():
        if game_state.energy < 1:
            game_state.purchase_message = "Không đủ năng lượng!"
            game_state.message_timer = time.time()
        else:
            start_exercise_session(game_state, difficulty, switch_screen_callback)
    return callback

def draw_rounded_rect(surface, color, rect, radius=20, border=0, border_color=None):
    rect = pygame.Rect(rect)
    if border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)
    pygame.draw.rect(surface, color, rect.inflate(-border*2, -border*2), border_radius=radius)

def draw_icon(surface, icon_type, x, y, size=30):
    if icon_type == "easy":
        pygame.draw.circle(surface, (100, 200, 100), (x, y), size//2)
        pygame.draw.ellipse(surface, (150, 240, 150), (x-size//4, y-size//2, size//2, size))
    elif icon_type == "medium":
        pygame.draw.polygon(surface, (255, 180, 50), [
            (x, y-size//2),
            (x+size//2, y),
            (x, y+size//2),
            (x-size//2, y)
        ])
    elif icon_type == "hard":
        pygame.draw.polygon(surface, (255, 100, 100), [
            (x, y-size//2),
            (x+size//3, y+size//2),
            (x-size//3, y+size//2)
        ])

def draw_exercise(screen, game_state, switch_screen_callback):
    global exercise_data
    if exercise_data is None:
        load_exercise_data()

    buttons = []
    draw_mode_description(screen,150, config.WIDTH - 620)


    # Nút quay lại
    back_button = ui_elements.Button(
        x=100, y=50, w=120, h=50,
        text="Quay lại",
        callback=lambda: switch_screen_callback(config.SCREEN_LESSON),
        color=(120, 80, 60),
        border_radius=10,  # có thể bỏ bo góc
        click_sound=click_sound
    )
    buttons.append(back_button)

    # Các mức độ khó
    difficulty_levels = [
        {"name": "DỄ", "desc": "10 điểm/câu", "diff": "easy", "color": (100, 200, 100)},
        {"name": "TRUNG BÌNH", "desc": "15 điểm/câu", "diff": "medium", "color": (255, 180, 50)},
        {"name": "KHÓ", "desc": "20 điểm/câu", "diff": "hard", "color": (255, 100, 100)},
    ]

    card_y = 120
    for level in difficulty_levels:
        btn = ui_elements.Button(
            x=100, y=card_y + 20, w=300, h=60,
            text=level["name"],
            callback=create_difficulty_callback(level["diff"], game_state, switch_screen_callback),
            color=level["color"],
            border_radius=10,
            click_sound=click_sound
        )
        buttons.append(btn)

        desc = config.FONT_SMALL.render(level["desc"], True, (100, 100, 100))
        screen.blit(desc, (100, card_y + 90))

        card_y += 150

    # Hiển thị năng lượng
    energy_text = config.FONT_SMALL.render(f"Năng lượng: {game_state.energy}", True, (0, 0, 0))
    screen.blit(energy_text, (config.WIDTH - energy_text.get_width() - 110, 40))

    # Vẽ tất cả nút
    for button in buttons:
        button.draw(screen)

    return buttons


def _get_wrap_func():
    """Trả về hàm wrap từ ui_elements nếu có, còn không trả về fallback."""
    if hasattr(ui_elements, "wrap_text") and callable(getattr(ui_elements, "wrap_text")):
        return ui_elements.wrap_text
    return _wrap_text

def _wrap_text(text: str, font: pygame.font.Font, max_width: int):
    """
    Trả về danh sách các dòng đã được wrap để vừa max_width.
    Xử lý newline trong text, và tách từ nếu một từ dài hơn max_width.
    """
    if text is None:
        return [""]
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        words = para.split(" ")
        if not words:
            lines.append("")
            continue
        cur_line = ""
        for w in words:
            test = (cur_line + " " + w) if cur_line else w
            if font.size(test)[0] <= max_width:
                cur_line = test
            else:
                if cur_line:
                    lines.append(cur_line)
                # nếu từ w vẫn quá dài, tách theo ký tự
                if font.size(w)[0] > max_width:
                    part = ""
                    for ch in w:
                        if font.size(part + ch)[0] <= max_width:
                            part += ch
                        else:
                            if part:
                                lines.append(part)
                            part = ch
                    if part:
                        cur_line = part
                    else:
                        cur_line = ""
                else:
                    cur_line = w
        if cur_line:
            lines.append(cur_line)
    return lines or [""]

def draw_exercise_quiz(screen, game_state, switch_screen_callback):
    global transition_timer
    
    buttons = []
    exercise_state = game_state.exercise_state

    if not exercise_state or exercise_state["completed"]:
        if transition_timer:
            pygame.time.set_timer(transition_timer, 0)
            transition_timer = None
        switch_screen_callback(config.SCREEN_EXERCISE)
        return buttons

    current_question = exercise_state["questions"][exercise_state["current_question"]]
    wrap_func = _get_wrap_func()

    for i in range(30):
        x = random.randint(0, config.WIDTH)
        y = random.randint(0, config.HEIGHT)
        size = random.randint(2, 8)
        alpha = random.randint(10, 30)
        dot_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (200, 230, 200, alpha), (size, size), size)
        screen.blit(dot_surf, (x, y))
    
    # Layout: chia màn hình làm hai cột giống quiz_screen
    margin = 40
    page_width = (config.WIDTH - margin * 3) // 2
    left_x = margin + 50
    right_x = left_x + page_width + margin - 25
    top_y = 150
    content_width = page_width - 70

    # Đếm câu hỏi ở góc trên phải
    counter = config.FONT_SMALL.render(f"Câu {exercise_state['current_question']+1}/{len(exercise_state['questions'])}", True, (80, 120, 80))
    screen.blit(counter, (config.WIDTH - counter.get_width() - 100, 550))

    # --- Vẽ tiêu đề "Câu thứ n" phía trên câu hỏi ---
    try:
        title_text = f"Câu {exercise_state['current_question'] + 1}"
        title_surf = config.FONT_TITLE.render(title_text, True, (80, 120, 80))
        screen.blit(title_surf, (left_x, top_y - title_surf.get_height() - 20))
    except Exception:
        pass

    # --- Vẽ câu hỏi bên trái ---
    try:
        ui_elements.draw_multiline_text(
            screen,
            current_question.get("question", ""),
            left_x,
            top_y,
            config.FONT,
            (70, 70, 70),
            content_width
        )
    except Exception:
        try:
            txt = current_question.get("question", "")[:200]
            t_surf = config.FONT.render(txt, True, (70, 70, 70))
            screen.blit(t_surf, (left_x, top_y))
        except Exception:
            pass

    # Vẽ đáp án bên phải, đảm bảo wrap nội dung trong box
    choice_top_y = top_y
    choice_spacing = 20
    choice_height_min = 45

    choices = current_question.get("choices", [])
    # Precompute wrapped lines & heights
    wrappeds = [wrap_func(choice, config.FONT, content_width - 20) for choice in choices]

    # Tính tổng chiều cao cần thiết; nếu vượt quá vùng có thể, giảm khoảng cách
    total_req_height = 0
    for w in wrappeds:
        text_height = max(1, len(w)) * config.FONT.get_linesize()
        total_req_height += max(choice_height_min, text_height + 10)
    total_req_height += (len(choices) - 1) * choice_spacing

    available_height = config.HEIGHT - top_y - 140  # dành chỗ cho feedback & nút bấm dưới
    if total_req_height > available_height:
        # giảm spacing xuống mức tối thiểu
        choice_spacing = 8
        total_req_height = 0
        for w in wrappeds:
            text_height = max(1, len(w)) * config.FONT.get_linesize()
            total_req_height += max(choice_height_min, text_height + 10)
        total_req_height += (len(choices) - 1) * choice_spacing

    # Vẽ từng button
    y = choice_top_y
    for idx, wrapped in enumerate(wrappeds):
        text_height = max(1, len(wrapped)) * config.FONT.get_linesize()
        choice_height = max(choice_height_min, text_height + 10)

        # Xác định màu button tùy trạng thái
        if exercise_state.get("answered", False):
            if idx == current_question["correct_answer"]:
                color = (100, 200, 100)  # Xanh cho đúng
            elif idx == exercise_state.get("user_answer"):
                color = (255, 120, 120)  # Đỏ cho sai
            else:
                color = (250, 235, 215)  # Xám cho các lựa chọn khác
        else:
            color = (255, 228, 196)  # Màu xanh lá nhạt mặc định

        # Tạo button (truyền text rỗng, vẽ text thủ công) để tránh giới hạn ký tự trong Button
        # IMPORTANT: freeze current values into default args to avoid late-binding issues
        btn = ui_elements.Button(
            right_x,
            y,
            content_width,
            choice_height,
            "",
            lambda i=idx: handle_answer_selection(game_state, i, switch_screen_callback),
            color,
            8,
            click_sound
        )
        try:
            btn.draw(screen)
        except Exception:
            pass

        # Vẽ text wrapped trong button, căn giữa
        line_y = y + 5
        for line in wrapped:
            try:
                text_surface = config.FONT.render(line, True, (70, 70, 70))
            except Exception:
                text_surface = config.FONT.render(line, True, (0, 0, 0))
            screen.blit(
                text_surface,
                (right_x + (content_width - text_surface.get_width()) // 2, line_y)
            )
            line_y += config.FONT.get_linesize()

        buttons.append(btn)
        y += choice_height + choice_spacing

    # Hiển thị feedback nếu đã trả lời
    if exercise_state.get("answered", False):
        is_correct = exercise_state.get("user_answer") == current_question["correct_answer"]
        feedback = "Chính xác!" if is_correct else "Sai rồi."
        feedback_color = (80, 160, 80) if is_correct else (200, 80, 80)

        try:
            ui_elements.draw_text_centered(
                screen,
                feedback,
                right_x + content_width // 2,
                y + 10,
                config.FONT,
                feedback_color
            )
        except Exception:
            try:
                t = config.FONT.render(feedback, True, feedback_color)
                screen.blit(t, (right_x + (content_width - t.get_width()) // 2, y + 10))
            except Exception:
                pass
    return buttons


def handle_answer_selection(game_state, answer_index, switch_screen_callback):
    global transition_timer
    
    state = game_state.exercise_state
    if state.get("answered", False):
        return
    
    question = state["questions"][state["current_question"]]
    state["user_answer"] = answer_index
    state["answered"] = True

    # Kiểm tra đúng/sai
    if answer_index == question["correct_answer"]:
        # Use get() with default value in case points is missing
        points = question.get("points", 10 if state["difficulty"] == "easy" else 
                              15 if state["difficulty"] == "medium" else 20)
        state["score"] += points
        if correct_sound:
            correct_sound.play()
    else:
        if wrong_sound:
            wrong_sound.play()
    
    # Thiết lập timer để tự động chuyển câu
    if transition_timer:
        pygame.time.set_timer(transition_timer, 0)  # Hủy timer cũ nếu có
    
    transition_timer = pygame.USEREVENT + 1  # Sử dụng event ID cao hơn để tránh xung đột
    pygame.time.set_timer(transition_timer, 1500)  # 1.5 giây

def check_timer_event(game_state, switch_screen_callback, event):
    global transition_timer
    
    if event.type == transition_timer:
        pygame.time.set_timer(transition_timer, 0)  # Tắt timer
        transition_timer = None
        
        state = game_state.exercise_state
        if state["current_question"] < len(state["questions"]) - 1:
            state["current_question"] += 1
            state["answered"] = False
            state["user_answer"] = None
        else:
            state["completed"] = True
            show_result(game_state, switch_screen_callback)

def start_exercise_session(game_state, difficulty, switch_screen_callback):
    global exercise_data, transition_timer
    
    if transition_timer:
        pygame.time.set_timer(transition_timer, 0)
        transition_timer = None

    if game_state.energy < 1:
        game_state.purchase_message = "Không đủ năng lượng!"
        game_state.message_timer = time.time()
        return

    if exercise_data is None:
        load_exercise_data()

    questions = exercise_data.get(difficulty, [])
    if not questions:
        game_state.purchase_message = f"Không có câu hỏi {difficulty}!"
        game_state.message_timer = time.time()
        return

    game_state.energy -= 1
    game_state.write_data()

    # Chọn ngẫu nhiên 10 câu hỏi
    selected = random.sample(questions, min(10, len(questions)))
    game_state.exercise_state = {
        "difficulty": difficulty,
        "questions": selected,
        "current_question": 0,
        "score": 0,
        "completed": False,
        "user_answer": None,
        "answered": False,
    }
    switch_screen_callback(config.SCREEN_EXERCISE_QUIZ)

def show_result(game_state, switch_screen_callback):
    state = game_state.exercise_state
    game_state.point += state["score"]
    
    result = f"Hoàn thành! Điểm: {state['score']}"
    game_state.purchase_message = result
    game_state.message_timer = time.time()
    
    switch_screen_callback(config.SCREEN_EXERCISE)