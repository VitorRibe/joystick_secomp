import pygame
import sys
import os
import random
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- CONFIGURAÇÃO DE TELA ---
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND_Y = SCREEN_HEIGHT - 80

# --- CONTROLES ---
JUMP_KEY = pygame.K_SPACE

# Variáveis globais
player_speed = 6  # velocidade base dos obstáculos
speed_increment_timer = 0
SPEED_INCREASE_INTERVAL = 5000  # a cada 5 segundos
SPEED_INCREMENT = 0.5


# --- CLASSES ---
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # corrida
        self.run_images = [
            pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_run1.png")).convert_alpha(),
            pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_run2.png")).convert_alpha()
        ]
        # pulo
        self.jump_image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "jump.png")).convert_alpha()
        self.image = self.run_images[0]

        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.bottom = GROUND_Y
        self.vel_y = 0
        self.gravity = 0.8
        self.is_jumping = False
        self.animation_index = 0
        self.animation_speed = 0.15

    def jump(self):
        if not self.is_jumping:
            self.vel_y = -15
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

        # animação
        if self.is_jumping:
            self.image = self.jump_image
        else:
            self.animation_index += self.animation_speed
            if self.animation_index >= len(self.run_images):
                self.animation_index = 0
            self.image = self.run_images[int(self.animation_index)]

        # mantém o rect no meio inferior
        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom))

class Obstacle(pygame.sprite.Sprite):
    # Dicionário com os obstáculos e seus tamanhos
    OBSTACLE_TYPES = {
        "caramelo": (60, 60),
        "placa": (80, 80)
    }

    def __init__(self):
        super().__init__()
        # Escolhe um tipo aleatório
        self.type = random.choice(list(self.OBSTACLE_TYPES.keys()))
        width, height = self.OBSTACLE_TYPES[self.type]

        path = os.path.join(ASSETS_DIR, "img", f"{self.type}.png")
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(0, 300)
        self.rect.bottom = GROUND_Y
        self.speed = 6  # valor inicial, será incrementado globalmente

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# --- FUNÇÃO PRINCIPAL ---
def game_loop(arduino_reader=None):
    global player_speed, speed_increment_timer
    pygame.init()
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()

    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Dino Arcade")
    clock = pygame.time.Clock()
    running = True
    score = 0

    # --- SONS ---
    global jump_sound, die_sound
    jump_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "jump.wav"))
    die_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "die.wav"))

    # --- SPRITES ---
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player = Dino()
    all_sprites.add(player)

    # temporizador de obstáculos
    obstacle_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacle_timer, 1500)

    # Atualizar velocidade gradativamente
    now = pygame.time.get_ticks()
    if now - speed_increment_timer > SPEED_INCREASE_INTERVAL:
        speed_increment_timer = now
        player_speed += SPEED_INCREMENT

    # Atualizar velocidade dos obstáculos
    for obs in obstacles:
        obs.speed = player_speed

    serial_active = arduino_reader and arduino_reader.ser and arduino_reader.ser.is_open

    font = pygame.font.Font(None, 40)

    while running:
        screen.fill(WHITE)

        # --- EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == obstacle_timer:
                obs = Obstacle()
                all_sprites.add(obs)
                obstacles.add(obs)

        # --- INPUT ---
        keys = pygame.key.get_pressed()
        if keys[JUMP_KEY]:
            player.jump()

        if serial_active:
            state = arduino_reader.control_state
            if state['BTN_A']:
                player.jump()

        # --- UPDATE ---
        all_sprites.update()

        # --- COLISÕES ---
        if pygame.sprite.spritecollide(player, obstacles, False):
            if pygame.mixer.get_init():
                die_sound.play()
            time.sleep(0.5)
            break  # sai do jogo e volta para o menu

        # --- DESENHO ---
        all_sprites.draw(screen)

        # pontuação
        score_text = font.render(f"SCORE: {score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(60)
        score += 1

    # --- LIMPAR ---
    all_sprites.empty()
    obstacles.empty()
    return
