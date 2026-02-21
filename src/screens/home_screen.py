import pygame
import ui_elements
import config
import os
import json
import tkinter as tk
from tkinter import messagebox

# Đường dẫn file API (cùng cấp với home_screen.py)
BASE_DIR = os.path.dirname(__file__)
API_FILE = os.path.join(BASE_DIR, "API_AI.json")

# Load âm thanh an toàn
try:
    click_sound = pygame.mixer.Sound(os.path.join(config.ASSETS_DIR, "audio", "click.mp3"))
except Exception:
    click_sound = None


def is_valid_api(api_key: str) -> bool:
    """Kiểm tra API Gemini hợp lệ (sơ bộ)"""
    if not isinstance(api_key, str):
        return False
    api_key = api_key.strip()
    return api_key.startswith("AI") and len(api_key) > 20


def load_api_key():
    """Đọc API từ file JSON và kiểm tra hợp lệ"""
    if not os.path.exists(API_FILE):
        return None
    try:
        with open(API_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            api_key = data.get("API")
            if is_valid_api(api_key):
                return api_key.strip()
            return None
    except Exception:
        return None


def save_api_key(api_key):
    """Lưu API vào file JSON (ngay trong thư mục screens/)"""
    with open(API_FILE, "w", encoding="utf-8") as f:
        json.dump({"API": api_key}, f, ensure_ascii=False, indent=4)
        f.flush()
        os.fsync(f.fileno())
    print(f"API đã được lưu vào: {os.path.abspath(API_FILE)}")


def open_api_window():
    """Mở cửa sổ nhập API key"""
    def save_and_close():
        api_value = entry.get().strip()
        if is_valid_api(api_value):
            save_api_key(api_value)
            messagebox.showinfo("Thành công", f"API đã được lưu!\nĐường dẫn: {os.path.abspath(API_FILE)}")
            root.destroy()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập API hợp lệ!")

    root = tk.Tk()
    root.title("Nhập API Gemini Free")

    label = tk.Label(root, text=(
        "Bạn chưa có API!\n\n"
        "Hướng dẫn lấy API Gemini Free:\n"
        "1. Vào https://aistudio.google.com/app/apikey\n"
        "2. Đăng nhập bằng tài khoản Google.\n"
        "3. Copy API Key và dán vào ô bên dưới."
    ), justify="left", padx=10, pady=10)
    label.pack()

    entry = tk.Entry(root, width=50)
    entry.pack(pady=5)

    btn_save = tk.Button(root, text="Lưu API", command=save_and_close)
    btn_save.pack(pady=10)

    root.mainloop()


def draw_home(screen, game_state, switch_screen_callback):
    # Vẽ nền
    try:
        image_bg = pygame.image.load(os.path.join(config.ASSETS_DIR, "setting", "back.png"))
        image_bg = pygame.transform.scale(image_bg, (960, 640))
        screen.blit(image_bg, (0, 0))
    except Exception:
        screen.fill((200, 200, 200))

    # Vẽ tiêu đề
    try:
        image = pygame.image.load(os.path.join(config.ASSETS_DIR, "setting", "home_logo.png"))
        image = pygame.transform.scale(image, (850, 370))
        screen.blit(image, (70, 50))
    except Exception:
        pass

    # Resource button
    try:
        button_img = pygame.image.load(os.path.join(config.ASSETS_DIR, "setting", "button.png"))
        button_img = pygame.transform.scale(button_img, (196, 94))
        button_hover_img = pygame.image.load(os.path.join(config.ASSETS_DIR, "setting", "hover_button.png"))
        button_hover_img = pygame.transform.scale(button_hover_img, (196, 94))
    except Exception:
        return

    button_x, button_y = 390, 450
    button_rect = button_img.get_rect(topleft=(button_x, button_y))

    # Kiểm tra API
    api_key = load_api_key()

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    if button_rect.collidepoint(mouse_pos):
        screen.blit(button_hover_img, button_rect)
        if mouse_click[0]:
            if click_sound:
                click_sound.play()
            if api_key:
                # API hợp lệ -> vào bài học
                switch_screen_callback(config.SCREEN_LESSON)
            else:
                # Nếu không có hoặc API sai định dạng
                open_api_window()
                api_key_new = load_api_key()
                if api_key_new:
                    switch_screen_callback(config.SCREEN_LESSON)
                else:
                    game_state.show_message("Vui lòng nhập API hợp lệ!")
    else:
        screen.blit(button_img, button_rect)

    pygame.display.flip()
