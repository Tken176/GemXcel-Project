import pygame
import sys
import time
import threading
import subprocess
import pkg_resources
import os
import json
import config
# Chạy migration và đảm bảo data directories tồn tại khi khởi động
def initialize_app():
    """Khởi tạo ứng dụng và migrate data nếu cần"""
    
    # Migration data từ phiên bản cũ (nếu có)
    config.migrate_old_data()
    
    # Đảm bảo thư mục data tồn tại
    config.ensure_data_directories()
    

# Gọi hàm này trước khi khởi tạo GameState hoặc bất kỳ class nào khác
if __name__ == "__main__":
    initialize_app()


# === KHỞI TẠO BAN ĐẦU ===
pygame.init()

# Import các modules từ src

from game_state import GameState
import ui_elements
import quiz_data as quiz_data_module
import screens.home_screen
import screens.lesson_screen
import screens.shop_screen
import screens.account_screen
import screens.collection_screen
import screens.knowledge_page_screen
from screens.quiz_screen import draw_quiz_screen, set_sounds, check_answer_mcq, finish_quiz_session, next_quiz_question
import screens.exercise_screen
from config import SCREEN_EXERCISE, SCREEN_EXERCISE_QUIZ
import screens.setting_screen
import screens.load_screen as load_screen


# ===Âm thanh ===
pygame.mixer.init()

# Âm thanh nhấn nút - DI CHUYỂN LÊN TRƯỚC
click_sound = pygame.mixer.Sound(os.path.join(config.ASSETS_DIR, "audio", "click.mp3"))

# Sau đó mới gọi set_click_sound
screens.exercise_screen.set_click_sound(click_sound)

# Sau phần khởi tạo click_sound trong main.py
correct_sound = pygame.mixer.Sound(config.SOUND_CORRECT_PATH)
wrong_sound = pygame.mixer.Sound(config.SOUND_WRONG_PATH)

# Truyền các âm thanh vào các màn hình cần thiết
screens.quiz_screen.set_sounds(correct_sound, wrong_sound)
screens.exercise_screen.set_sounds(correct_sound, wrong_sound)

# Mở nhạc nền
pygame.mixer.music.load(os.path.join(config.ASSETS_DIR, "audio", "bg.mp3"))
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# Cấu hình màn hình
SCREEN = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("GEMXCEL")

icon_path = os.path.join("icon.ico")  
icon = pygame.image.load(icon_path)
# Set icon cho cửa sổ
pygame.display.set_icon(icon)

# Khởi tạo trạng thái game
game_state = GameState(file_path=config.DATA_FILE_PATH)

# Biến toàn cục
current_screen = game_state.current_screen
active_buttons = []
last_click_time = 0

def switch_screen(screen_name):
    global current_screen
    game_state.current_screen = screen_name
    current_screen = screen_name

def handle_button_click(callback_function, *args):
    # Bỏ qua kiểm tra thời gian nếu là sự kiện quiz
    if "quiz" in str(callback_function).lower():
        callback_function(*args)
    else:
        global last_click_time
        current_time = time.time()
        if current_time - last_click_time > 0.1:  # Giảm từ 0.3s xuống 0.1s
            callback_function(*args)
            last_click_time = current_time

