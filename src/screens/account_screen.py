import pygame
import config
import ui_elements
import os
import math  
from pygame import gfxdraw

click_sound = None


def set_click_sound(sound):
    global click_sound
    click_sound = sound

def draw_account(screen, font_title, font, colors, game_state):
    # Tạo background với độ trong suốt
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    # overlay.fill((235, 255, 235, 180))  # Màu xanh nhạt với độ trong suốt
    screen.blit(overlay, (0, 0))

    # Tính toán vị trí và kích thước mới cho card
    menu_width = 190
    available_width = config.WIDTH - menu_width
    card_width = 600
    card_x = menu_width + (available_width - card_width) // 2
    card_rect = pygame.Rect(card_x, 50, card_width, 500)
    
    pygame.draw.rect(screen, (190, 230, 190), card_rect, border_radius=20)
    pygame.draw.rect(screen, (90, 160, 90), card_rect, 2, border_radius=20)
    
    # Vẽ tiêu đề với hiệu ứng bóng đổ
    title_text = font_title.render("TÀI KHOẢN", True, (255, 255, 255))
    title_shadow = font_title.render("TÀI KHOẢN", True, (0, 0, 0, 100))
    
    # Tính toán vị trí tiêu đề (căn giữa card)
    title_x = card_x + (card_width - title_text.get_width()) // 2
    
    # Vẽ bóng đổ (3 lần với vị trí hơi lệch)
    screen.blit(title_shadow, (title_x + 2, 58))
    screen.blit(title_shadow, (title_x, 59))
    screen.blit(title_shadow, (title_x, 61))
    
    # Vẽ tiêu đề chính
    screen.blit(title_text, (title_x, 60))
    
    # Vẽ avatar (căn giữa card)
    avatar_x = card_x + (card_width // 2) - 60
    try:
        avatar_image = pygame.image.load(game_state.avatar_path)
        avatar_image = pygame.transform.scale(avatar_image, (120, 120))
        avatar_rect = avatar_image.get_rect(center=(avatar_x + 60, 180))
        screen.blit(avatar_image, avatar_rect)
    except Exception as e:
        print(f"Không thể tải avatar: {e}")
        pygame.draw.circle(screen, colors["accent"], (avatar_x + 60, 180), 60)
    
    # Danh sách thông tin tài khoản
    account_info = [
        {"label": "Streak:", "value": str(game_state.streak), "color": (255, 100, 0)},
        {"label": "Ngày hôm nay:", "value": game_state.last_day.strftime('%d/%m/%Y'), "color": colors["text"]},
        {"label": "Điểm:", "value": str(game_state.point), "color": (255, 215, 0)},
        {"label": "Năng lượng:", "value": f"{game_state.energy}/10", "color": (0, 200, 255)},
        {"label": "Thẻ bảo vệ:", "value": str(game_state.the_streak), "color": (100, 200, 100)},
    ]
    
    # Vẽ các thông tin tài khoản
    for index, info in enumerate(account_info):
        y_position = 250 + index * 60
        
        # Vẽ nhãn (căn trái với lề 100px từ card)
        label_surface = font.render(info["label"], True, colors["text"])
        screen.blit(label_surface, (card_x + 100, y_position))
        
        # Vẽ giá trị (căn trái với lề 300px từ card)
        value_surface = font.render(info["value"], True, info["color"])
        screen.blit(value_surface, (card_x + 300, y_position))
        
        # Vẽ thanh năng lượng đặc biệt
        if info["label"] == "Năng lượng:":
            energy_bar_background = pygame.Rect(card_x + 300, y_position + 5, 200, 20)
            pygame.draw.rect(screen, (50, 50, 70), energy_bar_background, border_radius=0)
            
            energy_filled_width = int(200 * (game_state.energy / 10))
            energy_filled_rect = pygame.Rect(card_x + 300, y_position + 5, energy_filled_width, 20)
            
            # Vẽ gradient màu
            if energy_filled_width > 0:
                for x in range(energy_filled_rect.width):
                    ratio = x / energy_filled_rect.width
                    red = int(255 * (1 - ratio))
                    green = int(255 * ratio)
                    gradient_color = (red, green, 0)
                    pygame.draw.line(
                        screen, 
                        gradient_color,
                        (energy_filled_rect.x + x, energy_filled_rect.y),
                        (energy_filled_rect.x + x, energy_filled_rect.y + energy_filled_rect.height)
                    )
            
            # Vẽ số năng lượng trên thanh
            energy_text = font.render(f"{game_state.energy}/10", True, (255, 255, 255))
            text_x = card_x + 400 - energy_text.get_width() // 2
            text_y = y_position + 5 + (20 - energy_text.get_height()) // 2
            screen.blit(energy_text, (text_x, text_y))
            draw_medal(screen, card_x + card_width - 100, 180, game_state.streak, font_title)

    
def draw_medal(screen, center_x, center_y, streak, font):
    import pygame.gfxdraw as gfxdraw
    import math  # Đảm bảo đã import math

    # Xác định cấp độ và màu sắc theo streak
    if streak < 2:
        return  # Không vẽ huy chương nếu streak quá thấp
    elif 2 <= streak <= 3:
        outer_color = (176, 141, 87)  # Đồng
        inner_color = (210, 180, 140)
        accent_color = (110, 90, 50)
        medal_type = "bronze"
    elif 4 <= streak <= 6:
        outer_color = (180, 180, 190)  # Bạc
        inner_color = (230, 230, 230)
        accent_color = (120, 120, 140)
        medal_type = "silver"
    elif streak >= 7:
        outer_color = (240, 200, 0)     # Vàng
        inner_color = (255, 230, 80)
        accent_color = (200, 160, 0)
        medal_type = "gold"
        
    radius = 55
    shadow_offset = 6

    # Vẽ bóng đổ nền
    gfxdraw.filled_circle(screen, center_x + shadow_offset, center_y + shadow_offset, radius + 4, (50, 50, 50, 80))

    # Vẽ vòng ngoài với hiệu ứng sáng tối
    for r in range(radius, 0, -2):
        shade = max(0, 255 - int(r * 2))
        color_layer = (*outer_color[:3], max(50, shade))
        gfxdraw.filled_circle(screen, center_x, center_y, r, color_layer[:3])

    # Vẽ vòng trong
    gfxdraw.filled_circle(screen, center_x, center_y, radius - 8, inner_color)

    # Viền nổi
    pygame.draw.circle(screen, accent_color, (center_x, center_y), radius - 8, 3)

    # Ruy băng phía dưới
    ribbon_width = 20
    ribbon_height = 70
    pygame.draw.rect(screen, (130, 0, 0), (center_x - ribbon_width // 2, center_y + radius - 10, ribbon_width, ribbon_height))
    pygame.draw.rect(screen, (200, 0, 0), (center_x - ribbon_width // 2, center_y + radius - 10, ribbon_width, ribbon_height), 2)

    # Vẽ biểu tượng thủ công
    if medal_type == "bronze":
        # Lá cây: 2 chiếc lá đối xứng
        for angle_deg in [0, 180]:
            angle_rad = math.radians(angle_deg)
            x_off = 15 * math.cos(angle_rad)
            y_off = 10 * math.sin(angle_rad)
            pygame.draw.ellipse(screen, (34, 139, 34), (center_x + x_off - 12, center_y + y_off - 6, 24, 12))
        pygame.draw.line(screen, (0, 100, 0), (center_x, center_y - 2), (center_x, center_y + 8), 2)

    elif medal_type == "silver":
        # Ngọn lửa nhiều lớp
        pygame.draw.ellipse(screen, (255, 100, 0), (center_x - 8, center_y - 15, 16, 30))
        pygame.draw.ellipse(screen, (255, 200, 0), (center_x - 4, center_y - 10, 8, 20))
        pygame.draw.ellipse(screen, (255, 255, 100), (center_x - 2, center_y - 6, 4, 10))

    elif medal_type == "gold":
        # Vương miện pixel-style
        pygame.draw.rect(screen, accent_color, (center_x - 15, center_y - 10, 30, 8))
        for peak_x in [center_x - 10, center_x, center_x + 10]:
            pygame.draw.polygon(screen, inner_color,
                                [(peak_x - 4, center_y - 10), (peak_x, center_y - 20), (peak_x + 4, center_y - 10)])
        # Đá quý
        jewel_positions = [(-10, -15), (0, -18), (10, -15)]
        jewel_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for (dx, dy), color in zip(jewel_positions, jewel_colors):
            pygame.draw.circle(screen, color, (center_x + dx, center_y + dy), 3)

    # Vẽ số streak dưới huy chương
    streak_text = font.render(str(streak), True, (30, 30, 30))
    text_rect = streak_text.get_rect(center=(center_x, center_y + radius + 15))
    screen.blit(streak_text, text_rect)
