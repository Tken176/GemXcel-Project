import pygame
import os
import config
from pygame import mixer
import subprocess
import sys
import time
import math
from typing import List, Dict, Tuple, Optional, Callable
import ui_elements
import threading

# Animation variables
animation_time = 0
hover_states = {}

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import threading
from g4f.client import Client
from g4f.models import gpt_4o_mini


class ChatbotApp:
    def __init__(self):
        try:
            # Cấu hình CustomTkinter
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # Tạo cửa sổ chính
            self.root = ctk.CTk()
            self.root.title("GEM AI - Trợ lý thông minh")
            self.root.geometry("800x600")
            
            # Đặt cửa sổ ở vị trí không trùng với pygame
            screen_width = self.root.winfo_screenwidth()
            ai_x = min(screen_width - 850, 1000)  # Đặt bên phải
            ai_y = 50
            self.root.geometry(f"800x600+{ai_x}+{ai_y}")
            
            # Đảm bảo không thu nhỏ cửa sổ pygame
            self.root.attributes('-topmost', False)
            self.root.focus_set()
            
            # Khởi tạo client GPT
            self.client = Client()
            self.conversation_history = []
            
            # Kiến thức mặc định cho AI (thay thế file database.txt)
            self.default_knowledge = """
            Tôi là GEM AI - Trợ lý thông minh được tích hợp vào game học tập.
            
            KIẾN THỨC CƠ BẢN:
            - Tôi có thể giúp giải đáp thắc mắc về học tập, giáo dục
            - Hỗ trợ giải bài tập toán học, vật lý, hóa học cơ bản
            - Tư vấn phương pháp học tập hiệu quả
            - Giải thích các khái niệm khó hiểu
            - Gợi ý cách ghi nhớ kiến thức
            
            CHỨC NĂNG GAME:
            - Game có hệ thống điểm và năng lượng
            - Người chơi có thể đổi avatar bằng điểm
            - Có streak system để khuyến khích học đều đặn
            - Có nhiều màn chơi khác nhau
            
            NGUYÊN TẮC HOẠT ĐỘNG:
            - Trả lời một cách thân thiện, hữu ích
            - Khuyến khích tinh thần học tập
            - Đưa ra lời khuyên tích cực
            - Giải thích đơn giản, dễ hiểu
            """
            
            self.setup_ui()
            
        except Exception as e:
            print(f"Lỗi khởi tạo ChatbotApp: {e}")
            raise
            
    def setup_ui(self):
        try:
            # Frame chính
            main_frame = ctk.CTkFrame(self.root)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Text widget hiển thị cuộc trò chuyện
            self.chat_display = ctk.CTkTextbox(main_frame, height=400, width=760)
            self.chat_display.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Frame nhập tin nhắn
            input_frame = ctk.CTkFrame(main_frame)
            input_frame.pack(fill="x", padx=10, pady=5)
            
            # Entry nhập tin nhắn
            self.message_entry = ctk.CTkEntry(input_frame, placeholder_text="Hỏi GEM AI bất kỳ điều gì...")
            self.message_entry.pack(side="left", fill="x", expand=True, padx=5)
            
            # Button gửi
            send_button = ctk.CTkButton(input_frame, text="Gửi", command=self.send_message, width=80)
            send_button.pack(side="right", padx=2)
            
            # Button xóa cuộc trò chuyện
            clear_button = ctk.CTkButton(input_frame, text="Xóa", command=self.clear_chat, width=80)
            clear_button.pack(side="right", padx=2)
            
            # Button đóng (không ảnh hưởng pygame)
            close_button = ctk.CTkButton(input_frame, text="Đóng", command=self.safe_close, width=80)
            close_button.pack(side="right", padx=2)
            
            # Bind Enter key
            self.message_entry.bind("<Return>", lambda event: self.send_message())
            
            # Status label
            self.status_label = ctk.CTkLabel(main_frame, text="GEM AI sẵn sàng hỗ trợ bạn!")
            self.status_label.pack(pady=5)
            
            # Hiển thị lời chào
            self.add_to_chat("GEM AI", "Xin chào! Tôi là GEM AI, trợ lý thông minh của bạn trong game học tập.\nHãy hỏi tôi bất kỳ điều gì về học tập, game, hoặc những thắc mắc khác nhé! 😊")
            
        except Exception as e:
            print(f"Lỗi setup UI: {e}")
            raise

    def safe_close(self):
        """Đóng cửa sổ AI một cách an toàn mà không ảnh hưởng pygame"""
        try:
            self.root.withdraw()  # Ẩn thay vì destroy
        except:
            pass

    def add_to_chat(self, sender, message):
        """Thêm tin nhắn vào khung chat"""
        try:
            timestamp = time.strftime("%H:%M")
            display_name = "🤖 GEM AI" if sender == "GEM AI" else "👤 Bạn"
            self.chat_display.insert(tk.END, f"[{timestamp}] {display_name}:\n{message}\n\n")
            self.chat_display.see(tk.END)
        except Exception as e:
            print(f"Lỗi add_to_chat: {e}")
            
    def send_message(self):
        """Gửi tin nhắn và nhận phản hồi từ GPT"""
        try:
            user_message = self.message_entry.get().strip()
            
            if not user_message:
                return
                
            # Hiển thị tin nhắn người dùng
            self.add_to_chat("Bạn", user_message)
            self.message_entry.delete(0, tk.END)
            
            # Tạo thread để gọi GPT tránh đóng băng UI
            thread = threading.Thread(target=self.get_gpt_response, args=(user_message,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"Lỗi send_message: {e}")
            
    def get_gpt_response(self, user_message):
        """Lấy phản hồi từ GPT với kiến thức mặc định"""
        try:
            self.status_label.configure(text="GEM AI đang suy nghĩ...")
            
            # Tạo prompt với kiến thức mặc định
            system_prompt = f"""
            {self.default_knowledge}
            
            Bạn là GEM AI - một trợ lý AI thông minh, thân thiện và hữu ích. 
            Hãy trả lời câu hỏi của người dùng một cách chi tiết, dễ hiểu và tích cực.
            
            Nguyên tắc trả lời:
            1. Luôn thân thiện và lịch sự
            2. Giải thích rõ ràng, dễ hiểu
            3. Đưa ra ví dụ cụ thể khi cần
            4. Khuyến khích tinh thần học tập
            5. Nếu không biết câu trả lời, hãy thành thật và gợi ý tìm hiểu thêm
            """
            
            # Thêm lịch sử cuộc trò chuyện (giới hạn 10 tin nhắn gần nhất)
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
                
            messages.append({"role": "user", "content": user_message})
            
            # Gọi GPT
            response = self.client.chat.completions.create(
                model=gpt_4o_mini,
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            gpt_response = response.choices[0].message.content
            
            # Cập nhật UI trong main thread
            self.root.after(0, self.update_chat_with_response, gpt_response)
            
            # Lưu vào lịch sử
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": gpt_response})
            
        except Exception as e:
            error_msg = f"Xin lỗi, tôi gặp sự cố kỹ thuật: {str(e)}\n\nBạn có thể thử lại hoặc hỏi câu khác nhé!"
            self.root.after(0, self.update_chat_with_response, error_msg)
            
    def update_chat_with_response(self, response):
        """Cập nhật chat với phản hồi từ GPT"""
        try:
            self.add_to_chat("GEM AI", response)
            self.status_label.configure(text="GEM AI sẵn sàng hỗ trợ bạn!")
        except Exception as e:
            print(f"Lỗi update_chat_with_response: {e}")
            
    def clear_chat(self):
        """Xóa cuộc trò chuyện"""
        try:
            self.chat_display.delete("1.0", tk.END)
            self.conversation_history = []
            self.add_to_chat("GEM AI", "Cuộc trò chuyện đã được xóa! Tôi sẵn sàng hỗ trợ bạn với những câu hỏi mới. 😊")
            self.status_label.configure(text="GEM AI sẵn sàng hỗ trợ bạn!")
        except Exception as e:
            print(f"Lỗi clear_chat: {e}")
            
    def run(self):
        """Chạy ứng dụng"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Lỗi chạy ứng dụng: {e}")


def run_chatbot():
    """Hàm wrapper để chạy chatbot an toàn mà không ảnh hưởng pygame"""
    try:
        # Không cần tạo file database.txt nữa
        print("Khởi động GEM AI với kiến thức tích hợp...")
        
        # Khởi động ứng dụng
        app = ChatbotApp()
        app.run()
        
    except Exception as e:
        print(f"Lỗi trong run_chatbot: {e}")
        return False
    
    return True


def _open_gem_ai(screen: pygame.Surface, game_state: 'GameState', click_sound: pygame.mixer.Sound) -> None:
    """Mở GEM AI mà không thu nhỏ app chính - phiên bản cải tiến"""
    # Hiển thị màn hình loading ngắn gọn hơn
    start_time = time.time()
    duration = 1.5  # Giảm thời gian loading xuống 1.5 giây
    
    while time.time() - start_time < duration:
        # Xử lý events để tránh đóng băng
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        progress = min((time.time() - start_time) / duration, 1)

        # Vẽ background
        screen.fill(config.COLORS["bg"])
        _draw_gradient_background(screen, config.COLORS["bg"], (220, 245, 220), 
                                 pygame.Rect(0, 0, config.WIDTH, config.HEIGHT))
        
        # Logo hoặc icon AI (nếu có)
        ai_icon_rect = pygame.Rect(config.WIDTH//2 - 50, 120, 100, 100)
        pygame.draw.circle(screen, config.COLORS["accent"], ai_icon_rect.center, 50)
        pygame.draw.circle(screen, (255, 255, 255), ai_icon_rect.center, 40)
        
        # Vẽ "AI" text trong circle
        ai_text = config.FONT_TITLE.render("AI", True, config.COLORS["accent"])
        ai_text_pos = (ai_icon_rect.centerx - ai_text.get_width()//2, 
                      ai_icon_rect.centery - ai_text.get_height()//2)
        screen.blit(ai_text, ai_text_pos)
        
        # Tiêu đề
        text_surface = config.FONT_TITLE.render("ĐANG KHỞI ĐỘNG GEM AI", True, config.COLORS["accent"])
        text_pos = (config.WIDTH // 2 - text_surface.get_width() // 2, 250)
        screen.blit(text_surface, text_pos)

        # Thanh tiến trình với hiệu ứng đẹp hơn
        progress_rect = pygame.Rect(config.WIDTH//2 - 200, 300, 400, 20)
        pygame.draw.rect(screen, (200, 220, 200), progress_rect, border_radius=10)
        
        # Thanh tiến trình với gradient
        if progress > 0:
            filled_width = int(400 * progress)
            filled_rect = pygame.Rect(config.WIDTH//2 - 200, 300, filled_width, 20)
            pygame.draw.rect(screen, config.COLORS["accent"], filled_rect, border_radius=10)

        # Phần trăm
        percent = config.FONT.render(f"{int(progress*100)}%", True, config.COLORS["text"])
        screen.blit(percent, (config.WIDTH//2 - percent.get_width()//2, 330))
        
        # Tip ngẫu nhiên
        tips = [
            "💡 Tip: Bạn có thể hỏi GEM AI về bất kỳ môn học nào!",
            "🎯 Tip: GEM AI có thể giúp giải bài tập và giải thích khái niệm",
            "📚 Tip: Hãy thử hỏi về phương pháp học tập hiệu quả",
            "🤖 Tip: GEM AI luôn sẵn sàng hỗ trợ 24/7!"
        ]
        tip_index = int(progress * len(tips)) % len(tips)
        tip_text = config.FONT.render(tips[tip_index], True, config.COLORS["text"])
        screen.blit(tip_text, (config.WIDTH//2 - tip_text.get_width()//2, 380))

        pygame.display.flip()
        pygame.time.delay(30)

    # Sau khi loading xong, khởi động AI
    game_state.show_message("Đang mở GEM AI...")
    
    try:
        # Lưu trạng thái pygame hiện tại
        pygame_focused = pygame.display.get_surface() is not None
        
        # Khởi động GEM AI trong thread riêng
        def run_ai_safe():
            try:
                app = ChatbotApp()
                app.run()
            except Exception as e:
                print(f"Lỗi khi khởi động GEM AI: {e}")
        
        # Chạy trong thread daemon
        ai_thread = threading.Thread(target=run_ai_safe, daemon=True)
        ai_thread.start()
        
        # Đợi một chút để AI khởi động
        pygame.time.wait(500)
        
        # Đảm bảo pygame window vẫn active và không bị thu nhỏ
        if pygame_focused:
            # Force pygame window to stay active
            pygame.display.flip()
            
            # Thử các cách khác nhau để giữ focus cho pygame
            try:
                # Phương pháp 1: Re-initialize display nếu cần
                current_surface = pygame.display.get_surface()
                if current_surface:
                    pygame.display.flip()
                    
                # Phương pháp 2: Gửi event để active lại window
                pygame.event.post(pygame.event.Event(pygame.ACTIVEEVENT, {'gain': 1, 'state': 1}))
                
            except Exception as focus_error:
                print(f"Warning: Không thể duy trì focus pygame: {focus_error}")
        
        game_state.show_message("GEM AI đã khởi động thành công! 🤖")
        
    except Exception as e:
        print(f"Lỗi khi khởi động GEM AI: {e}")
        game_state.show_message("Không thể khởi động GEM AI!")
        
    # Làm mới màn hình pygame
    pygame.display.flip()


class ModernButton(ui_elements.Button):
    """Nút hiện đại với hiệu ứng hover và gradient"""
    def __init__(self, x: int, y: int, w: int, h: int, text: str, 
                 callback: Callable, color: Tuple[int, int, int], 
                 icon_path: Optional[str] = None, 
                 gradient_colors: Optional[List[Tuple[int, int, int]]] = None,
                 click_sound: Optional[pygame.mixer.Sound] = None):
        super().__init__(x, y, w, h, text, callback, color, 15, click_sound)
        self.icon_path = icon_path
        self.gradient_colors = gradient_colors or [color, 
            (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))]
        self.hover_scale = 1.0
        self.click_scale = 1.0
        self.shadow_offset = 0
        
    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Animation cho hover effect
        target_scale = 1.05 if is_hovered else 1.0
        self.hover_scale += (target_scale - self.hover_scale) * 0.15
        
        target_shadow = 8 if is_hovered else 4
        self.shadow_offset += (target_shadow - self.shadow_offset) * 0.1
        
        # Tính toán rect với scale
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Vẽ bóng đổ (giới hạn trong border radius)
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += int(self.shadow_offset)
        shadow_rect.y += int(self.shadow_offset)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), 
                        (0, 0, shadow_rect.width, shadow_rect.height), 
                        border_radius=15)
        surface.blit(shadow_surface, shadow_rect)
        
        # Vẽ gradient background (giới hạn trong border radius)
        gradient_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        self._draw_gradient_rect(gradient_surface, self.gradient_colors[0], self.gradient_colors[1], 
                               pygame.Rect(0, 0, scaled_rect.width, scaled_rect.height))
        surface.blit(gradient_surface, scaled_rect)
        
        # Vẽ viền (chỉ vẽ trên surface chính)
        border_color = (255, 255, 255, 150) if is_hovered else (200, 220, 200)
        pygame.draw.rect(surface, border_color, scaled_rect, 2, border_radius=0)
        
        # Vẽ glassmorphism overlay nếu hover
        if is_hovered:
            glass_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
            self._draw_glass_effect(glass_surface, pygame.Rect(0, 0, scaled_rect.width, scaled_rect.height))
            surface.blit(glass_surface, scaled_rect)
        
        # Vẽ icon nếu có
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                icon = pygame.image.load(self.icon_path)
                icon_size = int(40 * self.hover_scale)
                icon = pygame.transform.scale(icon, (icon_size, icon_size))
                icon_x = scaled_rect.x + 20
                icon_y = scaled_rect.centery - icon_size // 2
                surface.blit(icon, (icon_x, icon_y))
            except Exception as e:
                print(f"Error loading icon: {e}")
        
        # Vẽ text với hiệu ứng
        if self.text:
            text_color = (255, 255, 255) if is_hovered else config.COLORS["text"]
            text_render = config.FONT.render(self.text, True, text_color)
            
            # Vẽ text shadow
            shadow_render = config.FONT.render(self.text, True, (0, 0, 0, 100))
            shadow_x = scaled_rect.centerx - text_render.get_width() // 2 + 1
            shadow_y = scaled_rect.centery - text_render.get_height() // 2 + 1
            surface.blit(shadow_render, (shadow_x, shadow_y))
            
            # Vẽ text chính
            text_x = scaled_rect.centerx - text_render.get_width() // 2
            text_y = scaled_rect.centery - text_render.get_height() // 2
            if self.icon_path:
                text_x += 30  # Dịch chuyển text nếu có icon
            surface.blit(text_render, (text_x, text_y))

    def _draw_gradient_rect(self, surface: pygame.Surface, 
                          color1: Tuple[int, int, int], 
                          color2: Tuple[int, int, int], 
                          rect: pygame.Rect, 
                          vertical: bool = True) -> None:
        """Vẽ hình chữ nhật với gradient"""
        for i in range(rect.height if vertical else rect.width):
            ratio = i / (rect.height if vertical else rect.width)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            if vertical:
                pygame.draw.line(surface, (r, g, b), 
                               (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
            else:
                pygame.draw.line(surface, (r, g, b), 
                               (rect.x + i, rect.y), (rect.x + i, rect.y + rect.height))

    def _draw_glass_effect(self, surface: pygame.Surface, rect: pygame.Rect, alpha: int = 50) -> None:
        """Vẽ hiệu ứng kính mờ"""
        pygame.draw.rect(surface, (255, 255, 255, alpha), (0, 0, rect.width, rect.height), border_radius=15)
        pygame.draw.rect(surface, (255, 255, 255, 80), (0, 0, rect.width, rect.height//3), border_radius=15)


def draw_setting(screen: pygame.Surface, game_state: 'GameState', click_sound: pygame.mixer.Sound) -> List[ModernButton]:
    """Vẽ màn hình cài đặt chính với bố cục mới"""
    global animation_time
    animation_time = pygame.time.get_ticks()
    
    # Background với gradient động
    screen.fill(config.COLORS["bg"])
    bg_rect = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)
    _draw_gradient_background(screen, config.COLORS["bg"], (220, 245, 220), bg_rect)
    
    # Vẽ hiệu ứng particles
    _draw_floating_particles(screen, config.COLORS, animation_time)
    
    # Container chính
    main_container = pygame.Rect(50, 50, config.WIDTH - 100, config.HEIGHT - 100)
    _draw_glass_panel(screen, main_container, (240, 250, 240), 180)
    
    # Tiêu đề với hiệu ứng
    title_surface = config.FONT_TITLE.render("CÀI ĐẶT", True, config.COLORS["accent"])
    title_x = (screen.get_width() - title_surface.get_width()) // 2
    screen.blit(title_surface, (title_x, 70))

    # --- Phần thông tin người dùng ---
    user_section = pygame.Rect(100, 150, config.WIDTH - 200, 200)
    _draw_glass_panel(screen, user_section, (255, 255, 255), 150)
    
    # Avatar với hiệu ứng
    avatar_rect = pygame.Rect(120, 170, 120, 120)
    _draw_avatar_with_effects(screen, game_state, avatar_rect)
    
    # Thông tin người dùng
    user_info_x = 260
    _draw_user_info(screen, game_state, user_info_x, 180)
    
    # --- Phần cài đặt chức năng ---
    settings_section = pygame.Rect(100, 370, config.WIDTH - 200, 200)
    _draw_glass_panel(screen, settings_section, (255, 255, 255), 150)
    
    # Tạo các nút chức năng
    buttons = []
    
    # Nút đổi avatar
    avatar_btn = ModernButton(
        x=120, y=390, w=200, h=60,
        text="Đổi Avatar",
        callback=lambda: game_state.set_temp_screen("avatar_selection"),
        color=(100, 180, 255),
        gradient_colors=[(100, 180, 255), (70, 150, 230)],
        icon_path=os.path.join(config.ASSETS_DIR, "setting", "avatar_icon.png") if os.path.exists(os.path.join(config.ASSETS_DIR, "setting", "avatar_icon.png")) else None,
        click_sound=click_sound
    )
    buttons.append(avatar_btn)
    
    # Nút âm thanh
    sound_btn = ModernButton(
        x=340, y=390, w=200, h=60,
        text="Âm Thanh",
        callback=toggle_sound,
        color=(255, 180, 100),
        gradient_colors=[(255, 180, 100), (230, 150, 80)],
        icon_path=os.path.join(config.ASSETS_DIR, "setting", "sound_icon.png") if os.path.exists(os.path.join(config.ASSETS_DIR, "setting", "sound_icon.png")) else None,
        click_sound=click_sound
    )
    buttons.append(sound_btn)
    
    # Nút GEM AI
    ai_btn = ModernButton(
        x=560, y=390, w=200, h=60,
        text="GEM AI",
        callback=lambda: _open_gem_ai(screen, game_state, click_sound),
        color=(100, 220, 100),
        gradient_colors=[(100, 220, 100), (80, 200, 80)],
        icon_path=os.path.join(config.ASSETS_DIR, "setting", "ai_icon.png") if os.path.exists(os.path.join(config.ASSETS_DIR, "setting", "ai_icon.png")) else None,
        click_sound=click_sound
    )
    buttons.append(ai_btn)
    
    # Nút quay lại
    back_btn = ModernButton(
        x=50, y=config.HEIGHT - 80, w=150, h=50,
        text="Quay lại",
        callback=lambda: setattr(game_state, 'current_screen', "lesson"),
        color=(220, 100, 100),
        gradient_colors=[(220, 100, 100), (190, 70, 70)],
        click_sound=click_sound
    )
    buttons.append(back_btn)
    
    # Vẽ tất cả các nút
    for btn in buttons:
        btn.draw(screen)
    
    return buttons


def draw_avatar_selection(screen: pygame.Surface, game_state: 'GameState', 
                         click_sound: pygame.mixer.Sound) -> List[ModernButton]:
    """Vẽ màn hình chọn avatar với 4 avatar nằm gọn trong màn hình"""
    global animation_time
    animation_time = pygame.time.get_ticks()
    
    # Background
    screen.fill(config.COLORS["bg"])
    bg_rect = pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)
    _draw_gradient_background(screen, config.COLORS["bg"], (210, 240, 210), bg_rect)
    _draw_floating_particles(screen, config.COLORS, animation_time)
    
    # Container chính
    main_container = pygame.Rect(50, 50, config.WIDTH - 100, config.HEIGHT - 100)
    _draw_glass_panel(screen, main_container, (255, 255, 255), 150)
    
    # Tiêu đề
    title = config.FONT_TITLE.render("CHỌN AVATAR", True, config.COLORS["accent"])
    screen.blit(title, (config.WIDTH//2 - title.get_width()//2, 70))

    # Danh sách avatar
    avatar_options = [
        {"name": "Sách Thông Thái", "path": os.path.join(config.AVATAR_DIR, "avatar1.jpg"), "price": 100},
        {"name": "Mèo Vô Tri", "path": os.path.join(config.AVATAR_DIR, "avatar2.jpg"), "price": 150},
        {"name": "Cáo Tinh Nghịch", "path": os.path.join(config.AVATAR_DIR, "avatar3.jpg"), "price": 200},
        {"name": "Vô Cực", "path": os.path.join(config.AVATAR_DIR, "avatar4.jpg"), "price": 250},
    ]
    
    buttons = []
    
    # Tính toán kích thước và vị trí các card để vừa với màn hình 960px
    num_avatars = len(avatar_options)
    card_width = 200  # Giảm width để fit 4 avatar
    card_height = 240  # Giảm height tương ứng
    total_gap = config.WIDTH - (num_avatars * card_width)  # Tổng khoảng trống cần chia
    gap = total_gap // (num_avatars + 1)  # Chia đều khoảng cách giữa các avatar và 2 bên
    
    # Điều chỉnh vị trí y để avatar nằm giữa màn hình theo chiều dọc
    start_y = (config.HEIGHT - card_height) // 2
    
    # Hiển thị avatar dạng hàng ngang
    for i, avatar in enumerate(avatar_options):
        x = gap + i * (card_width + gap)  # Tính vị trí x để căn đều
        y = start_y
        
        owned = avatar["path"] in game_state.owned_avatars
        current = game_state.avatar_path == avatar["path"]
        
        # Vẽ card avatar
        card_rect = pygame.Rect(x, y, card_width, card_height)
        _draw_avatar_card_status(screen, avatar, card_rect, owned, current)
        
        # Tạo nút tương tác
        if owned:
            btn_callback = lambda a=avatar: _use_avatar(a, game_state)
        else:
            btn_callback = lambda a=avatar: _purchase_avatar(a, game_state)
            
        btn = ModernButton(
            x=x, y=y, w=card_width, h=card_height,
            text="", callback=btn_callback,
            color=(0, 0, 0, 0),
            click_sound=click_sound
        )
        buttons.append(btn)
    
    # Nút quay lại
    back_btn = ModernButton(
        x=config.WIDTH - 200, y=config.HEIGHT - 80, w=150, h=50,
        text="Quay lại", 
        callback=lambda: game_state.set_temp_screen(None),
        color=(220, 100, 100),
        gradient_colors=[(220, 100, 100), (190, 70, 70)],
        click_sound=click_sound
    )
    buttons.append(back_btn)
    back_btn.draw(screen)
    
    return buttons


# ===== Các hàm tiện ích =====

def _draw_gradient_background(surface: pygame.Surface, 
                            color1: Tuple[int, int, int], 
                            color2: Tuple[int, int, int], 
                            rect: pygame.Rect) -> None:
    """Vẽ background gradient"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))


def _draw_floating_particles(surface: pygame.Surface, 
                           colors: Dict[str, Tuple[int, int, int]], 
                           time_value: int) -> None:
    """Vẽ các hạt bay lơ lửng"""
    for i in range(15):
        x = (200 + i * 50 + math.sin(time_value * 0.01 + i) * 20) % config.WIDTH
        y = (100 + i * 30 + math.cos(time_value * 0.008 + i) * 15) % config.HEIGHT
        radius = 3 + math.sin(time_value * 0.02 + i) * 1
        alpha = int(100 + math.sin(time_value * 0.015 + i) * 50)
        
        particle_color = colors["accent"] if i % 3 == 0 else colors["button"]
        particle_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*particle_color, alpha), 
                          (radius * 2, radius * 2), radius)
        surface.blit(particle_surface, (x - radius * 2, y - radius * 2))


