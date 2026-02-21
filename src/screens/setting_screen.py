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
            font-family: 'Courier New', monospace;
            background: #3d2817;
            background-image: 
                repeating-linear-gradient(0deg, transparent, transparent 4px, rgba(0,0,0,.1) 4px, rgba(0,0,0,.1) 8px),
                repeating-linear-gradient(90deg, transparent, transparent 4px, rgba(0,0,0,.1) 4px, rgba(0,0,0,.1) 8px);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            image-rendering: pixelated;
        }

        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: #5c3d2e;
            border: 8px solid #2d1810;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 
                inset 0 0 0 4px #7a5436,
                8px 8px 0 rgba(0,0,0,0.3),
                0 0 0 2px #4a2f1f;
            position: relative;
        }

        .chat-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,.05) 2px, rgba(0,0,0,.05) 4px),
                repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(0,0,0,.05) 2px, rgba(0,0,0,.05) 4px);
            pointer-events: none;
        }

        .chat-header {
            background: #4a2f1f;
            padding: 20px;
            text-align: center;
            border-bottom: 4px solid #2d1810;
            box-shadow: inset 0 -2px 0 #7a5436;
            position: relative;
            z-index: 1;
        }

        .chat-header h1 {
            color: #f4e4c1;
            font-size: 28px;
            margin-bottom: 5px;
            font-weight: 700;
            text-shadow: 3px 3px 0 #2d1810;
            letter-spacing: 2px;
        }

        .chat-header p {
            color: #d4b896;
            font-size: 14px;
            text-shadow: 2px 2px 0 #2d1810;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            background: #f4e4c1;
            background-image: 
                repeating-linear-gradient(0deg, transparent, transparent 20px, rgba(139,90,43,.1) 20px, rgba(139,90,43,.1) 22px);
            position: relative;
            z-index: 1;
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
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #f4e4c1;
            font-size: 16px;
            flex-shrink: 0;
            border: 3px solid #2d1810;
            box-shadow: 3px 3px 0 rgba(0,0,0,0.3);
            image-rendering: pixelated;
        }

        .message.user .message-avatar {
            background: #8b5a2b;
        }

        .message.bot .message-avatar {
            background: #c19a6b;
        }

        .message-content {
            background: #fffef7;
            padding: 15px 20px;
            max-width: 70%;
            word-wrap: break-word;
            border: 3px solid #8b5a2b;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.2);
        }

        .message.user .message-content {
            background: #f9e4b7;
            border-color: #a0826d;
        }

        .message-text {
            color: #2d1810;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .message-time {
            font-size: 12px;
            color: #8b5a2b;
            margin-top: 8px;
        }

        .chat-input-container {
            padding: 20px;
            background: #4a2f1f;
            border-top: 4px solid #2d1810;
            position: relative;
            z-index: 1;
        }

        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .chat-input {
            flex: 1;
            background: #f4e4c1;
            border: 3px solid #2d1810;
            padding: 15px 20px;
            color: #2d1810;
            font-size: 16px;
            resize: none;
            outline: none;
            min-height: 50px;
            max-height: 120px;
            transition: all 0.1s ease;
            font-family: 'Courier New', monospace;
            box-shadow: inset 2px 2px 0 rgba(0,0,0,0.1);
        }

        .chat-input:focus {
            border-color: #8b5a2b;
            background: #fffef7;
        }

        .chat-input::placeholder {
            color: #a0826d;
        }

        .send-button {
            background: #c19a6b;
            border: 3px solid #2d1810;
            width: 50px;
            height: 50px;
            color: #2d1810;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.1s ease;
            font-size: 20px;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.3);
            image-rendering: pixelated;
        }

        .send-button:hover {
            transform: translate(2px, 2px);
            box-shadow: 2px 2px 0 rgba(0,0,0,0.3);
            background: #d4b896;
        }

        .send-button:active {
            transform: translate(4px, 4px);
            box-shadow: none;
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
            color: #8b5a2b;
            font-style: italic;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: #8b5a2b;
            animation: typingDot 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        .error-message {
            background: #d4a574;
            border: 3px solid #8b5a2b;
            color: #4a2f1f;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 4px 4px 0 rgba(0,0,0,0.2);
            font-weight: bold;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
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
            width: 12px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: #d4b896;
            border: 2px solid #8b5a2b;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: #8b5a2b;
            border: 2px solid #5c3d2e;
        }

        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: #a0826d;
        }

        @media (max-width: 768px) {
            .chat-container {
                width: 95%;
                height: 95vh;
                border-width: 6px;
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
                    <div class="message-text">Xin chào! Mình là GEM_AI – trợ lý ảo thông minh của bạn. Mình có thể giúp giải đáp mọi thắc mắc và đồng hành cùng bạn trong quá trình học. Hãy hỏi mình bất cứ điều gì nhé!</div>
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
                this.apiKey = null;
                this.apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
                this.chatMessages = document.getElementById('chatMessages');
                this.chatInput = document.getElementById('chatInput');
                this.sendButton = document.getElementById('sendButton');
                
                this.loadApiKey().then(() => this.init());
            }

            async loadApiKey() {
                if (this.apiKey) {
                    return;
                }
                try {
                    const res = await fetch('API_AI.json');
                    const data = await res.json();
                    if (data.API && data.API.startsWith("AI") && data.API.length > 20) {
                        this.apiKey = data.API.trim();
                        console.log("✅ API key loaded:", this.apiKey);
                    } else {
                        this.addErrorMessage("⚠️ API không hợp lệ trong API_AI.json");
                    }
                } catch {
                    this.addErrorMessage("⚠️ Không tìm thấy API_AI.json");
                }
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
                
                if (!this.apiKey) {
                    this.hideTypingIndicator();
                    this.addErrorMessage("⚠️ Chưa có API key hợp lệ.");
                    this.sendButton.disabled = false;
                    return;
                }

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
                    this.addErrorMessage('Xin lỗi, đã có lỗi xảy ra. ' + error.message);
                } finally {
                    this.sendButton.disabled = false;
                }
            }

            async callGeminiAPI(message) {
                const requestBody = {
                    contents: [
                        { parts: [ { text: message } ] }
                    ],
                    generationConfig: {
                        temperature: 0.7,
                        topP: 0.8,
                        topK: 40,
                        maxOutputTokens: 2048,
                    },
                    safetySettings: [
                        { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
                        { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
                        { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
                        { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_MEDIUM_AND_ABOVE" }
                    ]
                };

                const response = await fetch(`${this.apiUrl}?key=${this.apiKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
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
                if (typingIndicator) typingIndicator.remove();
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

# ===== BẮT ĐẦU PHẦN TỐI ƯU (thay thế từ ~dòng 552 trở xuống) =====

# Cache chung để tránh load/scale nhiều lần mỗi frame
_image_cache: Dict[str, pygame.Surface] = {}
_scaled_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}
_glow_cache: Dict[Tuple[int, int], pygame.Surface] = {}
_text_surface_cache: Dict[Tuple[str, int, Tuple[int, int, int]], pygame.Surface] = {}

# Tạo font nhỏ 1 lần (fallback nếu cần)
try:
    SMALL_FONT = pygame.font.Font(None, 20)
except Exception:
    SMALL_FONT = config.FONT  # fallback nhẹ

# Helper: load image 1 lần
def _load_image(path: str) -> Optional[pygame.Surface]:
    if not path:
        return None
    if path in _image_cache:
        return _image_cache[path]
    try:
        img = pygame.image.load(path).convert_alpha()
        _image_cache[path] = img
        return img
    except Exception:
        _image_cache[path] = None
        return None

# Helper: get scaled image with cache
def _get_scaled_image(path: str, w: int, h: int) -> Optional[pygame.Surface]:
    key = (path, w, h)
    if key in _scaled_cache:
        return _scaled_cache[key]
    img = _load_image(path)
    if img is None:
        _scaled_cache[key] = None
        return None
    scaled = pygame.transform.smoothscale(img, (w, h))
    _scaled_cache[key] = scaled
    return scaled

# Helper: create or get glow surface for size (cheap approximation)
def _get_glow_surface(diameter: int, color: Tuple[int, int, int]) -> pygame.Surface:
    key = (diameter, color[0] + color[1] + color[2])
    if key in _glow_cache:
        return _glow_cache[key]
    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    center = diameter // 2
    # tạo gradient vòng tròn đơn giản (ít vòng để nhanh)
    for i in range(8, 0, -1):
        alpha = int(12 * i)  # giảm alpha
        radius = int(center * (i / 8.0))
        pygame.draw.circle(surf, (*color, alpha), (center, center), radius)
    _glow_cache[key] = surf
    return surf

# Helper: cached text render
def _render_text_cached(text: str, font: pygame.font.Font, color: Tuple[int, int, int]) -> pygame.Surface:
    key = (text, id(font), color)
    if key in _text_surface_cache:
        return _text_surface_cache[key]
    surf = font.render(text, True, color)
    _text_surface_cache[key] = surf
    return surf

# Tối ưu ModernButton: cache icon surfaces tại thuộc tính để không load mỗi frame
class ModernButton(ui_elements.Button):
    def __init__(self, x: int, y: int, w: int, h: int, text: str,
                 callback: Callable, color: Tuple[int, int, int],
                 icon_path: Optional[str] = None, gradient_colors: Optional[List[Tuple[int, int, int]]] = None,
                 click_sound: Optional[pygame.mixer.Sound] = None):
        super().__init__(x, y, w, h, text, callback, color, 15, click_sound)
        self.icon_path = icon_path
        self.gradient_colors = gradient_colors or [color, (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))]
        # cache icon surface
        self._icon_surf = None
        if self.icon_path and os.path.exists(self.icon_path):
            img = _load_image(self.icon_path)
            if img:
                try:
                    icon_h = max(16, int(self.rect.height * 0.6))
                    self._icon_surf = pygame.transform.smoothscale(img, (icon_h, icon_h))
                except Exception:
                    self._icon_surf = None

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        # KHÔNG CÓ SCALE - chỉ vẽ button cố định
        rect = self.rect

        # Shadow cố định nhỏ
        shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 25), shadow.get_rect(), border_radius=12)
        surface.blit(shadow, (rect.x + 2, rect.y + 2))

        # Background color thay đổi khi hover
        bg_color = (min(255, self.color[0] + 20), min(255, self.color[1] + 20), min(255, self.color[2] + 20)) if is_hovered else self.color
        pygame.draw.rect(surface, bg_color, rect, border_radius=12)

        # Border
        border_color = (255, 255, 255, 180) if is_hovered else (200, 220, 200)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)

        # Icon
        if self._icon_surf:
            icon_rect = self._icon_surf.get_rect()
            icon_rect.left = rect.left + 12
            icon_rect.centery = rect.centery
            surface.blit(self._icon_surf, icon_rect)

        # Text
        if self.text:
            text_color = (255, 255, 255) if is_hovered else config.COLORS.get("text", (240, 240, 240))
            text_surf = _render_text_cached(self.text, config.FONT, text_color)
            text_pos = (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2)
            if self._icon_surf:
                text_pos = (rect.left + 12 + self._icon_surf.get_width() + 10, text_pos[1])
            surface.blit(text_surf, text_pos)


# SỬA LỖI: purchase với kiểm tra đủ điểm + tránh trừ nhiều lần nếu ko đủ
def _purchase_avatar(avatar: Dict, game_state):
    price = avatar.get("price", 0)
    if getattr(game_state, "point", 0) >= price:
        game_state.point -= price
        # chỉ append nếu chưa có
        if avatar["path"] not in game_state.owned_avatars:
            game_state.owned_avatars.append(avatar["path"])
        game_state.avatar_path = avatar["path"]
    else:
        # nhẹ: show message hoặc in log (game_state có thể có method show_message)
        try:
            game_state.show_message("Không đủ điểm để mua avatar.")
        except Exception:
            print("Không đủ điểm để mua avatar.")

def _use_avatar(avatar: Dict, game_state):
    if avatar["path"] in game_state.owned_avatars:
        game_state.avatar_path = avatar["path"]
    else:
        _purchase_avatar(avatar, game_state)


def draw_setting(screen: pygame.Surface, game_state: 'GameState', click_sound: pygame.mixer.Sound) -> List[ModernButton]:
    """Vẽ màn hình cài đặt chính hoặc mở các phần con như chọn nhạc"""
    # Nếu đang mở chọn nhạc -> chỉ vẽ phần nhạc, ẩn các nút khác
    if getattr(game_state, "temp_screen", None) == "music_selection":
        return draw_music_selection(screen, game_state, click_sound)

    global animation_time
    animation_time = pygame.time.get_ticks()

    # Tiêu đề
    title_surf = _render_text_cached("CÀI ĐẶT", config.FONT_TITLE, config.COLORS.get("accent", (200, 200, 255)))
    title_x = (screen.get_width() - title_surf.get_width()) // 2 - 150
    screen.blit(title_surf, (title_x, 80))

    # Avatar và info
    avatar_rect = pygame.Rect(100, 50, 120, 120)
    _draw_avatar_with_effects(screen, game_state, avatar_rect)

    user_info_x = 260
    _draw_user_info(screen, game_state, user_info_x, 180)

    # Tạo nút
    buttons: List[ModernButton] = []

    def make_btn(x, y, w, h, text, callback, color, icon_file=None, gradient=None):
        icon_path = os.path.join(config.ASSETS_DIR, "setting", icon_file) if icon_file else None
        if icon_path and not os.path.exists(icon_path):
            icon_path = None
        return ModernButton(x, y, w, h, text, callback, color, icon_path=icon_path, gradient_colors=gradient, click_sound=click_sound)

    avatar_btn = make_btn(600, 170, 200, 60, "Đổi Avatar", lambda: game_state.set_temp_screen("avatar_selection"), (100, 180, 255), "avatar_icon.png", [(100, 180, 255), (70, 150, 230)])
    sound_btn = make_btn(600, 270, 200, 60, "Âm Thanh", lambda: open_music_selection(game_state), (255, 180, 100), "sound_icon.png", [(255, 180, 100), (230, 150, 80)])
    ai_btn = make_btn(600, 370, 200, 60, "GEM AI", lambda: _open_integrated_gem_ai(game_state), (100, 220, 100), "ai_icon.png", [(100, 220, 100), (80, 200, 80)])
    back_btn = make_btn(100, config.HEIGHT - 120, 150, 50, "Quay lại", lambda: setattr(game_state, 'current_screen', "lesson"), (220, 100, 100), None, [(220, 100, 100), (190, 70, 70)])

    for b in [avatar_btn, sound_btn, ai_btn, back_btn]:
        b.draw(screen)
        buttons.append(b)

    return buttons

def draw_music_selection(screen: pygame.Surface, game_state: 'GameState', click_sound: pygame.mixer.Sound) -> List[ModernButton]:
    """Màn hình chọn nhạc nền - 1 trang, phong cách công tắc pixel với hiệu ứng đẹp mắt"""
    
    # Danh sách nhạc với màu riêng cho mỗi bài
    music_list = [
        {"name": "Không nhạc nền", "file": None, "color": (120, 120, 130)},
        {"name": "Nhạc Mặc Định", "file": "mu1.mp3", "color": (180, 100, 220)},
        {"name": "Chưa có tên", "file": "mu2.mp3", "color": (100, 180, 230)},
        {"name": "Chưa có tên", "file": "mu3.mp3", "color": (230, 150, 100)},
        {"name": "Chưa có tên", "file": "mu4.mp3", "color": (150, 200, 120)},
        {"name": "Chưa có tên", "file": "mu5.mp3", "color": (230, 120, 150)},
    ]

    # Tiêu đề
    title = _render_text_cached("CHỌN NHẠC NỀN", config.FONT_TITLE, (160, 100, 60))
    screen.blit(title, (265 - title.get_width() // 2, 40))

    buttons = []

    # ======= BỐ CỤC 2 CỘT TRÁI - PHẢI =======
    cols, rows = 2, 3
    card_width, card_height = 320, 85
    left_x = config.WIDTH // 2 - card_width - 60
    right_x = config.WIDTH // 2 + 60
    y_start = 150
    v_gap = 40

    mouse_pos = pygame.mouse.get_pos()

    # Lấy thông tin animation từ game_state (nếu chưa có thì khởi tạo)
    if not hasattr(game_state, '_music_btn_pressed'):
        game_state._music_btn_pressed = {}
    if not hasattr(game_state, '_music_btn_press_time'):
        game_state._music_btn_press_time = {}

    for i, music in enumerate(music_list[:cols * rows]):
        col = i % cols
        row = i // cols
        x = left_x if col == 0 else right_x
        y = y_start + row * (card_height + v_gap)
        rect = pygame.Rect(x, y, card_width, card_height)

        is_current = game_state.current_music == music["file"]
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Kiểm tra trạng thái nhấn
        btn_id = f"music_{i}"
        is_pressed = game_state._music_btn_pressed.get(btn_id, False)
        press_time = game_state._music_btn_press_time.get(btn_id, 0)
        
        # Animation offset khi nhấn (hiệu ứng công tắc lên xuống)
        current_time = pygame.time.get_ticks()
        press_offset = 0
        if is_pressed and current_time - press_time < 150:  # 150ms animation
            progress = (current_time - press_time) / 150
            press_offset = int(6 * (1 - abs(progress - 0.5) * 2))  # Lên 6px rồi xuống
        
        # Điều chỉnh vị trí theo animation
        draw_rect = pygame.Rect(rect.x, rect.y + press_offset, rect.width, rect.height)
        
        # === Màu nền theo trạng thái (mỗi nút có màu riêng) ===
        base_color = music["color"]
        
        if is_current:
            # Bật - sáng nhẹ hơn màu gốc, giữ tone
            bg_color = tuple(min(255, int(c * 1.1 + 15)) for c in base_color)
            inner_glow = True

        elif is_hovered:
            # Hover - sáng nhẹ
            bg_color = tuple(min(200, int(c * 1.15)) for c in base_color)
            inner_glow = False
        else:
            # Mặc định - giữ màu gốc
            bg_color = base_color
            inner_glow = False

        # === Vẽ bóng đổ (shadow) ===
        shadow_offset = 4 - press_offset  # Shadow giảm khi nhấn
        if shadow_offset > 0:
            shadow_rect = draw_rect.copy()
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (40, 30, 30), shadow_rect, border_radius=12)

        # === Vẽ viền ngoài dày (3D effect) ===
        border_col = tuple(min(255, c + 40) for c in bg_color)
        pygame.draw.rect(screen, border_col, draw_rect, border_radius=12)
        
        # === Vẽ nền chính ===
        inner_rect = draw_rect.inflate(-6, -6)
        pygame.draw.rect(screen, bg_color, inner_rect, border_radius=10)

        # === Hiệu ứng sáng bóng trên cạnh trên ===
        highlight = pygame.Surface((inner_rect.width, inner_rect.height // 2), pygame.SRCALPHA)
        for j in range(inner_rect.height // 2):
            alpha = int(50 * (1 - j / (inner_rect.height // 2)))
            pygame.draw.line(highlight, (255, 255, 255, alpha), (10, j), (inner_rect.width - 10, j))
        screen.blit(highlight, (inner_rect.x, inner_rect.y))

            

        # === Icon công tắc bên trái ===
        switch_x = draw_rect.x + 20
        switch_y = draw_rect.centery
        switch_width = 50
        switch_height = 26
        
        # Khung công tắc
        switch_rect = pygame.Rect(switch_x, switch_y - switch_height // 2, switch_width, switch_height)
        switch_bg = (100, 200, 100) if is_current else (80, 80, 90)
        pygame.draw.rect(screen, switch_bg, switch_rect, border_radius=13)
        pygame.draw.rect(screen, (220, 220, 220), switch_rect, 2, border_radius=13)
        
        # Nút trượt
        knob_radius = 10
        knob_x = switch_x + switch_width - 13 if is_current else switch_x + 13
        knob_y = switch_y
        pygame.draw.circle(screen, (240, 240, 250), (knob_x, knob_y), knob_radius)
        pygame.draw.circle(screen, (200, 200, 210), (knob_x, knob_y), knob_radius, 2)

        # === Text tên bài ===
        text_color = (40, 40, 50) if is_current else (240, 240, 250)
        name_surf = _render_text_cached(music["name"], config.FONT, text_color)
        text_x = switch_x + switch_width + 15
        screen.blit(name_surf, (text_x, draw_rect.centery - name_surf.get_height() // 2))

        # === Particle effects khi click ===
        if is_pressed and current_time - press_time < 300:
            particle_progress = (current_time - press_time) / 300
            num_particles = 8
            for p in range(num_particles):
                angle = (p / num_particles) * math.pi * 2
                distance = 30 * particle_progress
                px = draw_rect.centerx + math.cos(angle) * distance
                py = draw_rect.centery + math.sin(angle) * distance
                particle_alpha = int(255 * (1 - particle_progress))
                particle_size = int(4 * (1 - particle_progress * 0.5))
                
                if particle_size > 0:
                    particle_surf = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surf, (*base_color, particle_alpha), (particle_size, particle_size), particle_size)
                    screen.blit(particle_surf, (px - particle_size, py - particle_size))

        # === Click handler với animation ===
        def _on_click(m=music, gs=game_state, bid=btn_id):
            # Trigger animation
            gs._music_btn_pressed[bid] = True
            gs._music_btn_press_time[bid] = pygame.time.get_ticks()
            
            if m["file"] == gs.current_music:
                _select_music(None, gs)
            else:
                _select_music(m["file"], gs)

        click_btn = ModernButton(rect.x, rect.y, rect.width, rect.height, "", _on_click, (0, 0, 0))
        buttons.append(click_btn)

    # ======= NÚT QUAY LẠI (với hiệu ứng đẹp hơn) =======
    back_x = config.WIDTH - 230
    back_y = config.HEIGHT - 110
    back_btn_rect = pygame.Rect(back_x, back_y, 150, 50)
    is_back_hovered = back_btn_rect.collidepoint(mouse_pos)
    
    # Hiệu ứng hover cho nút quay lại
    back_color = (220, 100, 80) if is_back_hovered else (200, 90, 70)
    back_shadow = pygame.Rect(back_x, back_y + 3, 150, 50)
    pygame.draw.rect(screen, (100, 45, 35), back_shadow, border_radius=10)
    pygame.draw.rect(screen, back_color, back_btn_rect, border_radius=10)
    pygame.draw.rect(screen, (250, 200, 180), back_btn_rect, 3, border_radius=10)
    
    back_text = _render_text_cached("Quay lại", config.FONT, (255, 255, 255))
    screen.blit(back_text, (back_btn_rect.centerx - back_text.get_width() // 2, 
                            back_btn_rect.centery - back_text.get_height() // 2))
    
    back_btn = ModernButton(
        back_x, back_y, 150, 50,
        "Quay lại",
        lambda: setattr(game_state, "temp_screen", None),
        (200, 90, 70),
        click_sound=click_sound
    )
    buttons.append(back_btn)

    return buttons


def _preview_music(music_file: str) -> None:
    """Nghe thử nhạc"""
    try:
        music_path = os.path.join(config.ASSETS_DIR, "audio", music_file)
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(0)
        else:
            print(f"Không tìm thấy file: {music_file}")
    except Exception as e:
        print(f"Lỗi nghe thử nhạc: {e}")

def _select_music(music_file: str, game_state) -> None:
    """Chọn nhạc nền chính (hỗ trợ tắt nhạc nếu chọn None)"""
    try:
        if not music_file:
            game_state.current_music = None
            pygame.mixer.music.stop()
            return

        music_path = os.path.join(config.ASSETS_DIR, "audio", music_file)
        if os.path.exists(music_path):
            game_state.current_music = music_file
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(game_state.music_volume)
            pygame.mixer.music.play(-1)
        else:
            print(f"Không tìm thấy file: {music_file}")
    except Exception as e:
        print(f"Lỗi chọn nhạc: {e}")

def draw_avatar_selection(screen: pygame.Surface, game_state: 'GameState', click_sound: pygame.mixer.Sound) -> List[ModernButton]:
    """Màn hình chọn avatar 2x2 - tối ưu: tránh tạo font mới, cache ảnh scaled"""
    title = _render_text_cached("CHỌN AVATAR", config.FONT_TITLE, config.COLORS.get("accent", (200, 200, 255)))
    screen.blit(title, (100, 50))

    avatar_options = [
        {"name": "Sách Thông Thái", "path": os.path.join(config.AVATAR_DIR, "avatar1.jpg"), "price": 100},
        {"name": "Mèo Vô Tri", "path": os.path.join(config.AVATAR_DIR, "avatar2.jpg"), "price": 300},
        {"name": "Cáo Tinh Nghịch", "path": os.path.join(config.AVATAR_DIR, "avatar3.jpg"), "price": 700},
        {"name": "Vô Cực", "path": os.path.join(config.AVATAR_DIR, "avatar4.jpg"), "price": 1000},
    ]

    buttons: List[ModernButton] = []
    
    # THAY ĐỔI: Tăng chiều rộng card và giảm khoảng cách dọc
    card_width, card_height = 350, 110  # Tăng từ 280 lên 350
    cols, rows = 2, 2
    h_gap = max(20, (config.WIDTH - cols * card_width) // (cols + 1))  # Tăng khoảng cách ngang một chút
    v_gap = 40  # GIẢM từ max(12, (config.HEIGHT - rows * card_height) // (rows + 1)) xuống 40px cố định

    mouse_pos = pygame.mouse.get_pos()

    for i, avatar in enumerate(avatar_options):
        col = i % cols
        row = i // cols
        x = h_gap + col * (card_width + h_gap)
        y = 160 + row * (card_height + v_gap)  # Tăng y bắt đầu từ 120 lên 140 để có thêm chút không gian
        card_rect = pygame.Rect(x, y, card_width, card_height)

        owned = avatar["path"] in game_state.owned_avatars
        current = game_state.avatar_path == avatar["path"]
        is_hovered = card_rect.collidepoint(mouse_pos)

        # background
        bg_color = ((150, 110, 90)) if not is_hovered else ((128, 85, 66))
        border_color = (128, 85, 66) if current else ((128, 85, 66) if is_hovered else (128, 85, 66))
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, card_rect, 4 if (current or is_hovered) else 3, border_radius=8)

        # avatar image left
        img_size = card_height - 24
        img_rect = pygame.Rect(x + 12, y + (card_height - img_size) // 2, img_size, img_size)
        scaled = _get_scaled_image(avatar["path"], img_size, img_size)
        if scaled:
            screen.blit(scaled, img_rect)
        else:
            pygame.draw.rect(screen, (150, 150, 150), img_rect, border_radius=6)

        # text info (cache renders) - với card rộng hơn, text sẽ có đủ chỗ
        name_font = config.FONT
        name_surf = _render_text_cached(avatar["name"], name_font, config.COLORS.get("white", (240, 240, 240)))
        screen.blit(name_surf, (img_rect.right + 12, y + 16))

        if current:
            status_text = "ĐANG DÙNG"
            status_color = (255, 215, 0)
        elif owned:
            status_text = "ĐÃ SỞ HỮU"
            status_color = (50, 180, 50)
        else:
            status_text = f"{avatar['price']} ĐIỂM"
            status_color = (220, 120, 50)

        status_surf = _render_text_cached(status_text, config.FONT, status_color)
        screen.blit(status_surf, (img_rect.right + 12, y + 55))

        # overlay click area button (invisible) - use one ModernButton per card (no heavy resources)
        if owned:
            cb = (lambda a=avatar: _use_avatar(a, game_state))
        else:
            cb = (lambda a=avatar: _purchase_avatar(a, game_state))

        btn = ModernButton(x, y, card_width, card_height, "", cb, (0, 0, 0))
        buttons.append(btn)

    # back button
    back_btn = ModernButton(config.WIDTH - 250, config.HEIGHT - 120, 150, 50, "Quay lại", lambda: game_state.set_temp_screen(None),
                            (220, 100, 100), click_sound=click_sound)
    buttons.append(back_btn)
    back_btn.draw(screen)

    return buttons


def _draw_gradient_background(surface: pygame.Surface, color1: Tuple[int, int, int], color2: Tuple[int, int, int], rect: pygame.Rect) -> None:
    """Vẽ gradient but optimized: vẽ mỗi vài px thay vì mỗi line khi rect cao"""
    height = rect.height
    # reduce steps for large heights to speed up
    steps = max(32, min(256, height))
    for i in range(steps):
        y = rect.y + int((i / steps) * height)
        ratio = i / (steps - 1)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        # draw rect of computed band
        band_h = int(height / steps) + 1
        pygame.draw.rect(surface, (r, g, b), (rect.x, y, rect.width, band_h))


def _draw_glass_panel(surface: pygame.Surface, rect: pygame.Rect, base_color: Tuple[int, int, int], alpha: int) -> None:
    """Vẽ panel kính mờ - tái sử dụng surface tạm, nhưng tránh nhiều draw calls"""
    glass = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # fill + thin border
    glass.fill((*base_color, alpha))
    pygame.draw.rect(glass, (255, 255, 255, 40), (0, 0, rect.width, rect.height), 2, border_radius=16)
    # subtle top highlight
    pygame.draw.rect(glass, (255, 255, 255, 30), (0, 0, rect.width, rect.height // 3), 0, border_radius=16)
    surface.blit(glass, rect)


def _draw_avatar_with_effects(surface: pygame.Surface, game_state: 'GameState', rect: pygame.Rect) -> None:
    """Vẽ avatar + glow (glow được cache) - light-weight"""
    # glow
    accent = config.COLORS.get("accent", (100, 180, 255))
    diameter = rect.width + 40
    glow = _get_glow_surface(diameter, accent)
    if glow:
        surface.blit(glow, (rect.centerx - diameter // 2, rect.centery - diameter // 2), special_flags=0)

    # frame
    pygame.draw.circle(surface, (255, 255, 255), rect.center, rect.width // 2 + 2)

    # image scaled and masked quickly
    img = _get_scaled_image(game_state.avatar_path, rect.width - 10, rect.height - 10)
    if img:
        # circular mask: faster is to blit image then draw a circle border and a small overlay
        surface.blit(img, (rect.x + 5, rect.y + 5))
        # subtle overlay if wanted (cheap)
        if hasattr(game_state, "avatar_outline") and game_state.avatar_path == getattr(game_state, "avatar_path"):
            pass
    else:
        # fallback placeholder
        pygame.draw.circle(surface, config.COLORS.get("button", (150, 150, 150)), rect.center, rect.width // 2 - 5)


def _draw_user_info(surface: pygame.Surface, game_state: 'GameState', x: int, y: int) -> None:
    """Vẽ thông tin người dùng - dùng cached text"""
    username = _render_text_cached("Người chơi", config.FONT_TITLE, config.COLORS.get("text", (240, 240, 240)))
    surface.blit(username, (x - 100, y + 45))

    points = _render_text_cached(f"Điểm: {game_state.point}", config.FONT, config.COLORS.get("text", (240, 240, 240)))
    surface.blit(points, (x - 100, y + 120))

    energy = _render_text_cached(f"Năng lượng: {game_state.energy}/10", config.FONT, config.COLORS.get("text", (240, 240, 240)))
    surface.blit(energy, (x - 100, y + 160))

    streak = _render_text_cached(f"Streak: {game_state.streak} ngày", config.FONT, config.COLORS.get("text", (240, 240, 240)))
    surface.blit(streak, (x - 100, y + 200))


def _draw_avatar_card_status(surface: pygame.Surface, avatar: Dict, rect: pygame.Rect, owned: bool, current: bool) -> None:
    """Vẽ card status (giữ đơn giản và nhanh)"""
    if current:
        card_color = (60, 160, 60)
        border_color = (255, 220, 50)
    elif owned:
        card_color = (100, 180, 100)
        border_color = (200, 200, 200)
    else:
        card_color = (200, 200, 200)
        border_color = (150, 150, 150)

    pygame.draw.rect(surface, card_color, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)

    img_size = int(rect.height * 0.6)
    img_rect = pygame.Rect(rect.centerx - img_size // 2, rect.y + 8, img_size, img_size)
    scaled = _get_scaled_image(avatar["path"], img_size, img_size)
    if scaled:
        surface.blit(scaled, img_rect)
    else:
        pygame.draw.rect(surface, (150, 150, 150), img_rect, border_radius=6)

    name = SMALL_FONT.render(avatar["name"], True, config.COLORS.get("text", (240, 240, 240)))
    surface.blit(name, (rect.centerx - name.get_width() // 2, img_rect.bottom + 5))

    if current:
        status_text, status_color = "ĐANG DÙNG", (255, 215, 0)
    elif owned:
        status_text, status_color = "ĐÃ SỞ HỮU", (50, 200, 50)
    else:
        status_text, status_color = f"{avatar.get('price', 0)} ĐIỂM", (230, 140, 50)

    status = SMALL_FONT.render(status_text, True, status_color)
    tag_rect = pygame.Rect(0, 0, status.get_width() + 12, status.get_height() + 6)
    tag_rect.centerx = rect.centerx
    tag_rect.y = rect.bottom - 25
    pygame.draw.rect(surface, (245, 245, 245), tag_rect, border_radius=6)
    pygame.draw.rect(surface, status_color, tag_rect, 1, border_radius=6)
    surface.blit(status, (tag_rect.centerx - status.get_width() // 2, tag_rect.y + 3))


def _open_integrated_gem_ai(game_state: 'GameState') -> None:
    try:
        temp_dir = tempfile.gettempdir()
        html_file = os.path.join(temp_dir, "gem_ai_chat.html")

        # Đọc API key từ file JSON
        api_file = os.path.join(os.path.dirname(__file__), "API_AI.json")
        api_key = None
        if os.path.exists(api_file):
            with open(api_file, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                api_key = data.get("API", "")

        # Ghi HTML ra file, chèn API key trực tiếp
        html_content = GEM_AI_HTML.replace("this.apiKey = null;", f"this.apiKey = '{api_key}';")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        file_url = f"file:///{html_file.replace(os.sep, '/')}"


        profile_dir = os.path.join(temp_dir, "gem_ai_profile")
        browser_args = [
            f"--app={file_url}",
            "--new-window",
            "--window-size=500,600",
            "--window-position=200,50",
            "--disable-features=TranslateUI",
        ]

        # tìm Chrome/Edge nhanh hơn: trả về sớm khi tìm thấy
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ]
        for chrome_path in chrome_paths:
            if chrome_path and os.path.exists(chrome_path):
                subprocess.Popen([chrome_path] + browser_args + [f"--user-data-dir={profile_dir}_chrome"])
                return

        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for edge_path in edge_paths:
            if os.path.exists(edge_path):
                subprocess.Popen([edge_path] + browser_args + [f"--user-data-dir={profile_dir}_edge"])
                return

        # fallback: mở bằng webbrowser (hệ điều hành quản lý)
        webbrowser.open(file_url)

    except Exception as e:
        print(f"Lỗi khi mở GEM AI: {e}")
        try:
            game_state.show_message("Không thể khởi động GEM AI!")
        except Exception:
            pass


def open_music_selection(game_state):
    """Mở màn hình chọn nhạc"""
    game_state.set_temp_screen("music_selection")
