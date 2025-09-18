import pygame
import math
import time
import config
import ui_elements
import datetime

font_icon = pygame.font.Font(config.ICON_DIR, 64)

def draw_collection(screen, font_title, font, font_small, colors, gem_types, game_state, handle_button_click_callback, draw_multiline_text_func):
    # Nếu đang xem chi tiết 1 viên đá
    if game_state.viewing_gem is not None:
        draw_gem_detail(screen, font_title, font, font_small, colors, game_state, draw_multiline_text_func)
        return

    # Vẽ header với hiệu ứng đẹp ở bên phải
    draw_collection_header(screen, font_title, colors)
    
    # Vẽ thống kê collection ở bên phải
    draw_collection_stats(screen, font, font_small, colors, gem_types, game_state)

    gem_size = 140
    margin_x = 220  # Dời sang phải để tránh thanh menu
    margin_y = 140
    spacing = 35

    # Tính toán animation timing
    current_time = time.time()

    for i, gem in enumerate(gem_types):
        row = i // 4
        col = i % 4
        x = margin_x + col * (gem_size + spacing)
        y = margin_y + row * (gem_size + spacing)

        owned = any(g["id"] == gem["id"] for g in game_state.collected_gems)

        # Vẽ gem card với hiệu ứng đẹp
        draw_gem_card(screen, gem, x, y, gem_size, owned, current_time, i, font_small, colors)

        # Store rect directly in the gem dictionary for click detection in main.py
        gem["rect"] = pygame.Rect(x, y, gem_size, gem_size)

def draw_collection_header(screen, font_title, colors):
    """Vẽ header với hiệu ứng đẹp ở bên phải"""
    # Vẽ panel header với bo góc, dành chỗ cho thanh menu
    header_rect = pygame.Rect(210, 20, config.WIDTH - 230, 80)
    
    # Vẽ shadow cho header
    shadow_rect = pygame.Rect(212, 22, config.WIDTH - 230, 80)
    pygame.draw.rect(screen, (0, 0, 0, 30), shadow_rect, border_radius=25)
    
    # Vẽ header chính
    pygame.draw.rect(screen, colors["white"], header_rect, border_radius=25)
    pygame.draw.rect(screen, colors["accent"], header_rect, 3, border_radius=25)
    
    # Vẽ title với hiệu ứng gradient text
    title_text = "BỘ SƯU TẬP ĐÁ QUÝ "
    title_surface = font_title.render(title_text, True, colors["accent"])
    title_rect = title_surface.get_rect(center=header_rect.center)
    screen.blit(title_surface, title_rect)

def draw_collection_stats(screen, font, font_small, colors, gem_types, game_state):
    """Vẽ thống kê collection"""
    # Chỉ đếm các gem có ID duy nhất
    unique_collected_ids = {g["id"] for g in game_state.collected_gems}
    collected_count = len(unique_collected_ids)
    total_count = len(gem_types)
    completion_percentage = (collected_count / total_count) * 100 if total_count > 0 else 0
    
    # Vẽ panel stats - dời sang phải để tránh menu
    stats_rect = pygame.Rect(220, 110, config.WIDTH - 270, 25)
    
    # Progress bar background - thu nhỏ lại để không đè lên menu
    progress_bg_rect = pygame.Rect(230, 113, config.WIDTH - 470, 19)
    pygame.draw.rect(screen, colors["progress_bg"], progress_bg_rect, border_radius=10)
    
    # Progress bar fill
    if completion_percentage > 0:
        fill_width = int((config.WIDTH - 470) * (completion_percentage / 100))
        progress_fill_rect = pygame.Rect(230, 113, fill_width, 19)
        pygame.draw.rect(screen, colors["accent"], progress_fill_rect, border_radius=10)
    
    # Stats text - chỉnh lại vị trí cho cân đối
    stats_text = f"Thu thập: {collected_count}/{total_count} ({completion_percentage:.1f}%)"
    stats_surface = font_small.render(stats_text, True, colors["text"])
    stats_rect = stats_surface.get_rect(midleft=(progress_bg_rect.right + 15, progress_bg_rect.centery))
    screen.blit(stats_surface, stats_rect)

