import pygame
import sys
import time
import threading
import subprocess
#import pkg_resources
import os
import json
import config

# ===== QUAN TRỌNG: Hàm lấy đường dẫn resource cho --onefile =====
def get_resource_path(relative_path):
    """
    Lấy đường dẫn đúng đến resource file
    Đặc biệt quan trọng khi sử dụng PyInstaller --onefile
    """
    try:
        # PyInstaller với --onefile tạo thư mục tạm _MEIPASS
        # Tất cả resources được giải nén vào đây khi chạy
        base_path = sys._MEIPASS
        print(f"🔍 Running from PyInstaller, base: {base_path}")
    except AttributeError:
        # Khi chạy ở chế độ development (python main.py)
        base_path = os.path.abspath(".")
        print(f"🔍 Running in development mode, base: {base_path}")
    
    full_path = os.path.join(base_path, relative_path)
    print(f"🔍 Looking for {relative_path} at: {full_path}")
    
    return full_path

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

# === Âm thanh ===
pygame.mixer.init()

# Âm thanh nhấn nút
click_sound = pygame.mixer.Sound(os.path.join(config.ASSETS_DIR, "audio", "click.mp3"))

# Sau đó mới gọi set_click_sound
screens.exercise_screen.set_click_sound(click_sound)
screens.lesson_screen.set_click_sound(click_sound)

# Âm thanh đúng/sai
correct_sound = pygame.mixer.Sound(config.SOUND_CORRECT_PATH)
wrong_sound = pygame.mixer.Sound(config.SOUND_WRONG_PATH)

# Truyền các âm thanh vào các màn hình cần thiết
screens.quiz_screen.set_sounds(correct_sound, wrong_sound)
screens.exercise_screen.set_sounds(correct_sound, wrong_sound)

# Cấu hình màn hình
SCREEN = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("GEMXCEL")
screens.shop_screen.load_item_images()  

# ===== LOAD ICON SỬ DỤNG get_resource_path() =====
icon_path = get_resource_path("icon.ico")
if os.path.exists(icon_path):
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)
else:
    print(f"⚠️ Warning: Icon not found at {icon_path}")

# Khởi tạo trạng thái game
game_state = GameState(file_path=config.DATA_FILE_PATH)
# ===== PHÁT NHẠC NỀN KHI KHỞI ĐỘNG =====
music_path = os.path.join(config.ASSETS_DIR, "audio", game_state.current_music)

if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(game_state.music_volume)
    pygame.mixer.music.play(-1)  # lặp vô hạn
else:
    print("Không tìm thấy file nhạc:", music_path)

# Biến toàn cục
current_screen = game_state.current_screen
active_buttons = []
last_click_time = 0

def switch_screen(screen_name):
    global current_screen
    game_state.current_screen = screen_name
    current_screen = screen_name

def handle_button_click(callback_function, *args):
    global last_click_time
    now = time.time()
    if now - last_click_time > 0.2:  # chặn spam click 200ms
        callback_function(*args)
        last_click_time = now

def normal(name, size=None):
    path=os.path.join(config.ASSETS_DIR,"setting", f"{name}")
    image=pygame.image.load(path).convert_alpha()
    if size:
        image=pygame.transform.scale(image,size)
    return image

def hover(name,size=None):
    path=os.path.join(config.ASSETS_DIR,"setting", f"{name}")
    image=pygame.image.load(path).convert_alpha()
    if size:
        image=pygame.transform.scale(image,size)
    return image

