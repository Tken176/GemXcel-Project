# screens/load_screen.py
import pygame
import tkinter as tk
from tkinter import filedialog
import os
import threading
import config
import ui_elements
import math
from .content_processor import ContentProcessor

def choose_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path

def simulate_cmd_questions(filepath, update_status_callback):
    try:
        processor = ContentProcessor()
        
        if not processor.is_supported(filepath):
            update_status_callback("Định dạng file không được hỗ trợ\n" +
                                 f"Chỉ chấp nhận: {', '.join(processor.supported_formats)}")
            return
            
        def processing_task():
            try:
                update_status_callback("Đang xử lý file...")
                success, message = processor.process_file(filepath)
                update_status_callback(message)
            except Exception as e:
                update_status_callback(f"Lỗi hệ thống: {str(e)}")
        
        # Khởi chạy trong thread riêng
        thread = threading.Thread(target=processing_task)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        update_status_callback(f"Lỗi khởi tạo: {str(e)}")

def run(screen, switch_screen, click_sound=None):
    running = True
    clock = pygame.time.Clock()
    
    title_font = pygame.font.Font(config.FONT_PATH, 42)
    subtitle_font = pygame.font.Font(config.FONT_PATH, 24)
    status_font = pygame.font.Font(config.FONT_PATH, 18)
    
    pulse_scale = 1.0
    pulse_direction = 0.003
    time_elapsed = 0
    angle = 0
    
    should_return = [False]
    status_message = ""
    processing = False
    
    def update_status(message):
        nonlocal status_message
        status_message = message
    
    def back_callback():
        nonlocal should_return
        should_return[0] = True
        switch_screen(config.SCREEN_LESSON)
    
    back_button = ui_elements.Button(
        x=40,
        y=530,
        w=160,
        h=60,
        text="Quay lại",
        callback=back_callback,
        color=config.COLORS["button"],
        # hover_color=config.COLORS["hover"],
        # text_color=config.COLORS["text"],
        border_radius=15,
        click_sound=click_sound,
    )

    upload_rect = pygame.Rect(config.WIDTH // 2 - 150, config.HEIGHT // 2 - 100, 300, 200)
    upload_color = config.COLORS["panel"]
    upload_hover_color = config.COLORS["hover"]
    
    upload_text = subtitle_font.render("NHẤN ĐỂ CHỌN FILE", True, (60, 100, 60))

    while running:
        time_elapsed += 1
        angle = (angle + 2) % 360
        screen.fill(config.COLORS["bg"])
        
        # Hiệu ứng pulse
        pulse_scale += pulse_direction
        if pulse_scale > 1.05 or pulse_scale < 0.95:
            pulse_direction *= -1
        
        # Tiêu đề với bóng đổ
        title_text = title_font.render("TẢI LÊN TÀI LIỆU", True, config.COLORS["text"])
        shadow_text = title_font.render("TẢI LÊN TÀI LIỆU", True, (120, 160, 120))
        screen.blit(shadow_text, (config.WIDTH // 2 - shadow_text.get_width() // 2 + 2, 102))
        screen.blit(title_text, (config.WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Phụ đề
        subtitle_text = subtitle_font.render("Chọn file từ thiết bị của bạn để bắt đầu xử lý", True, (90, 130, 90))
        screen.blit(subtitle_text, (config.WIDTH // 2 - subtitle_text.get_width() // 2, 170))
        
        # Nút upload
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = upload_rect.collidepoint(mouse_pos)
        current_color = upload_hover_color if is_hovered else upload_color
        
        scaled_rect = pygame.Rect(
            upload_rect.x - (upload_rect.w * (pulse_scale - 1) / 2),
            upload_rect.y - (upload_rect.h * (pulse_scale - 1) / 2),
            upload_rect.w * pulse_scale,
            upload_rect.h * pulse_scale
        )
        
        pygame.draw.rect(screen, current_color, scaled_rect, border_radius=20)
        pygame.draw.rect(screen, config.COLORS["hover"], scaled_rect, 2, border_radius=20)
        
        if time_elapsed % 30 < 15 and not is_hovered:
            pygame.draw.rect(screen, config.COLORS["hover"], scaled_rect, 2, border_radius=20)
        
        # Biểu tượng upload
        # icon = pygame.font.SysFont("segoe ui emoji", 85).render("📤", True, (255, 255, 255)) [DEBUG]
        icon = pygame.font.SysFont("segoe ui emoji", 85).render("📤", True, (255, 255, 255))
        screen.blit(icon, (config.WIDTH // 2 - 55, config.HEIGHT // 2 - 60))
        screen.blit(upload_text, (config.WIDTH // 2 - upload_text.get_width() // 2, config.HEIGHT // 2 + 50))
        
        # Hiển thị trạng thái
        if status_message:
            # color = (0, 150, 0) if "✅" in status_message else (200, 0, 0) [DEBUG]
            color = (0, 150, 0) if "True" in status_message else (200, 0, 0)
            lines = status_message.split('\n')
            for i, line in enumerate(lines):
                status_line = status_font.render(line, True, color)
                screen.blit(status_line, (config.WIDTH // 2 - status_line.get_width() // 2, 400 + i * 25))
        
        # Hiệu ứng loading khi đang xử lý
        if processing:
            pygame.draw.arc(screen, config.COLORS["hover"], 
                          (config.WIDTH // 2 - 20, 450, 40, 40), 
                          math.radians(angle), math.radians(angle + 270), 3)
        
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            back_button.handle_event(event)
            
            if should_return[0]:
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not back_button.rect.collidepoint(event.pos):
                    if upload_rect.collidepoint(event.pos):
                        if click_sound:
                            click_sound.play()
                        selected_file = choose_file()
                        if selected_file:
                            processing = True
                            simulate_cmd_questions(selected_file, lambda msg: (
                                update_status(msg),
                                setattr(type('obj', (object,), {}), 'processing', False)
                            ))

        pygame.display.flip()
        clock.tick(60)