import pygame
import time
import config # Import config for constants like WIDTH, HEIGHT

# Cooldown for button clicks (to prevent multiple rapid clicks)
_last_click_time = 0

class CircleButton:
    def __init__(self, x, y, radius, callback, color, hover_color=None, click_sound=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.callback = callback
        self.color = color
        self.hover_color = hover_color if hover_color else color
        self.click_sound = click_sound
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            distance = ((mouse_pos[0] - self.x)**2 + (mouse_pos[1] - self.y)**2)**0.5
            self.is_hovered = distance <= self.radius
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.click_sound:
                self.click_sound.play()
            self.callback()
class Button:
    def __init__(self, x, y, w, h, text, callback, color=config.COLORS["button"], border_radius=10, click_sound=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.border_radius = border_radius
        self.click_sound = click_sound

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = config.COLORS["hover"] if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=self.border_radius)
        
        if self.text:
            text_render = config.FONT.render(self.text, True, config.COLORS["black"])
            text_rect = text_render.get_rect(center=self.rect.center)
            surface.blit(text_render, text_rect)

    def handle_event(self, event):
        global _last_click_time
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            current_time = time.time()
            if current_time - _last_click_time > 0.3:
                if self.click_sound:
                    self.click_sound.play()
                self.callback()
                _last_click_time = current_time
                pygame.display.flip()  # Cập nhật màn hình ngay sau khi nhấn
                return True
        return False
def draw_button(surface, text, x, y, width, height, color, hover_color, action=None):
    # This function is now redundant if you use the Button class,
    # but I'll keep it as a wrapper if some parts of the code still rely on it directly.
    # It will need to accept `game_state` if the action needs it.
    # For now, it will simply return a Button object for consistent handling in main.py
    return Button(x, y, width, height, text, action, color)
def draw_rounded_rect(surface, color, rect, radius=20, border=0, border_color=None):
    """
    Vẽ hình chữ nhật bo góc
    - surface: bề mặt vẽ
    - color: màu fill
    - rect: (x, y, width, height)
    - radius: độ bo góc
    - border: độ dày viền
    - border_color: màu viền
    """
    x, y, w, h = rect
    rect = pygame.Rect(x, y, w, h)
    
    if border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)
    
    inner_rect = rect.inflate(-border*2, -border*2)
    pygame.draw.rect(surface, color, inner_rect, 0, border_radius=max(0, radius-border))
def draw_multiline_text(surface, text, x, y, font, color, max_width, line_spacing=10):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + i * (font.get_height() + line_spacing)))

    return len(lines)

def draw_text_centered(screen, text, x, y, font, color):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    screen.blit(rendered, rect)


def draw_feedback(surface, text, y, font=config.FONT, color=config.COLORS["text"]):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(config.WIDTH//2 + 50, y)) # Adjusted center for quiz feedback
    surface.blit(surf, rect)

def draw_message(surface, msg, font, colors, screen_width, screen_height):
    msg_box = pygame.Rect(screen_width // 2 - 200, screen_height - 70, 400, 50)
    pygame.draw.rect(surface, colors["white"], msg_box, border_radius=10)
    pygame.draw.rect(surface, colors["black"], msg_box, 2, border_radius=10)
    msg_surface = font.render(msg, True, colors["accent"])
    surface.blit(msg_surface, (msg_box.centerx - msg_surface.get_width()//2, msg_box.centery - msg_surface.get_height()//2))

