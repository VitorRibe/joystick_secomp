import pygame
import sys, os
import time
import importlib
from src.serial_reader import ArduinoSerialReader

# --- CONFIGURAÇÕES DE TELA E CORES ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /home/vitor/PycharmProjects/joystick_secomp/src
thumb_path = os.path.join(BASE_DIR, "games")


# --- JOGOS DISPONÍVEIS ---
games = [
    {"name": "Space Shooter", "module": "games.space.nave_game",
     "thumb": os.path.join(thumb_path, "space", "assets", "img", "game_cover.png")},
    {"name": "Protodino Entrega", "module": "games.dino.dino_game",
     "thumb": os.path.join(thumb_path, "dino", "assets", "img", "game_cover.png")},
    {"name": "Futuro Game 3", "module": None,
     "thumb": os.path.join(thumb_path, "assets", "img", "thumb_futuro.png")},
    {"name": "Futuro Game 4", "module": None,
     "thumb": os.path.join(thumb_path, "assets", "img", "thumb_futuro.png")},
]


# --- DESENHA MENU ---
def draw_menu(screen, font, selected_index, bg_image, logo):
    screen.blit(bg_image, (0, 0))
    title_font = pygame.font.Font(None, 80)
    title = title_font.render("ARCADE SECOMP", True, BLUE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    # Grade 2x2
    cols = 2
    spacing_x = 300
    spacing_y = 220
    start_x = (SCREEN_WIDTH - (cols - 1) * spacing_x) // 3
    start_y = 180

    for i, game in enumerate(games):
        col = i % cols
        row = i // cols
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y

        # Carregar thumbnail
        try:
            thumb = pygame.image.load(game["thumb"]).convert_alpha()
        except:
            thumb = pygame.Surface((200, 120))
            thumb.fill(GRAY)
        thumb = pygame.transform.scale(thumb, (200, 120))
        rect = thumb.get_rect(topleft=(x, y))

        # Destacar o selecionado
        if i == selected_index:
            pygame.draw.rect(screen, BLUE, rect.inflate(12, 12), border_radius=10, width=4)

        screen.blit(thumb, rect.topleft)

        # Nome do jogo
        name_text = font.render(game["name"], True, WHITE)
        screen.blit(name_text, (x + 100 - name_text.get_width() // 2, y + 130))

        # --- desenha o logo da empresa no rodapé ---
        logo_rect = logo.get_rect()
        logo_rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)  # centralizado com margem
        screen.blit(logo, logo_rect)

    pygame.display.flip()

# --- LOOP PRINCIPAL DO MENU ---
def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Menu Arcade SECOMP")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # --- FUNDO ---
    try:
        bg_image = pygame.image.load("assets/img/menu_bg.png").convert()
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_image.fill(BLACK)

    # --- Carregar logo da empresa ---
    logo = pygame.image.load("../imgs/logo.png").convert_alpha()
    logo = pygame.transform.scale(logo, (80, 40))  # ajuste o tamanho como quiser

    '''# --- SOM DO MENU ---
    try:
        pygame.mixer.music.load("assets/sounds/menu_music.mp3")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("⚠️ Falha ao carregar musica de menu:", e)
    '''

    # --- INICIALIZA SERIAL UMA ÚNICA VEZ ---
    SERIAL_PORT = '/dev/ttyUSB0'
    BAUD_RATE = 115200
    arduino_reader = ArduinoSerialReader(SERIAL_PORT, BAUD_RATE)
    try:
        arduino_reader.start()
        time.sleep(2)
        serial_active = arduino_reader.ser and arduino_reader.ser.is_open
        print(f"Serial ativo? {serial_active}")
    except Exception as e:
        print(f"⚠️ Falha ao iniciar o Arduino: {e}")
        serial_active = False

    selected_index = 0
    running = True

    while running:
        draw_menu(screen, font, selected_index, bg_image, logo)
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # --- TECLADO ---
        if keys[pygame.K_LEFT]:
            selected_index = (selected_index - 1) % len(games)
            time.sleep(0.15)
        elif keys[pygame.K_RIGHT]:
            selected_index = (selected_index + 1) % len(games)
            time.sleep(0.15)
        elif keys[pygame.K_SPACE]:
            chosen = games[selected_index]
            if chosen["module"]:
                if pygame.mixer.get_init():  # checa se o mixer está ativo
                    pygame.mixer.music.stop()
                module = importlib.import_module(chosen["module"])
                module.game_loop(arduino_reader)
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                #pygame.mixer.music.play(-1)
            time.sleep(0.3)

        # --- ARDUINO ---
        if serial_active:
            state = arduino_reader.control_state
            if state["LEFT"]:
                selected_index = (selected_index - 1) % len(games)
                time.sleep(0.2)
            elif state["RIGHT"]:
                selected_index = (selected_index + 1) % len(games)
                time.sleep(0.2)
            elif state["BTN_A"]:
                chosen = games[selected_index]
                if chosen["module"]:
                    if pygame.mixer.get_init():  # checa se o mixer está ativo
                        pygame.mixer.music.stop()
                    module = importlib.import_module(chosen["module"])
                    module.game_loop(arduino_reader)
                    #pygame.mixer.music.play(-1)
                time.sleep(0.3)

    # --- ENCERRA ---
    arduino_reader.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