def _draw_glass_panel(surface: pygame.Surface, rect: pygame.Rect, 
                     base_color: Tuple[int, int, int], alpha: int) -> None:
    """Vẽ panel kính mờ"""
    glass_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glass_surface, (*base_color, alpha), (0, 0, rect.width, rect.height), border_radius=20)
    pygame.draw.rect(glass_surface, (255, 255, 255, 50), (0, 0, rect.width, rect.height), 2, border_radius=20)
    pygame.draw.rect(glass_surface, (255, 255, 255, 30), (0, 0, rect.width, rect.height//3), border_radius=20)
    surface.blit(glass_surface, rect)


def _draw_avatar_with_effects(surface: pygame.Surface, game_state: 'GameState', rect: pygame.Rect) -> None:
    """Vẽ avatar với hiệu ứng đặc biệt"""
    # Glow effect
    for i in range(3):
        glow_radius = rect.width//2 + 10 + i * 5
        glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*config.COLORS["accent"], 60 - i * 20),
                          (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (rect.centerx - glow_radius, rect.centery - glow_radius))
    
    # Avatar frame
    pygame.draw.circle(surface, (255, 255, 255), rect.center, rect.width//2)
    
    # Load và hiển thị avatar
    try:
        avatar_img = pygame.image.load(game_state.avatar_path)
        avatar_img = pygame.transform.scale(avatar_img, (rect.width-10, rect.height-10))
        avatar_mask = pygame.Surface((rect.width-10, rect.height-10), pygame.SRCALPHA)
        pygame.draw.circle(avatar_mask, (255, 255, 255, 255), 
                          (rect.width//2-5, rect.height//2-5), rect.width//2-5)
        avatar_img.blit(avatar_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(avatar_img, (rect.x+5, rect.y+5))
    except Exception as e:
        print(f"Error loading avatar: {e}")
        pygame.draw.circle(surface, config.COLORS["button"], rect.center, rect.width//2-5)


def _draw_user_info(surface: pygame.Surface, game_state: 'GameState', 
                   x: int, y: int) -> None:
    """Vẽ thông tin người dùng"""
    # Tên người dùng
    username = config.FONT_TITLE.render("Người chơi", True, config.COLORS["text"])
    surface.blit(username, (x, y-10))
    
    # Điểm
    points = config.FONT.render(f"Điểm: {game_state.point}", True, config.COLORS["text"])
    surface.blit(points, (x, y + 50))
    
    # Năng lượng
    energy = config.FONT.render(f"Năng lượng: {game_state.energy}/10", True, config.COLORS["text"])
    surface.blit(energy, (x, y + 90))
    
    # Streak
    streak = config.FONT.render(f"Streak: {game_state.streak} ngày", True, config.COLORS["text"])
    surface.blit(streak, (x, y + 130))


def _draw_avatar_card_status(surface: pygame.Surface, avatar: Dict, 
                           rect: pygame.Rect, owned: bool, current: bool) -> None:
    """Vẽ card avatar với trạng thái nổi bật (phiên bản nhỏ gọn)"""
    # Xác định màu sắc theo trạng thái
    if current:
        card_color = (70, 200, 70)  # Đang sử dụng - xanh đậm
        border_color = (255, 255, 0)  # Viền vàng
    elif owned:
        card_color = (100, 200, 100)  # Đã sở hữu - xanh nhạt
        border_color = (200, 200, 200)  # Viền trắng xám
    else:
        card_color = (200, 200, 200)  # Chưa sở hữu - xám
        border_color = (150, 150, 150)  # Viền xám đậm
    
    # Vẽ card background
    pygame.draw.rect(surface, card_color, rect, border_radius=12)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)
    
    # Avatar image (nhỏ hơn để phù hợp với card nhỏ)
    img_size = min(rect.width - 30, rect.height - 80)  # Giảm kích thước ảnh
    img_rect = pygame.Rect(
        rect.x + (rect.width - img_size)//2,
        rect.y + 15,
        img_size,
        img_size
    )
    
    try:
        avatar_img = pygame.image.load(avatar["path"])
        avatar_img = pygame.transform.scale(avatar_img, (img_size, img_size))
        surface.blit(avatar_img, img_rect)
        
        # Hiệu ứng selected
        if current:
            selected_overlay = pygame.Surface((img_size, img_size), pygame.SRCALPHA)
            pygame.draw.rect(selected_overlay, (255, 255, 0, 50), (0, 0, img_size, img_size), border_radius=8)
            surface.blit(selected_overlay, img_rect)
    except:
        pygame.draw.rect(surface, (150, 150, 150), img_rect, border_radius=8)
    
    # Avatar info (điều chỉnh vị trí cho phù hợp)
    info_y = rect.y + img_size + 20
    
    # Tên avatar (sử dụng font nhỏ hơn nếu cần)
    name = config.FONT.render(avatar["name"], True, config.COLORS["text"])
    surface.blit(name, (rect.centerx - name.get_width()//2, info_y))
    
    # Trạng thái
    status_y = info_y + 25
    if current:
        status_text = "ĐANG DÙNG"
        status_color = (255, 255, 0)  # Vàng
    elif owned:
        status_text = "ĐÃ SỞ HỮU"
        status_color = (50, 200, 50)  # Xanh lá
    else:
        status_text = f"{avatar['price']} ĐIỂM"
        status_color = (255, 150, 50)  # Cam
    
    status = config.FONT.render(status_text, True, status_color)
    surface.blit(status, (rect.centerx - status.get_width()//2, status_y))


def _use_avatar(avatar: Dict, game_state: 'GameState') -> None:
    """Sử dụng avatar đã sở hữu"""
    game_state.avatar_path = avatar["path"]
    game_state.show_message(f"Đã đổi sang avatar {avatar['name']}!")
    game_state.set_temp_screen(None)
    game_state.write_data()


def _purchase_avatar(avatar: Dict, game_state: 'GameState') -> None:
    """Mua avatar mới"""
    if game_state.point >= avatar["price"]:
        game_state.point -= avatar["price"]
        game_state.owned_avatars.append(avatar["path"])
        game_state.avatar_path = avatar["path"]
        game_state.show_message(f"Đã mua avatar {avatar['name']}!")
        game_state.write_data()
    else:
        game_state.show_message("Không đủ điểm!")


def _open_gem_ai(screen: pygame.Surface, game_state: 'GameState', click_sound: pygame.mixer.Sound) -> None:
    """Mở GEM AI mà không thu nhỏ app chính"""
    # Hiển thị màn hình loading trước
    start_time = time.time()
    duration = 2  # Thời gian loading 2 giây
    
    while time.time() - start_time < duration:
        # Xử lý events để tránh đóng băng
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        progress = min((time.time() - start_time) / duration, 1)

        # Vẽ background
        screen.fill(config.COLORS["bg"])
        _draw_gradient_background(screen, config.COLORS["bg"], (220, 245, 220), 
                                 pygame.Rect(0, 0, config.WIDTH, config.HEIGHT))
        
        # Tiêu đề
        text_surface = config.FONT_TITLE.render("ĐANG KHỞI ĐỘNG GEM AI", True, config.COLORS["accent"])
        text_pos = (config.WIDTH // 2 - text_surface.get_width() // 2, 150)
        screen.blit(text_surface, text_pos)

        # Thanh tiến trình
        progress_rect = pygame.Rect(config.WIDTH//2 - 250, 300, 500, 30)
        pygame.draw.rect(screen, (200, 220, 200), progress_rect, border_radius=15)
        pygame.draw.rect(screen, config.COLORS["accent"], 
                        pygame.Rect(config.WIDTH//2 - 250, 300, int(500 * progress), 30), 
                        border_radius=15)

        # Phần trăm
        percent = config.FONT.render(f"{int(progress*100)}%", True, config.COLORS["text"])
        screen.blit(percent, (config.WIDTH//2 - percent.get_width()//2, 350))

        pygame.display.flip()
        pygame.time.delay(50)

    # Sau khi loading xong, khởi động AI
    game_state.show_message("Đang mở GEM AI...")
    
    try:
        # Khởi động GEM AI trong thread riêng để không block UI
        def run_ai_safe():
            try:
                # Đặt vị trí cửa sổ AI ở bên cạnh thay vì đè lên
                # Không sử dụng SDL_VIDEO_WINDOW_POS để tránh ảnh hưởng đến Pygame
                app = ChatbotApp()
                
                # Đặt vị trí cửa sổ AI bên cạnh cửa sổ chính
                # (giả sử cửa sổ pygame ở vị trí mặc định)
                try:
                    # Lấy kích thước màn hình
                    screen_width = app.root.winfo_screenwidth()
                    screen_height = app.root.winfo_screenheight()
                    
                    # Đặt cửa sổ AI ở bên phải (hoặc vị trí phù hợp)
                    ai_x = min(screen_width - 800 - 50, config.WIDTH + 50)  # Bên cạnh cửa sổ game
                    ai_y = 50
                    
                    app.root.geometry(f"800x600+{ai_x}+{ai_y}")
                except:
                    # Fallback: đặt ở vị trí mặc định
                    app.root.geometry("800x600+100+100")
                
                # Đảm bảo cửa sổ AI không chiếm focus hoàn toàn
                app.root.attributes('-topmost', False)
                
                app.run()
                
            except Exception as e:
                print(f"Lỗi khi khởi động GEM AI: {e}")
        
        # Chạy trong thread daemon để không block main thread
        ai_thread = threading.Thread(target=run_ai_safe, daemon=True)
        ai_thread.start()
        
        game_state.show_message("GEM AI đã được khởi động")
        
        # Đảm bảo pygame window vẫn active
        pygame.display.flip()
        
        # Delay ngắn để user thấy thông báo
        pygame.time.wait(500)
        
    except Exception as e:
        print(f"Lỗi khi khởi động GEM AI: {e}")
        game_state.show_message("Không thể khởi động GEM AI!")


def toggle_sound() -> None:
    """Bật/tắt âm thanh"""
    if mixer.music.get_volume() > 0:
        mixer.music.set_volume(0)
        pygame.mixer.pause()
    else:
        mixer.music.set_volume(0.5)
        pygame.mixer.unpause()