# shop_screen.py
import pygame
import config
import ui_elements
from pygame import gfxdraw

font_icon = pygame.font.Font(config.ICON_DIR, 64)

shop_items = [
    {"name": "Thẻ bảo vệ streak", "price": 150, "icon": "\U0001F6E1", "color": (70, 130, 180)},
    {"name": "Tinh thể kỳ ảo(V.I.P)", "price": 550, "icon": "\U0001F48E", "color": (220, 20, 60)},
    {"name": "Tinh thể kỳ ảo", "price": 470, "icon": "\U0001F52E", "color": (138, 43, 226)},
    {"name": "Gói điểm", "price": 50, "icon": "\U0001F4B0", "color": (210, 105, 30)},
    {"name": "Hồi năng lượng", "price": 120, "icon": "\u26A1", "color": (50, 205, 50)},
    {"name": "Bùa tăng tốc điểm", "price": 80, "icon": "\u2728", "color": (255, 140, 0)},
]

def draw_shop(screen, font_title, font, colors, game_state, handle_button_click_callback, items):
    menu_width = 190  # Độ rộng menu bên trái
    shop_x = menu_width  # Bắt đầu từ sau menu
    
    # Background cho phần cửa hàng
    shop_bg = pygame.Rect(shop_x, 0, config.WIDTH - menu_width, config.HEIGHT)
    pygame.draw.rect(screen, (240, 248, 255), shop_bg)
    
    # Title (căn trái so với phần shop)
    title = font_title.render("CỬA HÀNG", True, (30, 30, 30))
    title_main = font_title.render("CỬA HÀNG", True, (255, 215, 0))
    screen.blit(title, (shop_x + 210, 32))
    screen.blit(title_main, (shop_x + 208, 30))
    
    # Đường kẻ trang trí (căn trái)
    pygame.draw.line(screen, (255, 215, 0), (shop_x + 180, 80), (shop_x + 480, 80), 3)
    
    # Vẽ các mặt hàng (2 cột)
    item_width = 300
    item_height = 150
    item_margin = 20
    items_per_row = 2
    total_row_width = items_per_row * item_width + (items_per_row - 1) * item_margin
    start_x = (config.WIDTH + menu_width - total_row_width) // 2

    for i, item in enumerate(items):
        col = i % items_per_row
        row = i // items_per_row
        x = start_x + col * (item_width + item_margin)
        y = 100 + row * (item_height + 20)

        
        # Thẻ sản phẩm
        rect = pygame.Rect(x, y, 280, 160)
        
        # Hiệu ứng bóng
        shadow_rect = pygame.Rect(x + 3, y + 3, 280, 160)
        pygame.draw.rect(screen, (100, 100, 100, 100), shadow_rect, border_radius=12)
        
        # Hiệu ứng hover
        hover = rect.collidepoint(pygame.mouse.get_pos())
        card_color = (
            min(item["color"][0] + 40, 255),
            min(item["color"][1] + 40, 255),
            min(item["color"][2] + 40, 255)
        ) if hover else item["color"]
        
        # Vẽ thẻ với gradient
        pygame.draw.rect(screen, card_color, rect, border_radius=12)

        # Viền
        border_color = (255, 255, 255) if hover else (200, 200, 200)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=12)
        
        # Icon sản phẩm (căn giữa thẻ)
        icon = pygame.font.SysFont("segoe ui emoji", 48).render(item["icon"], True, (255, 255, 255))
        screen.blit(icon, (x + 140 - icon.get_width()//2, y + 20))
        
        # Tên sản phẩm (căn giữa)
        name_text = font.render(item["name"], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + 140, y + 90))
        screen.blit(name_text, name_rect)
        
        # Giá với icon đồng xu
        price_text = font.render(f"{item['price']}", True, (255, 255, 0))
        price_rect = price_text.get_rect(center=(x + 120, y + 130))
        screen.blit(price_text, price_rect)
        
        coin_icon = pygame.font.SysFont("segoe ui emoji", 20).render("$", True, (255, 255, 0))
        screen.blit(coin_icon, (price_rect.right + 5, y + 120))
        
        # Hiệu ứng khi hover
        if hover:
            glow_surface = pygame.Surface((300, 180), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 255, 30), (0, 0, 300, 180), border_radius=12)
            screen.blit(glow_surface, (x - 10, y - 10))
            
            pulse_size = int(abs(pygame.time.get_ticks() % 1000 - 500) / 50)
            pulse_rect = pygame.Rect(x - pulse_size, y - pulse_size, 
                                   280 + pulse_size*2, 160 + pulse_size*2)
            pygame.draw.rect(screen, (255, 255, 255, 50), pulse_rect, 2, border_radius=12+pulse_size)

    # Footer trang trí (căn trái)
    pygame.draw.line(screen, (255, 215, 0), (shop_x + 200, config.HEIGHT - 30), 
                    (shop_x + 600, config.HEIGHT - 30), 2)