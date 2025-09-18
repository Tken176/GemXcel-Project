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
import webbrowser
import tempfile
import json

# Animation variables
animation_time = 0
hover_states = {}

# GEM AI HTML template được nhúng trực tiếp
GEM_AI_HTML = '''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="google" content="notranslate">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEM AI - Chat Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }

        .chat-header {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chat-header h1 {
            color: white;
            font-size: 28px;
            margin-bottom: 5px;
            font-weight: 700;
        }

        .chat-header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            animation: fadeIn 0.5s ease-out;
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 16px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }

        .message.bot .message-avatar {
            background: linear-gradient(135deg, #f093fb, #f5576c);
        }

        .message-content {
            background: rgba(255, 255, 255, 0.15);
            padding: 15px 20px;
            border-radius: 18px;
            max-width: 70%;
            word-wrap: break-word;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .message.user .message-content {
            background: rgba(255, 255, 255, 0.2);
        }

        .message-text {
            color: white;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .message-time {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 8px;
        }

        .chat-input-container {
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .chat-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            padding: 15px 20px;
            color: white;
            font-size: 16px;
            resize: none;
            outline: none;
            min-height: 50px;
            max-height: 120px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .chat-input:focus {
            border-color: rgba(255, 255, 255, 0.4);
            background: rgba(255, 255, 255, 0.15);
        }

        .chat-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }

        .send-button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            font-size: 20px;
        }

        .send-button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            color: rgba(255, 255, 255, 0.8);
            font-style: italic;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.8);
            animation: typingDot 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        .error-message {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid rgba(255, 107, 107, 0.3);
            color: #ff6b6b;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes typingDot {
            0%, 20% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.5);
                opacity: 0.7;
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }

        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
        }

        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.5);
        }

        @media (max-width: 768px) {
            .chat-container {
                width: 95%;
                height: 95vh;
                border-radius: 15px;
            }

            .message-content {
                max-width: 85%;
            }

            .chat-header h1 {
                font-size: 24px;
            }

            .chat-input {
                font-size: 14px;
                padding: 12px 16px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>💎 GEM AI</h1>
            <p>gia sư hỗ trợ bạn</p>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-avatar">AI</div>
                <div class="message-content">
                    <div class="message-text">Xin chào! Tôi là GEM AI, trợ lý thông minh được hỗ trợ bởi Gemini. Tôi có thể giúp bạn trả lời câu hỏi, giải quyết vấn đề, và hỗ trợ nhiều công việc khác. Hãy hỏi tôi bất cứ điều gì bạn muốn biết!</div>
                    <div class="message-time" id="welcomeTime"></div>
                </div>
            </div>
        </div>

        <div class="chat-input-container">
            <div class="chat-input-wrapper">
                <textarea 
                    class="chat-input" 
                    id="chatInput" 
                    placeholder="Nhập tin nhắn của bạn..."
                    rows="1"
                ></textarea>
                <button class="send-button" id="sendButton">
                    ➤
                </button>
            </div>
        </div>
    </div>

    <script>
        class GemAIChatBot {
            constructor() {
                this.apiKey = 'INPUT_YOUR_API';
                this.apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
                this.chatMessages = document.getElementById('chatMessages');
                this.chatInput = document.getElementById('chatInput');
                this.sendButton = document.getElementById('sendButton');
                
                this.init();
            }

            init() {
                document.getElementById('welcomeTime').textContent = this.getCurrentTime();
                
                this.sendButton.addEventListener('click', () => this.sendMessage());
                this.chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });

                this.chatInput.addEventListener('input', () => {
                    this.chatInput.style.height = 'auto';
                    this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
                });
            }

            getCurrentTime() {
                const now = new Date();
                return now.toLocaleTimeString('vi-VN', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
            }

            async sendMessage() {
                const message = this.chatInput.value.trim();
                if (!message) return;

                this.addMessage(message, 'user');
                this.chatInput.value = '';
                this.chatInput.style.height = 'auto';
                
                this.sendButton.disabled = true;
                this.showTypingIndicator();
                
                try {
                    const response = await this.callGeminiAPI(message);
                    this.hideTypingIndicator();
                    
                    if (response && response.candidates && response.candidates[0]) {
                        const botMessage = response.candidates[0].content.parts[0].text;
                        this.addMessage(botMessage, 'bot');
                    } else {
                        throw new Error('Không nhận được phản hồi từ AI');
                    }
                } catch (error) {
                    this.hideTypingIndicator();
                    this.addErrorMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau. ' + error.message);
                } finally {
                    this.sendButton.disabled = false;
                }
            }

            async callGeminiAPI(message) {
                const requestBody = {
                    contents: [
                        {
                            parts: [
                                {
                                    text: message
                                }
                            ]
                        }
                    ],
                    generationConfig: {
                        temperature: 0.7,
                        topP: 0.8,
                        topK: 40,
                        maxOutputTokens: 2048,
                    },
                    safetySettings: [
                        {
                            category: "HARM_CATEGORY_HARASSMENT",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            category: "HARM_CATEGORY_HATE_SPEECH",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        },
                        {
                            category: "HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold: "BLOCK_MEDIUM_AND_ABOVE"
                        }
                    ]
                };

                const response = await fetch(`${this.apiUrl}?key=${this.apiKey}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(`API Error: ${response.status} - ${errorData.error?.message || 'Unknown error'}`);
                }

                return await response.json();
            }

            addMessage(text, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = sender === 'user' ? 'U' : 'AI';
                
                const content = document.createElement('div');
                content.className = 'message-content';
                
                const messageText = document.createElement('div');
                messageText.className = 'message-text';
                messageText.textContent = text;
                
                const messageTime = document.createElement('div');
                messageTime.className = 'message-time';
                messageTime.textContent = this.getCurrentTime();
                
                content.appendChild(messageText);
                content.appendChild(messageTime);
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(content);
                
                this.chatMessages.appendChild(messageDiv);
                this.scrollToBottom();
            }

            addErrorMessage(text) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = text;
                this.chatMessages.appendChild(errorDiv);
                this.scrollToBottom();
            }

            showTypingIndicator() {
                const typingDiv = document.createElement('div');
                typingDiv.className = 'message bot';
                typingDiv.id = 'typing-indicator';
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = 'AI';
                
                const content = document.createElement('div');
                content.className = 'message-content';
                
                const typingText = document.createElement('div');
                typingText.className = 'typing-indicator';
                typingText.innerHTML = `
                    <span>Đang nhập</span>
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                `;
                
                content.appendChild(typingText);
                typingDiv.appendChild(avatar);
                typingDiv.appendChild(content);
                
                this.chatMessages.appendChild(typingDiv);
                this.scrollToBottom();
            }

            hideTypingIndicator() {
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
            }

            scrollToBottom() {
                setTimeout(() => {
                    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
                }, 100);
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new GemAIChatBot();
        });
    </script>
</body>
</html>'''

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
        
        # Vẽ bóng đổ
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += int(self.shadow_offset)
        shadow_rect.y += int(self.shadow_offset)
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), 
                        (0, 0, shadow_rect.width, shadow_rect.height), 
                        border_radius=15)
        surface.blit(shadow_surface, shadow_rect)
        
        # Vẽ gradient background
        gradient_surface = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        self._draw_gradient_rect(gradient_surface, self.gradient_colors[0], self.gradient_colors[1], 
                               pygame.Rect(0, 0, scaled_rect.width, scaled_rect.height))
        surface.blit(gradient_surface, scaled_rect)
        
        # Vẽ viền
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
    
    # Nút GEM AI (tích hợp trực tiếp)
    ai_btn = ModernButton(
        x=560, y=390, w=200, h=60,
        text="GEM AI",
        callback=lambda: _open_integrated_gem_ai(game_state),
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
        {"name": "Mèo Vô Tri", "path": os.path.join(config.AVATAR_DIR, "avatar2.jpg"), "price": 300},
        {"name": "Cáo Tinh Nghịch", "path": os.path.join(config.AVATAR_DIR, "avatar3.jpg"), "price": 700},
        {"name": "Vô Cực", "path": os.path.join(config.AVATAR_DIR, "avatar4.jpg"), "price": 1000},
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


def _open_integrated_gem_ai(game_state: 'GameState') -> None:
    """Mở GEM AI tích hợp bằng Chrome/Edge app mode (ẩn thanh địa chỉ, ép kích thước nhỏ, chặn dịch)"""
    try:
        # Tạo file HTML tạm thời
        temp_dir = tempfile.gettempdir()
        html_file = os.path.join(temp_dir, "gem_ai_chat.html")

        # Ghi nội dung HTML vào file tạm
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(GEM_AI_HTML)

        # URL chuẩn
        file_url = f"file:///{html_file.replace(os.sep, '/')}"
        profile_dir = os.path.join(temp_dir, "gem_ai_profile")

        # Args chung cho Chrome/Edge
        browser_args = [
            f"--app={file_url}",
            "--new-window",
            "--window-size=500,600",
            "--window-position=200,50",   # 👈 vị trí cao hơn
            "--disable-features=TranslateUI",
        ]

        # Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ]
        for chrome_path in chrome_paths:
            if chrome_path and os.path.exists(chrome_path):
                subprocess.Popen([chrome_path] + browser_args + [f"--user-data-dir={profile_dir}_chrome"])
                game_state.show_message("GEM AI đã khởi động bằng Chrome!")
                return

        # Edge
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for edge_path in edge_paths:
            if os.path.exists(edge_path):
                subprocess.Popen([edge_path] + browser_args + [f"--user-data-dir={profile_dir}_edge"])
                game_state.show_message("GEM AI đã khởi động bằng Edge!")
                return

        # Fallback
        webbrowser.open(file_url)
        game_state.show_message("GEM AI đã mở trong trình duyệt!")

    except Exception as e:
        print(f"Lỗi: {e}")
        game_state.show_message("Không thể khởi động GEM AI!")


def toggle_sound() -> None:
    """Bật/tắt âm thanh"""
    if mixer.music.get_volume() > 0:
        mixer.music.set_volume(0)
        pygame.mixer.pause()
    else:
        mixer.music.set_volume(0.5)
        pygame.mixer.unpause()