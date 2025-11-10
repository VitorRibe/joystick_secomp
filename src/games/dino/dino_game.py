import pygame
import os
import random
import time

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
GROUND_Y = SCREEN_HEIGHT - 80
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
WHITE = (255, 255, 255)

# --- CONTROLES ---
JUMP_KEY = pygame.K_SPACE


# --- CLASSES ---
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_images = [
            pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_run1.png")).convert_alpha(),
            pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_run2.png")).convert_alpha()
        ]
        self.jump_image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_jump.png")).convert_alpha()
        self.image = self.run_images[0]

        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.bottom = GROUND_Y

        self.vel_y = 0
        self.gravity = 0.6
        self.jump_strength = -21
        self.is_jumping = False

        self.animation_index = 0
        self.animation_speed = 0.15

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_strength
            self.is_jumping = True
            if pygame.mixer.get_init():
                jump_sound.play()

    def update(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.is_jumping = False

        if self.is_jumping:
            self.image = self.jump_image
        else:
            self.animation_index += self.animation_speed
            if self.animation_index >= len(self.run_images):
                self.animation_index = 0
            self.image = self.run_images[int(self.animation_index)]

        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom))


class Obstacle(pygame.sprite.Sprite):
    OBSTACLES = {
        "caramelo": (100, 100),
        "placa": (200, 170)
    }

    def __init__(self):
        super().__init__()
        self.type = random.choice(list(self.OBSTACLES.keys()))
        width, height = self.OBSTACLES[self.type]
        path = os.path.join(ASSETS_DIR, "img", f"{self.type}.png")
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(0, 300)
        self.rect.bottom = GROUND_Y
        self.speed = 8

        # Reduz 10% da hitbox
        shrink_x = int(self.rect.width * 0.3)
        shrink_y = int(self.rect.height * 0.3)
        self.rect = self.rect.inflate(-shrink_x, -shrink_y)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# --- FUNÇÕES AUXILIARES ---
def draw_text(screen, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)


def show_game_over_screen(screen, clock, score, arduino_reader=None, serial_active=False):
    waiting_for_input = True
    while waiting_for_input:
        screen.fill(WHITE)
        draw_text(screen, "G A M E   O V E R", 80, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        draw_text(screen, f"Pontuação: {score}", 50, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(screen, "Pressione [AÇÃO] ou [ESPAÇO] para Reiniciar", 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.7)
        draw_text(screen, "Pressione [START] ou [ENTER] para Voltar ao Menu", 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.8)
        pygame.display.flip()
        clock.tick(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            return "restart"
        elif keys[pygame.K_RETURN]:
            return "menu"

        if serial_active and arduino_reader:
            state = arduino_reader.control_state
            if state["BTN_A"]:
                return "restart"
            if state["BTN_SW"]:
                return "menu"

        if serial_active:
            time.sleep(0.1)


# --- LOOP PRINCIPAL DO JOGO ---
def game_loop(arduino_reader=None):
    pygame.init()
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()

    screen = SCREEN
    clock = pygame.time.Clock()
    running = True
    score = 0
    player_speed = 8
    speed_timer = pygame.time.get_ticks()

    # Sons
    global jump_sound, die_sound
    jump_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "jump.wav"))
    die_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "die.wav"))

    # Fundo
    background = pygame.image.load(os.path.join(ASSETS_DIR, "img", "bg.png")).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_x = 0
    bg_speed = 1

    # Sprites
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player = Dino()
    all_sprites.add(player)

    OBSTACLE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(OBSTACLE_EVENT, 1500)

    font = pygame.font.Font(None, 40)

    serial_active = arduino_reader and arduino_reader.ser and arduino_reader.ser.is_open

    while running:
        screen.fill(WHITE)
        now = pygame.time.get_ticks()

        if now - speed_timer > 5000:
            speed_timer = now
            player_speed += 1
            for obs in obstacles:
                obs.speed = player_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == OBSTACLE_EVENT:
                obs = Obstacle()
                obs.speed = player_speed
                all_sprites.add(obs)
                obstacles.add(obs)

        # --- ENTRADAS ---
        keys = pygame.key.get_pressed()
        if keys[JUMP_KEY]:
            player.jump()

        if serial_active:
            state = arduino_reader.control_state
            if state["BTN_A"]:
                player.jump()

        # --- ATUALIZAÇÃO ---
        all_sprites.update()

        # --- FUNDO ANIMADO ---
        bg_x -= bg_speed
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0
        screen.blit(background, (bg_x, 0))
        screen.blit(background, (bg_x + SCREEN_WIDTH, 0))

        # --- COLISÕES ---
        if pygame.sprite.spritecollide(player, obstacles, False):
            if pygame.mixer.get_init():
                die_sound.play()
            time.sleep(0.5)
            result = show_game_over_screen(screen, clock, score, arduino_reader, serial_active)
            if result == "restart":
                return game_loop(arduino_reader)
            elif result == "menu":
                return
            elif result == "exit":
                pygame.quit()
                return

        # --- DESENHO ---
        all_sprites.draw(screen)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (SCREEN_WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(60)
        score += 1

    # Limpeza final
    all_sprites.empty()
    obstacles.empty()
    return


if __name__ == "__main__":
    game_loop()
