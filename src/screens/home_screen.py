import pygame
import ui_elements
import config
import os

def draw_home(screen, game_state, switch_screen_callback):
    screen.fill(config.COLORS["bg"])
    #vẽ nền
    image_path_bg = os.path.join(config.ASSETS_DIR, "setting", "home_bg.jpg")
    image_bg = pygame.image.load(image_path_bg)
    image_bg = pygame.transform.scale(image_bg, (960, 640))  
    screen.blit(image_bg, (0, 0))

    # Vẽ tiêu đề
    image_path = os.path.join(config.ASSETS_DIR, "setting", "home_logo.png")
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (850,370))  
    screen.blit(image, (70, 50))

    start_button = ui_elements.Button(
        x=config.WIDTH // 2 - 110,
        y=420,
        w=220,  
        h=70,   
        text="BẮT ĐẦU",
        callback=lambda: switch_screen_callback(config.SCREEN_LESSON),
        color=(134, 83, 51),
        border_radius=10
    )

    start_button.draw(screen)


    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    if mouse_click[0] and start_button.rect.collidepoint(mouse_pos):
        start_button.callback()