def get_current_screen_buttons(current_screen_name, game_state, switch_screen_callback, handle_button_click_callback):
    buttons = []
    
    # Menu buttons
    if current_screen_name != config.SCREEN_EXERCISE and current_screen_name != config.SCREEN_EXERCISE_QUIZ:
        buttons.extend([
            ui_elements.Button(0, 120, 190, 90, "Bài học", 
                lambda: switch_screen_callback(config.SCREEN_LESSON),
                click_sound=click_sound),
            ui_elements.Button(0, 200, 190, 90, "Cửa hàng", 
                lambda: switch_screen_callback(config.SCREEN_SHOP),
                click_sound=click_sound),
            ui_elements.Button(0, 280, 190, 90, "Tài khoản", 
                lambda: switch_screen_callback(config.SCREEN_ACCOUNT),
                click_sound=click_sound),
            ui_elements.Button(0, 360, 190, 90, "Bộ sưu tập", 
                lambda: switch_screen_callback(config.SCREEN_COLLECTION),
                click_sound=click_sound),
        ])

    if current_screen_name == config.SCREEN_LESSON:
        quiz_file_exists = os.path.exists(config.QUIZ_DATA_FILE_PATH)

        # Thêm nút "Bài tập" chỉ khi có quiz.json
        if quiz_file_exists:
            buttons.append(ui_elements.Button(
                x=config.WIDTH - 170,
                y=20,
                w=130,
                h=50,
                text="Bài tập",
                callback=lambda: switch_screen_callback(config.SCREEN_EXERCISE),
                color=config.COLORS["button"],
                border_radius=10,
                click_sound=click_sound
            ))

        # Thêm nút "NẠP FILE" với vị trí thay đổi tùy điều kiện
        load_file_btn_x = config.WIDTH - 320 if quiz_file_exists else config.WIDTH - 470
        load_file_btn_y = 20 if quiz_file_exists else 270  
        load_file_btn_w = 130 if quiz_file_exists else 200
        load_file_btn_h = 50 if quiz_file_exists else 80

        buttons.append(ui_elements.Button(
            x=load_file_btn_x,
            y=load_file_btn_y,
            w=load_file_btn_w,
            h=load_file_btn_h,
            text="NẠP FILE",
            callback=lambda: switch_screen_callback(config.SCREEN_LOAD),
            color=config.COLORS["button"],
            border_radius=10,
            click_sound=click_sound
        ))
        
        lessons = screens.lesson_screen.load_lessons_data()
        if lessons:  # Chỉ thêm nút nếu có dữ liệu bài học
            for index, lesson in enumerate(lessons):
                x_position, y_position = 240, 100 + index * 100
                lesson_id = index + 1
                button = ui_elements.Button(
                    x_position, y_position, 680, 90, "",
                    lambda lesson_id=lesson_id: switch_screen_callback(config.SCREEN_KNOWLEDGE_PAGE) if game_state.start_lesson(lesson_id) else None,
                    config.COLORS["white"],
                    click_sound=click_sound
                )
                buttons.append(button)
    
    elif current_screen_name == config.SCREEN_EXERCISE:
        buttons.extend(screens.exercise_screen.draw_exercise(SCREEN, game_state, switch_screen) or [])
    elif current_screen_name == config.SCREEN_SHOP:
        for index, item in enumerate(screens.shop_screen.shop_items):
            col = index % 2
            row = index // 2
            x_position = 190 + 50 + col * 300  # 190px menu + padding 50px
            y_position = 120 + row * 180
            buttons.append(ui_elements.Button(
                x_position, y_position, 280, 160, "",
                lambda item_name=item["name"], price=item["price"]: game_state.purchase_item(item_name, price),
                config.COLORS["white"],
                click_sound=click_sound
            ))
        
    elif current_screen_name == config.SCREEN_COLLECTION:
        if game_state.viewing_gem is not None:
            buttons.append(ui_elements.Button(
                220, 570, 150, 60, "Quay lại",
                lambda: screens.collection_screen.set_viewing_gem_to_none(game_state),
                click_sound=click_sound
            ))
    
    elif current_screen_name == config.SCREEN_KNOWLEDGE_PAGE:
        lesson_id = game_state.current_lesson_id
        page_index = game_state.current_page_index
        
        # Nút "Trước"
        if page_index > 0:
            buttons.append(ui_elements.Button(
                config.WIDTH//2 - 150,
                config.HEIGHT - 60,
                100,
                50,
                "Trước",
                lambda: handle_button_click_callback(game_state.goto_prev_page),
                config.COLORS["button"],
                click_sound=click_sound
            ))

        # Nút "Tiếp"
        if hasattr(game_state, "lesson_pages") and page_index < len(game_state.lesson_pages) - 1:
            buttons.append(ui_elements.Button(
                config.WIDTH//2 + 50,
                config.HEIGHT - 60,
                100,
                50,
                "Tiếp",
                lambda: handle_button_click_callback(game_state.goto_next_page),
                config.COLORS["button"],
                click_sound=click_sound
            ))

        else:
            buttons.append(ui_elements.Button(
                config.WIDTH//2 + 50,
                config.HEIGHT - 60, 
                100, 
                50, 
                "Bài tập",
                lambda: handle_button_click_callback(
                    screens.knowledge_page_screen.finish_lesson_and_start_quiz, 
                    game_state, 
                    lesson_id, 
                    switch_screen_callback
                ),
                config.COLORS["accent"],
                click_sound=click_sound
            ))

    elif current_screen_name == config.SCREEN_QUIZ_SCREEN:
        buttons = draw_quiz_screen(
            SCREEN,
            config.FONT_TITLE,
            config.FONT,
            config.FONT_SMALL,
            config.COLORS,
            game_state,
            handle_button_click,
            quiz_data_module.quiz_data
        ) or []

    return buttons  # Đảm bảo luôn trả về danh sách