def draw_gem_card(screen, gem, x, y, gem_size, owned, current_time, index, font_small, colors):
    """Vẽ gem card với hiệu ứng đẹp"""
    # Tạo hiệu ứng hover/animation
    hover_offset = math.sin(current_time * 2 + index * 0.3) * 2 if owned else 0
    card_y = y + hover_offset
    
    # Vẽ shadow cho card
    shadow_rect = pygame.Rect(x + 3, card_y + 3, gem_size, gem_size)
    draw_rounded_rect_with_shadow(screen, shadow_rect, (0, 0, 0, 40), 20)
    
    # Tính toán màu cho card
    if owned:
        # Tạo gradient cho gem được sở hữu
        primary_color = gem["color"]
        secondary_color = (
            min(255, primary_color[0] + 30),
            min(255, primary_color[1] + 30),
            min(255, primary_color[2] + 30)
        )
    else:
        # Màu xám cho gem chưa sở hữu
        primary_color = (80, 80, 80)
        secondary_color = (60, 60, 60)
    
    # Vẽ card chính với gradient
    card_rect = pygame.Rect(x, card_y, gem_size, gem_size)
    draw_gradient_rect(screen, card_rect, primary_color, secondary_color, 20)
    
    # Vẽ border với hiệu ứng glow nếu owned
    if owned:
        # Outer glow
        glow_rect = pygame.Rect(x - 2, card_y - 2, gem_size + 4, gem_size + 4)
        pygame.draw.rect(screen, (*primary_color, 100), glow_rect, 3, border_radius=22)
        
        # Inner border
        pygame.draw.rect(screen, colors["white"], card_rect, 2, border_radius=20)
    else:
        pygame.draw.rect(screen, colors["card_border"], card_rect, 2, border_radius=20)
    
    # Vẽ nội dung card
    if owned:
        # Vẽ gem icon/pattern
        draw_gem_pattern(screen, card_rect, primary_color)
        
        # Vẽ tên gem với background
        name_bg_rect = pygame.Rect(x + 5, card_y + gem_size - 35, gem_size - 10, 30)
        pygame.draw.rect(screen, (0, 0, 0, 120), name_bg_rect, border_radius=8)
        
        name_text = font_small.render(gem["name"], True, colors["white"])
        name_rect = name_text.get_rect(center=name_bg_rect.center)
        screen.blit(name_text, name_rect)
        
        # Vẽ sparkle effects
        draw_sparkles(screen, card_rect, current_time, index)
    else:
        # Vẽ question mark với hiệu ứng
        question_size = 60
        question_font = pygame.font.Font(config.FONT_PATH, question_size)
        question_text = question_font.render("?", True, colors["white"])
        question_rect = question_text.get_rect(center=card_rect.center)
        screen.blit(question_text, question_rect)
        
        # Vẽ lock icon nhỏ
        lock_icon = pygame.font.SysFont("segoe ui emoji", 30).render("\U0001F512", True, colors["white"])
        screen.blit(lock_icon, (x + gem_size - 30, card_y + gem_size - 30))

def draw_gradient_rect(screen, rect, color1, color2, border_radius=0):
    """Vẽ hình chữ nhật với gradient"""
    # Tạo surface tạm thời cho gradient
    temp_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(temp_surface, (r, g, b), (0, y), (rect.width, y))
    
    # Tạo mask cho border radius nếu cần
    if border_radius > 0:
        mask_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
        temp_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    screen.blit(temp_surface, rect.topleft)

def draw_rounded_rect_with_shadow(screen, rect, color, border_radius):
    """Vẽ hình chữ nhật bo góc với shadow"""
    # Tạo surface với alpha cho shadow
    shadow_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, color, (0, 0, rect.width, rect.height), border_radius=border_radius)
    screen.blit(shadow_surface, rect.topleft)

def draw_gem_pattern(screen, rect, color):
    """Vẽ pattern cho gem"""
    center_x, center_y = rect.center
    
    # Vẽ các đường kim cương
    points = []
    for i in range(6):
        angle = i * math.pi / 3
        x = center_x + math.cos(angle) * 30
        y = center_y + math.sin(angle) * 30
        points.append((x, y))
    
    # Vẽ hình kim cương
    if len(points) >= 3:
        lighter_color = (
            min(255, color[0] + 50),
            min(255, color[1] + 50),
            min(255, color[2] + 50)
        )
        pygame.draw.polygon(screen, lighter_color, points)
        pygame.draw.polygon(screen, (255, 255, 255, 100), points, 2)

def draw_sparkles(screen, rect, current_time, index):
    """Vẽ hiệu ứng sparkles cho gem được sở hữu"""
    for i in range(3):
        angle = current_time * 3 + index * 0.5 + i * 2.1
        radius = 40 + math.sin(current_time * 2 + i) * 10
        x = rect.centerx + math.cos(angle) * radius
        y = rect.centery + math.sin(angle) * radius
        
        # Kiểm tra xem sparkle có nằm trong rect không
        if rect.collidepoint(x, y):
            sparkle_size = 3 + math.sin(current_time * 4 + i) * 2
            pygame.draw.circle(screen, (255, 255, 255, 150), (int(x), int(y)), max(1, int(sparkle_size)))

