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

    # Background với màu xanh lá nhạt (235, 255, 235)
    screen.fill((235, 255, 235))
    
    # Các yếu tố trang trí
    for i in range(15):
        x = random.randint(0, config.WIDTH)
        y = random.randint(0, config.HEIGHT)
        size = random.randint(5, 20)
        alpha = random.randint(30, 80)
        leaf_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(leaf_surf, (200, 240, 200, alpha), (size, size), size)
        screen.blit(leaf_surf, (x, y))

    # Header với gradient
    header = pygame.Surface((config.WIDTH, 180))
    for y in range(180):
        color = (180 - y//3, 220 - y//4, 180 - y//6)
        pygame.draw.line(header, color, (0, y), (config.WIDTH, y))
    screen.blit(header, (0, 0))

    # Tiêu đề với bóng đổ
    title = config.FONT_TITLE.render("CHỌN CẤP ĐỘ", True, (255, 255, 255))
    shadow = config.FONT_TITLE.render("CHỌN CẤP ĐỘ", True, (100, 150, 100))
    screen.blit(shadow, (config.WIDTH//2 - title.get_width()//2 + 3, 93))
    screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 90))

    # Nút quay lại
    back_button = ui_elements.Button(
        x=30, y=30, w=120, h=50,
        text="Quay lại",
        callback=lambda: switch_screen_callback(config.SCREEN_LESSON),
        color=(200, 230, 200),
        border_radius=25,
        click_sound=click_sound
    )

    # Các mức độ khó
    difficulty_levels = [
        {"name": "DỄ", "desc": "10 điểm/câu", "diff": "easy", "color": (100, 200, 100)},
        {"name": "TRUNG BÌNH", "desc": "15 điểm/câu", "diff": "medium", "color": (255, 180, 50)},
        {"name": "KHÓ", "desc": "20 điểm/câu", "diff": "hard", "color": (255, 100, 100)},
    ]

    buttons = [back_button]
    card_y = 180
    for level in difficulty_levels:
        # Nền card
        draw_rounded_rect(screen, (255, 255, 255), (50, card_y, config.WIDTH-100, 120), 25, 2, (220, 220, 220))
        
        # Vẽ icon
        draw_icon(screen, level["diff"], 90, card_y + 50)
        
        # Nút độ khó
        btn = ui_elements.Button(
            x=120, y=card_y+20, w=config.WIDTH-170, h=60,
            text=level["name"],
            callback=create_difficulty_callback(level["diff"], game_state, switch_screen_callback),
            color=level["color"],
            border_radius=30,
            click_sound=click_sound
        )
        buttons.append(btn)
        
        # Mô tả
        desc = config.FONT_SMALL.render(level["desc"], True, (100, 100, 100))
        screen.blit(desc, (config.WIDTH//2 - desc.get_width()//2, card_y+90))
        
        card_y += 140

    # Hiển thị năng lượng
    energy_text = config.FONT_SMALL.render(f"Năng lượng: {game_state.energy}", True, (80, 120, 80))
    screen.blit(energy_text, (config.WIDTH - energy_text.get_width() - 30, 40))

    # Vẽ tất cả nút
    for button in buttons:
        button.draw(screen)

    return buttons

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

    # Nền với pattern
    screen.fill((235, 255, 235))
    for i in range(50):
        x = random.randint(0, config.WIDTH)
        y = random.randint(0, config.HEIGHT)
        size = random.randint(2, 8)
        alpha = random.randint(10, 30)
        dot_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (200, 230, 200, alpha), (size, size), size)
        screen.blit(dot_surf, (x, y))

    # Thanh tiến trình
    progress = (exercise_state["current_question"] + 1) / len(exercise_state["questions"])
    pygame.draw.rect(screen, (220, 220, 220), (50, 50, config.WIDTH-100, 12), border_radius=6)
    pygame.draw.rect(screen, (100, 180, 100), (50, 50, int((config.WIDTH-100) * progress), 12), border_radius=6)
    
    # Đếm câu hỏi
    counter = config.FONT_SMALL.render(f"Câu {exercise_state['current_question']+1}/{len(exercise_state['questions'])}", True, (80, 120, 80))
    screen.blit(counter, (config.WIDTH - counter.get_width() - 60, 45))

    # Card câu hỏi
    draw_rounded_rect(screen, (255, 255, 255), (40, 90, config.WIDTH-80, 160), 20, 2, (220, 220, 220))
    
    # Văn bản câu hỏi
    question_lines = ui_elements.draw_multiline_text(
        screen, current_question["question"],
        60, 110, config.FONT, (70, 70, 70), config.WIDTH-120
    )

    # Các lựa chọn
    y_pos = 270
    max_height = config.HEIGHT - 50  # Giới hạn chiều cao tối đa
    choice_count = len(current_question["choices"])
    choice_height = min(70, (max_height - y_pos) // max(choice_count, 1))
    
    for idx, choice in enumerate(current_question["choices"]):
        # Xác định màu nút
        if exercise_state.get("answered", False):
            if idx == current_question["correct_answer"]:
                color = (100, 200, 100)  # Xanh cho đúng
            elif idx == exercise_state.get("user_answer"):
                color = (255, 120, 120)  # Đỏ cho sai
            else:
                color = (220, 220, 220)  # Xám cho các lựa chọn khác
        else:
            color = (200, 230, 200)  # Màu xanh lá nhạt mặc định
            
        btn = ui_elements.Button(
            50, y_pos, config.WIDTH-100, choice_height - 10,
            choice, 
            lambda i=idx: handle_answer_selection(game_state, i, switch_screen_callback),
            color, 15, click_sound
        )
        buttons.append(btn)
        y_pos += choice_height

    # Vẽ tất cả nút
    for button in buttons:
        button.draw(screen)

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

    # Chọn ngẫu nhiên 5 câu hỏi
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