# Khởi tạo các luồng cập nhật nền
threading.Thread(target=game_state.update_energy_thread, daemon=True).start()
threading.Thread(target=game_state.update_point_thread, daemon=True).start()
threading.Thread(target=game_state.update_streak_thread, daemon=True).start()

# Nút cài đặt hình tròn
setting_button = ui_elements.CircleButton(
    150, 60, 25,
    lambda: switch_screen(config.SCREEN_SETTING),
    config.COLORS["button"],
    hover_color=config.COLORS["hover"],
    click_sound=click_sound
)

# --- Vòng lặp chính ---
running = True
while running:
    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT + 1:  # Kiểm tra timer chuyển câu
            screens.exercise_screen.check_timer_event(game_state, switch_screen, event)
        if event.type == pygame.USEREVENT and hasattr(event, 'force_redraw'):
            pygame.display.flip()
        if event.type == pygame.USEREVENT + 2: 
            importlib.reload(quiz_data_module)
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))
        # Cập nhật active_buttons với giá trị mặc định là []
        if game_state.current_screen == config.SCREEN_SETTING:
            if hasattr(game_state, 'temp_screen') and game_state.temp_screen == "avatar_selection":
                active_buttons = screens.setting_screen.draw_avatar_selection(
                    screen=SCREEN,
                    game_state=game_state,
                    click_sound=click_sound
                ) or []
            else:
                active_buttons = screens.setting_screen.draw_setting(
                    screen=SCREEN,
                    game_state=game_state,
                    click_sound=click_sound
                ) or []
        else:
            active_buttons = get_current_screen_buttons(
                game_state.current_screen, 
                game_state, 
                switch_screen, 
                handle_button_click
            ) or []

        # Xử lý sự kiện cho các nút (chỉ khi active_buttons không rỗng)
        for button in active_buttons:
            button.handle_event(event)
        setting_button.handle_event(event)

        if game_state.current_screen == config.SCREEN_EXERCISE_QUIZ:
            active_buttons = screens.exercise_screen.draw_exercise_quiz(SCREEN, game_state, switch_screen) or []
            for button in active_buttons:
                button.handle_event(event)

        if game_state.current_screen == config.SCREEN_COLLECTION and event.type == pygame.MOUSEBUTTONDOWN:
            if game_state.viewing_gem is None and not game_state.just_closed_detail:
                for gem in config.GEM_TYPES:
                    if "rect" in gem and gem["rect"].collidepoint(event.pos):
                        if any(g["id"] == gem["id"] for g in game_state.collected_gems):
                            game_state.viewing_gem = gem
            if game_state.just_closed_detail:
                game_state.just_closed_detail = False

    # Vẽ màn hình
    SCREEN.fill(config.COLORS["bg"])

    if game_state.current_screen != config.SCREEN_EXERCISE and game_state.current_screen != config.SCREEN_EXERCISE_QUIZ:
        pygame.draw.rect(SCREEN, config.COLORS["panel"], (0, 0, 190, config.HEIGHT))
        
        # AVATAR và nút cài đặt
        try:
            avatar_img = pygame.image.load(game_state.avatar_path)
            avatar_img = pygame.transform.scale(avatar_img, (100, 100))
            SCREEN.blit(avatar_img, (15, 10))
        except:
            pygame.draw.circle(SCREEN, config.COLORS["accent"], (65, 60), 50)

        setting_button.draw(SCREEN)
        setting_icon = pygame.image.load(os.path.join(config.ASSETS_DIR, "setting", "setting_icon.png"))
        setting_icon = pygame.transform.scale(setting_icon, (40, 40))
        SCREEN.blit(setting_icon, (130,42))

        main_1 = f"Điểm: {game_state.point}"
        main_2 = f"Năng lượng: {game_state.energy}"
        main_text_1 = config.FONT.render(main_1, True, config.COLORS["text"])
        main_text_2 = config.FONT.render(main_2, True, config.COLORS["text"])
        SCREEN.blit(main_text_1, (15, config.HEIGHT - 100))
        SCREEN.blit(main_text_2, (15, config.HEIGHT - 150))

    # Vẽ các nút (chỉ khi active_buttons không rỗng)
    for button in active_buttons:
        button.draw(SCREEN)

    # Vẽ nội dung màn hình hiện tại
    if game_state.current_screen == config.SCREEN_HOME:
        screens.home_screen.draw_home(SCREEN, game_state, switch_screen)
    elif game_state.current_screen == config.SCREEN_LESSON:
        screens.lesson_screen.draw_lesson(SCREEN, config.FONT_PATH, config.FONT_TITLE, config.FONT, config.COLORS, game_state, switch_screen, handle_button_click)
    elif game_state.current_screen == config.SCREEN_EXERCISE:
        screens.exercise_screen.draw_exercise(SCREEN, game_state, switch_screen)
    elif game_state.current_screen == config.SCREEN_SETTING:
        if hasattr(game_state, 'temp_screen') and game_state.temp_screen == "avatar_selection":
            screens.setting_screen.draw_avatar_selection(
                screen=SCREEN,
                game_state=game_state,
                click_sound=click_sound
            )
        else:
            screens.setting_screen.draw_setting(
                screen=SCREEN,
                game_state=game_state,
                click_sound=click_sound
            )
    elif game_state.current_screen == config.SCREEN_SHOP:
        screens.shop_screen.draw_shop(SCREEN, config.FONT_TITLE, config.FONT, config.COLORS, game_state, handle_button_click, screens.shop_screen.shop_items)
    elif game_state.current_screen == config.SCREEN_ACCOUNT:
        screens.account_screen.draw_account(SCREEN, config.FONT_TITLE, config.FONT, config.COLORS, game_state)
    elif game_state.current_screen == config.SCREEN_COLLECTION:
        screens.collection_screen.draw_collection(SCREEN, config.FONT_TITLE, config.FONT, config.FONT_SMALL, config.COLORS, config.GEM_TYPES, game_state, handle_button_click, ui_elements.draw_multiline_text)
    elif game_state.current_screen == config.SCREEN_KNOWLEDGE_PAGE:
        screens.knowledge_page_screen.draw_knowledge_page(
            SCREEN,
            config.FONT_TITLE,
            config.FONT,
            config.COLORS,
            game_state,
            handle_button_click,
            switch_screen
        )
    elif game_state.current_screen == config.SCREEN_QUIZ_SCREEN:
        draw_quiz_screen(
            SCREEN,
            config.FONT_TITLE,
            config.FONT,
            config.FONT_SMALL,
            config.COLORS,
            game_state,
            handle_button_click,
            quiz_data_module.quiz_data
        )
    elif game_state.current_screen == config.SCREEN_LOAD:
        result = load_screen.run(SCREEN, switch_screen, click_sound)
        if result == "quit":
            running = False

    elif game_state.current_screen == config.SCREEN_EXERCISE_QUIZ:
        if not hasattr(game_state, 'exercise_state') or game_state.exercise_state is None:
            switch_screen(config.SCREEN_EXERCISE)
        else:
            active_buttons = screens.exercise_screen.draw_exercise_quiz(SCREEN, game_state, switch_screen) or []
    
    if game_state.purchase_message and time.time() - game_state.message_timer < 3:
        ui_elements.draw_message(SCREEN, game_state.purchase_message, config.FONT, config.COLORS, config.WIDTH, config.HEIGHT)

    pygame.display.flip()

game_state.write_data()
pygame.quit()
sys.exit()