def get_current_screen_buttons(current_screen_name, game_state, switch_screen_callback, handle_button_click_callback):    
    # Menu buttons
    buttons=[]
    if current_screen_name != config.SCREEN_EXERCISE and current_screen_name != config.SCREEN_EXERCISE_QUIZ:
        buttons.extend([
            ui_elements.RecButton(-3,120, normal("bai_hoc.png",(75,47)), hover("bai_hoc_hover.png",(75,47)),
            lambda: switch_screen_callback(config.SCREEN_LESSON),
            click_sound=click_sound),
            ui_elements.RecButton(-3,220,normal("cua_hang.png",(75,47)), hover("cua_hang_hover.png",(74,47)),
            lambda: switch_screen_callback(config.SCREEN_SHOP),
            click_sound=click_sound),
            ui_elements.RecButton(-3,320, normal("tai_khoan.png",(75,47)), hover("tai_khoan_hover.png",(75,47)),
            lambda: switch_screen_callback(config.SCREEN_ACCOUNT),
            click_sound=click_sound),
            ui_elements.RecButton(-3,420,normal("bo_suu_tap.png",(75,47)), hover("bo_suu_tap_hover.png",(75,47)),
            lambda: switch_screen_callback(config.SCREEN_COLLECTION),
            click_sound=click_sound)
        ])

    if current_screen_name == config.SCREEN_LESSON and game_state.current_screen != config.SCREEN_KNOWLEDGE_PAGE:
        quiz_file_exists = os.path.exists(config.QUIZ_DATA_FILE_PATH)

        if quiz_file_exists:
            buttons.append(ui_elements.Button(
                x=config.WIDTH - 240,
                y=530,
                w=130,
                h=50,
                text="Bài tập",
                callback=lambda: switch_screen_callback(config.SCREEN_EXERCISE),
                color=config.COLORS["text"],
                border_radius=10,
                click_sound=click_sound
            ))

        load_file_btn_x = config.WIDTH - 315 if quiz_file_exists else config.WIDTH - 370
        load_file_btn_y = 42 if quiz_file_exists else 320  
        load_file_btn_w = 130 if quiz_file_exists else 200
        load_file_btn_h = 50 if quiz_file_exists else 80

        buttons.append(ui_elements.Button(
            x=load_file_btn_x,
            y=load_file_btn_y,
            w=load_file_btn_w,
            h=load_file_btn_h,
            text="NẠP FILE",
            callback=lambda: switch_screen_callback(config.SCREEN_LOAD),
            color=config.COLORS["text"],
            border_radius=10,
            click_sound=click_sound
        ))
        
        lessons = screens.lesson_screen.load_lessons_data()
        if lessons:
            for index, lesson in enumerate(lessons):
                x_position, y_position = 240, 100 + index * 100
                lesson_id = index + 1
                button = ui_elements.TextButton(
                    x_position, y_position, "",
                    lambda lesson_id=lesson_id: switch_screen_callback(config.SCREEN_KNOWLEDGE_PAGE) if game_state.start_lesson(lesson_id) else None
                    ,click_sound=click_sound
                )
                buttons.append(button)
    
    elif current_screen_name == config.SCREEN_EXERCISE:
        buttons.extend(screens.exercise_screen.draw_exercise(SCREEN, game_state, switch_screen) or [])
    elif current_screen_name == config.SCREEN_SHOP:
        screens.shop_screen.item_rects = []
        item_width, item_height = 300, 170
        item_margin = 130
        items_per_row = 2
        start_x = 110
        start_y = 120

        for index, item in enumerate(screens.shop_screen.shop_items):
            col = index % items_per_row
            row = index // items_per_row
            x_position = start_x + col * (item_width + item_margin)
            y_position = start_y + row * (item_height - 50)
            shrink = 83
            rect = pygame.Rect(
                x_position, 
                y_position,
                item_width, 
                item_height - shrink
            )
            screens.shop_screen.item_rects.append({
                "rect": rect,
                "name": item["name"],
                "price": item["price"]
            })
        
    elif current_screen_name == config.SCREEN_COLLECTION:
        if game_state.viewing_gem is not None:
            buttons.append(ui_elements.Button(
                550, 140, 40, 40, "<",
                lambda: screens.collection_screen.set_viewing_gem_to_none(game_state),
                click_sound=click_sound
            ))
    
    elif current_screen_name == config.SCREEN_KNOWLEDGE_PAGE:
        lesson_id = game_state.current_lesson_id
        spread_index = game_state.current_page_index

        if spread_index > 0:
            buttons.append(ui_elements.Button(
                config.WIDTH//2 - 150,
                config.HEIGHT - 110,
                100,
                50,
                "Trước",
                lambda: handle_button_click_callback(game_state.goto_prev_page),
                config.COLORS["text"],
                click_sound=click_sound
            ))

        if hasattr(game_state, "lesson_spreads") and spread_index < len(game_state.lesson_spreads) - 1:
            buttons.append(ui_elements.Button(
                config.WIDTH//2 + 50,
                config.HEIGHT - 110,
                100,
                50,
                "Tiếp",
                lambda: handle_button_click_callback(game_state.goto_next_page),
                config.COLORS["text"],
                click_sound=click_sound
            ))
        else:
            buttons.append(ui_elements.Button(
                config.WIDTH//2 + 50,
                config.HEIGHT - 110, 
                100, 
                50, 
                "Bài tập",
                lambda: handle_button_click_callback(
                    screens.knowledge_page_screen.finish_lesson_and_start_quiz, 
                    game_state, 
                    lesson_id, 
                    switch_screen_callback
                ),
                config.COLORS["text"],
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

    return buttons

# Khởi tạo các luồng cập nhật nền
threading.Thread(target=game_state.update_energy_thread, daemon=True).start()
threading.Thread(target=game_state.update_point_thread, daemon=True).start()
threading.Thread(target=game_state.update_streak_thread, daemon=True).start()

# Nút cài đặt hình tròn
setting_button = ui_elements.CircleButton(
    829, 67, 25,
    lambda: switch_screen(config.SCREEN_SETTING),
    config.COLORS["text"],
    hover_color=config.COLORS["text_hover"],
    click_sound=click_sound
)

# --- Vòng lặp chính ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state.current_screen == config.SCREEN_LESSON:
                if screens.lesson_screen.handle_lesson_click(event.pos, game_state, switch_screen):
                    continue
            mouse_pos = pygame.mouse.get_pos()
            if game_state.current_screen == config.SCREEN_SHOP:
                for item_info in screens.shop_screen.item_rects:
                    if item_info["rect"].collidepoint(mouse_pos):
                        game_state.purchase_item(item_info["name"], item_info["price"])
        if event.type == pygame.USEREVENT + 1:
            screens.exercise_screen.check_timer_event(game_state, switch_screen, event)
        if event.type == pygame.USEREVENT and hasattr(event, 'force_redraw'):
            pygame.display.flip()
        if event.type == pygame.USEREVENT + 2: 
            importlib.reload(quiz_data_module)
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'force_redraw': True}))
            
        if game_state.current_screen == config.SCREEN_SETTING:
            if hasattr(game_state, 'temp_screen') and game_state.temp_screen == "avatar_selection":
                active_buttons = screens.setting_screen.draw_avatar_selection(
                    screen=SCREEN,
                    game_state=game_state,
                    click_sound=click_sound
                ) or []
            elif hasattr(game_state, 'temp_screen') and game_state.temp_screen == "music_selection":
                active_buttons = screens.setting_screen.draw_music_selection(
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
    background = os.path.join(config.ASSETS_DIR, "setting", "background.png")
    back_bg = pygame.image.load(background)
    back_bg = pygame.transform.scale(back_bg, (960, 640))  
    SCREEN.blit(back_bg, (0, 0))

    if game_state.current_screen != config.SCREEN_EXERCISE and game_state.current_screen != config.SCREEN_EXERCISE_QUIZ and game_state.current_screen != config.SCREEN_KNOWLEDGE_PAGE:
        setting_button.draw(SCREEN)
        setting_icon = pygame.image.load(os.path.join(config.ASSETS_DIR, "setting", "setting_icon.png"))
        setting_icon = pygame.transform.scale(setting_icon, (40, 40))
        SCREEN.blit(setting_icon, (810,50))
        if game_state.current_screen not in (config.SCREEN_ACCOUNT, config.SCREEN_SETTING, config.SCREEN_EXERCISE, config.SCREEN_EXERCISE_QUIZ):
            try:
                avatar_img = pygame.image.load(game_state.avatar_path)
                avatar_img = pygame.transform.scale(avatar_img, (100, 100))
                SCREEN.blit(avatar_img, (320, 470))
            except:
                pygame.draw.circle(SCREEN, config.COLORS["accent"], (65, 60), 50)
            
            main_1 = f"Điểm: {game_state.point}"
            main_2 = f"Năng lượng: {game_state.energy}"
            main_text_1 = config.FONT.render(main_1, True, config.COLORS["text"])
            main_text_2 = config.FONT.render(main_2, True, config.COLORS["text"])
            SCREEN.blit(main_text_1, (80, config.HEIGHT - 110))
            SCREEN.blit(main_text_2, (80, config.HEIGHT - 150))

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