def draw_gem_detail(screen, font_title, font, font_small, colors, game_state, draw_multiline_text_func):
    gem = game_state.viewing_gem
    current_time = time.time()

    # Vẽ panel chi tiết chính (dời sang phải để tránh menu và đưa lên gần mép trên hơn)
    panel_rect = pygame.Rect(210, 20, config.WIDTH - 230, config.HEIGHT - 110)  # Đã điều chỉnh y từ 50 xuống 20
    
    # Shadow cho panel
    shadow_rect = pygame.Rect(213, 23, config.WIDTH - 230, config.HEIGHT - 100)  # Điều chỉnh tương ứng
    draw_rounded_rect_with_shadow(screen, shadow_rect, (0, 0, 0, 80), 25)
    
    # Panel chính
    pygame.draw.rect(screen, colors["white"], panel_rect, border_radius=25)
    pygame.draw.rect(screen, gem["color"], panel_rect, 4, border_radius=25)

    # Vẽ viên đá lớn ở giữa với hiệu ứng
    gem_size = 180
    gem_x = panel_rect.centerx - gem_size // 2
    gem_y = panel_rect.y + 50  # Điều chỉnh vị trí y cho phù hợp với panel mới
    gem_rect = pygame.Rect(gem_x, gem_y, gem_size, gem_size)
    
    # Vẽ glow effect
    glow_intensity = (math.sin(current_time * 2) + 1) / 2
    glow_size = gem_size + int(20 * glow_intensity)
    glow_rect = pygame.Rect(gem_x - 10, gem_y - 10, glow_size, gem_size)
    
    # Multiple glow layers
    for i in range(3):
        alpha = int(50 * glow_intensity * (1 - i * 0.3))
        glow_surface = pygame.Surface((glow_size + i * 4, glow_size + i * 4), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*gem["color"], alpha), (0, 0, glow_size + i * 4, glow_size + i * 4), border_radius=25 + i * 2)
        screen.blit(glow_surface, (glow_rect.x - i * 2, glow_rect.y - i * 2))
    
    # Gem chính với gradient
    secondary_color = (
        min(255, gem["color"][0] + 40),
        min(255, gem["color"][1] + 40),
        min(255, gem["color"][2] + 40)
    )
    draw_gradient_rect(screen, gem_rect, gem["color"], secondary_color, 25)
    
    # Gem pattern
    draw_gem_pattern(screen, gem_rect, gem["color"])
    
    # Border cho gem
    pygame.draw.rect(screen, colors["white"], gem_rect, 3, border_radius=25)

    # Vẽ tên đá với background đẹp
    name_y = gem_rect.bottom + 15  # Điều chỉnh khoảng cách
    name_text = font_title.render(gem["name"], True, gem["color"])
    name_rect = name_text.get_rect(centerx=panel_rect.centerx, y=name_y)
    
    # Background cho tên
    name_bg_rect = pygame.Rect(name_rect.x - 20, name_rect.y - 5, name_rect.width + 40, name_rect.height + 10)
    pygame.draw.rect(screen, colors["bg"], name_bg_rect, border_radius=15)
    pygame.draw.rect(screen, gem["color"], name_bg_rect, 2, border_radius=15)
    
    screen.blit(name_text, name_rect)

    # Vẽ mô tả với background panel
    desc_y = name_rect.bottom + 20  # Điều chỉnh khoảng cách
    desc_rect = pygame.Rect(panel_rect.x + 30, desc_y, panel_rect.width - 60, 120)
    pygame.draw.rect(screen, colors["panel"], desc_rect, border_radius=15)
    pygame.draw.rect(screen, colors["card_border"], desc_rect, 1, border_radius=15)
    
    draw_multiline_text_func(screen, gem["description"], desc_rect.x + 15, desc_rect.y + 15, font, colors["text"], desc_rect.width - 30)

    # Vẽ ngày thu thập nếu có
    collected_gem_data = next((g for g in game_state.collected_gems if g["id"] == gem["id"]), None)
    if collected_gem_data and "collected_date" in collected_gem_data:
        date_y = desc_rect.bottom + 15  # Điều chỉnh khoảng cách
        date_bg_rect = pygame.Rect(panel_rect.x + 30, date_y, panel_rect.width - 60, 35)
        pygame.draw.rect(screen, colors["accent"], date_bg_rect, border_radius=10)

        raw_date = collected_gem_data['collected_date']
        try:
            # Giả sử ngày lưu theo định dạng YYYY-MM-DD
            dt = datetime.datetime.strptime(raw_date, "%Y-%m-%d")
            formatted_date = dt.strftime("%d/%m/%Y")  # Chuyển sang DD/MM/YYYY
        except ValueError:
            # Nếu không đúng định dạng thì giữ nguyên
            formatted_date = raw_date

        date_text = font_small.render(f"Thu thập ngày: {formatted_date}", True, colors["white"])
        date_rect = date_text.get_rect(center=date_bg_rect.center)
        screen.blit(date_text, date_rect)


    # Vẽ sparkles cho toàn bộ panel
    for i in range(8):
        angle = current_time * 1.5 + i * 0.8
        radius_x = (panel_rect.width // 2 - 50) * (0.7 + 0.3 * math.sin(current_time + i))
        radius_y = (panel_rect.height // 2 - 50) * (0.7 + 0.3 * math.cos(current_time + i))
        x = panel_rect.centerx + math.cos(angle) * radius_x
        y = panel_rect.centery + math.sin(angle) * radius_y
        
        sparkle_size = 2 + math.sin(current_time * 3 + i) * 2
        pygame.draw.circle(screen, (255, 255, 255, 200), (int(x), int(y)), max(1, int(sparkle_size)))

def set_viewing_gem_to_none(game_state):
    game_state.viewing_gem = None
    game_state.just_closed_detail = True