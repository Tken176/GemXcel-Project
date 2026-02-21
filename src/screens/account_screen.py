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
    menu_width = 190
    # Tính toán vị trí và kích thước mới cho card
    available_width = config.WIDTH - menu_width
    card_width = 600
    card_x = menu_width + (available_width - card_width) // 2
    card_rect = pygame.Rect(card_x, 50, card_width, 500)
    
    
    # Vẽ tiêu đề với hiệu ứng bóng đổ
    title_text = font_title.render("TÀI KHOẢN", True, (255, 255, 255))
    title_shadow = font_title.render("TÀI KHOẢN", True, (0, 0, 0, 100))
    
    # Tính toán vị trí tiêu đề (căn giữa card)
    title_x = 140
    
    # Vẽ bóng đổ (3 lần với vị trí hơi lệch)
    screen.blit(title_shadow, (title_x + 2, 58))
    screen.blit(title_shadow, (title_x, 59))
    screen.blit(title_shadow, (title_x, 61))
    
    # Vẽ tiêu đề chính
    screen.blit(title_text, (title_x, 60))
    
    # Vẽ avatar (căn giữa card)
    avatar_x = card_x + (card_width // 2) - 5
    try:
        avatar_image = pygame.image.load(game_state.avatar_path)
        avatar_image = pygame.transform.scale(avatar_image, (120, 120))
        avatar_rect = avatar_image.get_rect(center=(avatar_x + 60, 180))
        screen.blit(avatar_image, avatar_rect)
    except Exception as e:
        print(f"Không thể tải avatar: {e}")
        pygame.draw.circle(screen, colors["accent"], (avatar_x + 60, 180), 100)
    
    # Danh sách thông tin tài khoản
    account_info = [
        {"label": "Streak:", "value": str(game_state.streak), "color": (255, 100, 0)},
        {"label": "Ngày hôm nay:", "value": game_state.last_day.strftime('%d/%m/%Y'), "color": colors["text"]},
        {"label": "Điểm:", "value": str(game_state.point), "color": (210, 150, 0)},
        {"label": "Năng lượng:", "value": f"{game_state.energy}/10", "color": (0, 200, 255)},
        {"label": "Thẻ bảo vệ:", "value": str(game_state.the_streak), "color": (100, 200, 100)},
    ]
    
    # Vẽ các thông tin tài khoản
    for index, info in enumerate(account_info):
        y_position = 200 + index * 60
        
        # Vẽ nhãn (căn trái với lề 100px từ card)
        label_surface = font.render(info["label"], True, colors["text"])
        screen.blit(label_surface, (100, y_position))
        
        # Vẽ giá trị (căn trái với lề 300px từ card)
        value_surface = font.render(info["value"], True, info["color"])
        screen.blit(value_surface, (300, y_position))
        
    # Vẽ huy chương (truyền game_state vào)
    draw_medal(screen, card_x + card_width - 100, 180, game_state, font_title)
    
    # Vẽ khung thành tựu ở góc phần tư thứ 4
    draw_achievement_box(screen, game_state, font, font_title)

    
def draw_medal(screen, center_x, center_y, game_state, font):
    """Vẽ huy chương đẹp với hiệu ứng đung đưa như trong gió"""
    import pygame.gfxdraw as gfxdraw
    import math

    streak = game_state.streak
    
    # Xác định cấp độ và màu sắc theo streak
    if streak < 2:
        return  # Không vẽ huy chương nếu streak quá thấp
    elif 2 <= streak <= 5:
        outer_color = (205, 127, 50)  # Đồng
        inner_color = (255, 198, 140)
        accent_color = (139, 90, 43)
        shine_color = (255, 220, 177)
        medal_type = "bronze"
    elif 6 <= streak <= 14:
        outer_color = (169, 169, 169)  # Bạc
        inner_color = (240, 240, 240)
        accent_color = (105, 105, 105)
        shine_color = (255, 255, 255)
        medal_type = "silver"
    elif streak >= 15:
        outer_color = (218, 165, 32)     # Vàng
        inner_color = (255, 223, 0)
        accent_color = (184, 134, 11)
        shine_color = (255, 250, 205)
        medal_type = "gold"
        
    radius = 55
    shadow_offset = 6

    # Hiệu ứng đung đưa như trong gió
    time = pygame.time.get_ticks() / 1000.0
    
    # Đung đưa nhẹ theo trục X và Y
    swing_x = 3 * math.sin(time * 1.5)
    swing_y = 2 * math.sin(time * 2.3 + 0.5)
    
    # Xoay nhẹ như đang lắc lư
    rotation_angle = 4 * math.sin(time * 1.8)
    
    # Hiệu ứng nhấp nháy nhẹ
    pulse_scale = 1.0 + 0.03 * math.sin(time * 2.5)
    
    # Áp dụng offset đung đưa
    medal_x = center_x + swing_x
    medal_y = center_y + swing_y

    # Vẽ bóng đổ mềm mại hơn
    for i in range(5):
        shadow_alpha = 20 - i * 3
        gfxdraw.filled_circle(screen, 
                             int(medal_x + shadow_offset), 
                             int(medal_y + shadow_offset + i), 
                             int(radius + 6 - i), 
                             (0, 0, 0, shadow_alpha))

    # Vẽ vòng ngoài với gradient đẹp hơn
    for r in range(radius, int(radius * 0.7), -1):
        progress = (radius - r) / (radius * 0.3)
        # Tạo gradient từ tối đến sáng
        color_r = int(outer_color[0] + (inner_color[0] - outer_color[0]) * progress)
        color_g = int(outer_color[1] + (inner_color[1] - outer_color[1]) * progress)
        color_b = int(outer_color[2] + (inner_color[2] - outer_color[2]) * progress)
        gfxdraw.filled_circle(screen, int(medal_x), int(medal_y), 
                             int(r * pulse_scale), (color_r, color_g, color_b))

    # Vẽ vòng trong sáng bóng
    inner_radius = int((radius - 10) * pulse_scale)
    gfxdraw.filled_circle(screen, int(medal_x), int(medal_y), inner_radius, inner_color)

    # Vẽ ánh sáng phản chiếu (highlight)
    highlight_offset_x = -radius // 4
    highlight_offset_y = -radius // 3
    for i in range(15, 0, -3):
        alpha = int(80 * (i / 15))
        gfxdraw.filled_circle(screen, 
                             int(medal_x + highlight_offset_x), 
                             int(medal_y + highlight_offset_y), 
                             i, (*shine_color, alpha))

    # Viền nổi 3D
    pygame.draw.circle(screen, accent_color, (int(medal_x), int(medal_y)), 
                      inner_radius, 4)
    pygame.draw.circle(screen, shine_color, (int(medal_x), int(medal_y)), 
                      inner_radius - 2, 2)

    # Ruy băng đẹp hơn với hiệu ứng gió
    ribbon_width = 24
    ribbon_height = 75
    ribbon_y_start = int(medal_y + radius - 5)
    
    # Tạo hiệu ứng gió cho ruy băng
    wave1 = 2 * math.sin(time * 3 + 0)
    wave2 = 2 * math.sin(time * 3 + 0.5)
    
    # Ruy băng trái
    left_ribbon = [
        (int(medal_x - ribbon_width//2 + wave1), ribbon_y_start),
        (int(medal_x - ribbon_width//2 + wave2), ribbon_y_start + ribbon_height//2),
        (int(medal_x - ribbon_width//2 - 3 + wave1), ribbon_y_start + ribbon_height),
        (int(medal_x - 2), ribbon_y_start + ribbon_height - 10),
    ]
    pygame.draw.polygon(screen, (180, 0, 0), left_ribbon)
    pygame.draw.polygon(screen, (220, 0, 0), left_ribbon, 2)
    
    # Ruy băng phải
    right_ribbon = [
        (int(medal_x + ribbon_width//2 + wave1), ribbon_y_start),
        (int(medal_x + ribbon_width//2 + wave2), ribbon_y_start + ribbon_height//2),
        (int(medal_x + ribbon_width//2 + 3 + wave1), ribbon_y_start + ribbon_height),
        (int(medal_x + 2), ribbon_y_start + ribbon_height - 10),
    ]
    pygame.draw.polygon(screen, (180, 0, 0), right_ribbon)
    pygame.draw.polygon(screen, (220, 0, 0), right_ribbon, 2)

    # Vẽ biểu tượng thủ công đẹp hơn
    if medal_type == "bronze":
        # Cành lá đơn giản nhưng đẹp
        for angle_deg in [-25, 25]:
            angle_rad = math.radians(angle_deg + rotation_angle)
            x_off = 18 * math.cos(angle_rad)
            y_off = 12 * math.sin(angle_rad)
            # Lá
            leaf_points = [
                (medal_x + x_off - 8, medal_y + y_off),
                (medal_x + x_off - 3, medal_y + y_off - 8),
                (medal_x + x_off + 8, medal_y + y_off),
                (medal_x + x_off - 3, medal_y + y_off + 8),
            ]
            pygame.draw.polygon(screen, (46, 125, 50), leaf_points)
            pygame.draw.polygon(screen, (27, 94, 32), leaf_points, 2)
        # Thân cây
        pygame.draw.line(screen, (101, 67, 33), (medal_x, medal_y - 5), 
                        (medal_x, medal_y + 10), 3)

    elif medal_type == "silver":
        # Ngọn lửa đẹp hơn với nhiều lớp
        flame_wave = 3 * math.sin(time * 6)
        
        # Lớp ngoài - cam đỏ
        flame_outer = [
            (medal_x, medal_y - 25 + flame_wave),
            (medal_x - 12, medal_y - 5),
            (medal_x - 8, medal_y + 10),
            (medal_x, medal_y + 5),
            (medal_x + 8, medal_y + 10),
            (medal_x + 12, medal_y - 5),
        ]
        pygame.draw.polygon(screen, (255, 69, 0), flame_outer)
        
        # Lớp giữa - cam vàng
        flame_middle = [
            (medal_x, medal_y - 20 + flame_wave),
            (medal_x - 8, medal_y - 2),
            (medal_x - 5, medal_y + 8),
            (medal_x, medal_y + 4),
            (medal_x + 5, medal_y + 8),
            (medal_x + 8, medal_y - 2),
        ]
        pygame.draw.polygon(screen, (255, 165, 0), flame_middle)
        
        # Lớp trong - vàng sáng
        flame_inner = [
            (medal_x, medal_y - 15 + flame_wave),
            (medal_x - 4, medal_y),
            (medal_x, medal_y + 6),
            (medal_x + 4, medal_y),
        ]
        pygame.draw.polygon(screen, (255, 255, 100), flame_inner)

    elif medal_type == "gold":
        # Vương miện sang trọng
        crown_bob = 2 * math.sin(time * 3)
        crown_y = medal_y - 10 + crown_bob
        
        # Đế vương miện
        crown_base = pygame.Rect(medal_x - 18, crown_y, 36, 10)
        pygame.draw.rect(screen, accent_color, crown_base, border_radius=2)
        pygame.draw.rect(screen, inner_color, crown_base.inflate(-4, -4), border_radius=2)
        
        # 3 đỉnh vương miện
        for i, peak_x in enumerate([medal_x - 12, medal_x, medal_x + 12]):
            offset = 2 * math.sin(time * 4 + i * 0.5)
            peak_points = [
                (peak_x - 5, crown_y),
                (peak_x, crown_y - 15 + offset),
                (peak_x + 5, crown_y),
            ]
            pygame.draw.polygon(screen, inner_color, peak_points)
            pygame.draw.polygon(screen, accent_color, peak_points, 2)
            
            # Đá quý trên đỉnh
            jewel_colors = [(255, 0, 127), (0, 191, 255), (50, 205, 50)]
            jewel_glow = int(200 + 55 * math.sin(time * 5 + i))
            pygame.draw.circle(screen, jewel_colors[i], 
                             (int(peak_x), int(crown_y - 13 + offset)), 4)
            gfxdraw.filled_circle(screen, int(peak_x), int(crown_y - 13 + offset), 
                                 3, (*jewel_colors[i], jewel_glow))

    # Vẽ số streak với hiệu ứng đẹp
    streak_glow = int(255 * (0.8 + 0.2 * math.sin(time * 4)))
    
    # Bóng đổ cho text
    streak_shadow = font.render(str(streak), True, (0, 0, 0))
    shadow_rect = streak_shadow.get_rect(center=(int(medal_x + 1), int(medal_y + 1)))
    screen.blit(streak_shadow, shadow_rect)
    
    # Text chính
    streak_text = font.render(str(streak), True, (255, 255, 255, streak_glow))
    text_rect = streak_text.get_rect(center=(int(medal_x), int(medal_y)))
    screen.blit(streak_text, text_rect)


def draw_achievement_box(screen, game_state, font, font_title):
    """Vẽ khung thành tựu đẹp mắt với hiệu ứng động"""
    
    collected = {g["id"] for g in game_state.collected_gems}
    count = len(collected)

    # Xác định cấp độ và màu sắc
    if 3 <= count <= 5:
        title = "NEWBIE"
        subtitle = "lấp lánh"
        border_color = (192, 192, 192)  # Bạc
        bg_color = (245, 245, 250)
        text_color = (50, 50, 70)
        glow_color = (192, 192, 192, 40)
        icon = "C"  # Star emoji
        icon_color = (150, 150, 160)
        particles_color = (200, 200, 210)
    elif 6 <= count <= 8:
        title = "HUNTER"
        subtitle = "đá quý"
        border_color = (255, 215, 0)  # Vàng
        bg_color = (255, 250, 235)
        text_color = (80, 60, 0)
        glow_color = (255, 215, 0, 50)
        icon = "B"  # Diamond emoji
        icon_color = (255, 180, 0)
        particles_color = (255, 230, 100)
    elif count > 8:
        title = "MASTER"
        subtitle = "sưu tầm"
        border_color = (220, 20, 60)  # Đỏ hồng
        bg_color = (255, 240, 245)
        text_color = (120, 20, 40)
        glow_color = (220, 20, 60, 60)
        icon = "A"  # Crown emoji
        icon_color = (200, 0, 40)
        particles_color = (255, 100, 150)
    else:
        return  # Không vẽ nếu chưa đạt thành tựu

    # Hiệu ứng động
    time = pygame.time.get_ticks() / 1000.0
    pulse_scale = 1.0 + 0.015 * math.sin(time * 2.5)
    glow_intensity = int(50 + 30 * math.sin(time * 3))
    
    # Vị trí góc dưới bên phải
    box_width = 310
    box_height = 160
    margin = 30
    box_x = config.WIDTH - box_width - margin - 80
    box_y = config.HEIGHT - box_height - margin - 90
    
    # Vẽ particles bay xung quanh
    for i in range(8):
        particle_angle = time * 0.5 + i * (math.pi / 4)
        particle_distance = 150 + 20 * math.sin(time * 2 + i)
        particle_x = box_x + box_width // 2 + particle_distance * math.cos(particle_angle)
        particle_y = box_y + box_height // 2 + particle_distance * math.sin(particle_angle)
        particle_alpha = int(100 + 100 * math.sin(time * 3 + i))
        
        particle_size = 3 + 2 * math.sin(time * 4 + i)
        draw_sparkle(screen, int(particle_x), int(particle_y), 
                    (*particles_color, particle_alpha), int(particle_size))
    
    # Vẽ hiệu ứng phát sáng nhiều lớp
    for i in range(5):
        glow_offset = 10 - i * 2
        glow_rect = pygame.Rect(box_x - glow_offset, box_y - glow_offset, 
                                box_width + glow_offset * 2, box_height + glow_offset * 2)
        glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        current_alpha = max(10, glow_intensity - i * 10)
        current_glow = (*glow_color[:3], current_alpha)
        pygame.draw.rect(glow_surface, current_glow, glow_surface.get_rect(), border_radius=20)
        screen.blit(glow_surface, glow_rect)
    
    # Vẽ nền chính với gradient
    main_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    
    # Gradient effect đẹp hơn
    for i in range(box_height):
        progress = i / box_height
        # Gradient từ sáng xuống tối nhẹ
        gradient_factor = int(15 * progress)
        color_layer = (max(0, bg_color[0] - gradient_factor), 
                      max(0, bg_color[1] - gradient_factor), 
                      max(0, bg_color[2] - gradient_factor))
        pygame.draw.line(screen, color_layer, 
                        (box_x + 15, box_y + i), 
                        (box_x + box_width - 15, box_y + i))
    
    pygame.draw.rect(screen, bg_color, main_rect, border_radius=18)
    
    # Viền vàng/bạc/đỏ với hiệu ứng sáng động
    border_alpha = int(255 * (0.9 + 0.1 * math.sin(time * 5)))
    pygame.draw.rect(screen, (*border_color[:3], border_alpha), main_rect, width=5, border_radius=18)
    
    # Viền sáng bên trong
    inner_border = pygame.Rect(box_x + 6, box_y + 6, box_width - 12, box_height - 12)
    lighter_border = tuple(min(255, c + 50) for c in border_color[:3])
    pygame.draw.rect(screen, lighter_border, inner_border, width=2, border_radius=15)
    
    # Hiệu ứng icon xoay và phóng to
    icon_rotation = 5 * math.sin(time * 2)
    icon_scale = 1.0 + 0.1 * math.sin(time * 3)
    icon_alpha = int(220 + 35 * math.sin(time * 4))
    
    # Vẽ glow cho icon
    for glow_r in range(35, 15, -5):
        glow_alpha = int(30 * (glow_r - 15) / 20)
        gfxdraw.filled_circle(screen, box_x + 40, int(box_y + 35), 
                             glow_r, (*icon_color, glow_alpha))
    
    # Vẽ icon với hiệu ứng
    icon_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    icon_text = font_title.render(icon, True, (*icon_color, icon_alpha))
    icon_text = pygame.transform.scale(icon_text, 
                                      (int(icon_text.get_width() * icon_scale),
                                       int(icon_text.get_height() * icon_scale)))
    icon_rect = icon_text.get_rect(center=(40, 40))
    icon_surface.blit(icon_text, icon_rect)
    
    # Bóng cho icon
    shadow_text = font_title.render(icon, True, (0, 0, 0, 100))
    shadow_rect = shadow_text.get_rect(center=(box_x + 42, int(box_y + 37)))
    screen.blit(shadow_text, shadow_rect)
    
    screen.blit(icon_surface, (box_x, int(box_y)))
    
    # Vẽ tiêu đề với hiệu ứng gradient color
    title_alpha = int(255 * (0.95 + 0.05 * math.sin(time * 4)))
    title_surface = font_title.render(title, True, (*text_color, title_alpha))
    title_rect = title_surface.get_rect(midleft=(box_x + 85, int(box_y + 40)))
    
    # Bóng cho text
    title_shadow = font_title.render(title, True, (0, 0, 0, 80))
    shadow_rect = title_shadow.get_rect(midleft=(box_x + 86, int(box_y + 42)))
    screen.blit(title_shadow, shadow_rect)
    screen.blit(title_surface, title_rect)
    
    # Vẽ subtitle với hiệu ứng
    subtitle_alpha = int(200 + 55 * math.sin(time * 3.5))
    subtitle_surface = font.render(subtitle, True, (*text_color, subtitle_alpha))
    subtitle_rect = subtitle_surface.get_rect(midleft=(box_x + 85, int(box_y + 80)))
    screen.blit(subtitle_surface, subtitle_rect)
    
    # Đường kẻ trang trí với hiệu ứng chảy
    line_y = int(box_y + 95)
    line_progress = (time * 0.5) % 1.0
    
    # Vẽ đường kẻ cơ bản
    line_alpha = int(200 + 55 * math.sin(time * 3))
    pygame.draw.line(screen, (*border_color, line_alpha), 
                    (box_x + 20, line_y + 5), 
                    (box_x + box_width - 20, line_y + 5), 3)
    
    # Vẽ điểm sáng chạy trên đường kẻ
    shine_x = box_x + 20 + int((box_width - 40) * line_progress)
    for r in range(8, 0, -2):
        shine_alpha = int(150 * (r / 8))
        gfxdraw.filled_circle(screen, shine_x, line_y+5, r, 
                             (*lighter_border, shine_alpha))
    
    # Vẽ thông tin số lượng gems với hiệu ứng
    info_text = f"Đã sưu tầm: {count} viên ngọc"
    info_alpha = int(255 * (0.9 + 0.1 * math.sin(time * 2.5)))
    info_surface = font.render(info_text, True, (*text_color, info_alpha))
    info_rect = info_surface.get_rect(center=(box_x + box_width // 2, int(box_y + 125)))
    
    # Bóng cho info text
    info_shadow = font.render(info_text, True, (0, 0, 0, 60))
    shadow_rect = info_shadow.get_rect(center=(box_x + box_width // 2 + 1, int(box_y + 127)))
    screen.blit(info_shadow, shadow_rect)
    screen.blit(info_surface, info_rect)
    
    # Vẽ các ngôi sao trang trí với hiệu ứng bay
    star_positions = [
        (box_x + box_width - 30, box_y + 15),
        (box_x + box_width - 20, box_y + 35),
        (box_x + box_width - 35, box_y + 50)
    ]
    for i, base_pos in enumerate(star_positions):
        # Hiệu ứng bay nhẹ
        star_float_x = 2 * math.sin(time * 2 + i * 0.7)
        star_float_y = 2 * math.cos(time * 1.5 + i * 0.5)
        pos_x = base_pos[0] + star_float_x
        pos_y = base_pos[1] + star_float_y
        
        star_alpha = int(200 + 55 * math.sin(time * 6 + i))
        star_size = 6 + 2 * math.sin(time * 4 + i)
        draw_sparkle(screen, int(pos_x), int(pos_y), 
                    (*border_color, star_alpha), int(star_size))


def draw_sparkle(screen, x, y, color, size):
    """Vẽ ngôi sao lấp lánh với hiệu ứng xoay"""
    time = pygame.time.get_ticks() / 1000.0
    rotation = time * 5  # Hiệu ứng xoay mượt hơn
    
    # Vẽ hình sao 4 cánh
    points = []
    inner_points = []
    for i in range(4):
        angle = math.pi / 2 * i + rotation
        # Điểm ngoài
        points.append((x + size * math.cos(angle), y + size * math.sin(angle)))
        # Điểm trong (tạo hình sao thực sự)
        inner_angle = angle + math.pi / 4
        inner_points.append((x + size * 0.4 * math.cos(inner_angle), 
                           y + size * 0.4 * math.sin(inner_angle)))
    
    # Tạo danh sách điểm xen kẽ để vẽ ngôi sao
    star_points = []
    for i in range(4):
        star_points.append(points[i])
        star_points.append(inner_points[i])
    
    # Vẽ ngôi sao
    if len(star_points) >= 3:
        pygame.draw.polygon(screen, color, star_points)
        
        # Vẽ viền sáng
        bright_color = tuple(min(255, c + 50) if isinstance(c, int) else c for c in color[:3])
        if len(bright_color) == 3:
            pygame.draw.polygon(screen, bright_color, star_points, 1)
        
    # Thêm chấm sáng ở giữa với hiệu ứng nhấp nháy
    center_alpha = int(255 * (0.7 + 0.3 * math.sin(time * 10)))
    center_surface = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
    center_radius = max(2, int(size * 0.3))
    
    # Vẽ glow cho tâm
    for r in range(center_radius * 2, center_radius, -1):
        glow_alpha = int(center_alpha * (r - center_radius) / center_radius * 0.5)
        gfxdraw.filled_circle(center_surface, int(size // 2), int(size // 2), 
                             r, (255, 255, 255, glow_alpha))
    
    # Vẽ tâm sáng
    gfxdraw.filled_circle(center_surface, int(size // 2), int(size // 2), 
                         center_radius, (255, 255, 255, center_alpha))
    screen.blit(center_surface, (int(x - size // 2), int(y - size // 2)))