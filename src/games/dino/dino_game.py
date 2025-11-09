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
        # imagens de corrida e pulo
        self.run_images = [
            pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_run1.png")).convert_alpha(),
            pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_run2.png")).convert_alpha()
        ]
        self.jump_image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "dino_jump.png")).convert_alpha()
        self.image = self.run_images[0]

        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.bottom = GROUND_Y

        # ajustes do pulo
        self.vel_y = 0
        self.gravity = 0.6  # gravidade menor para subida mais suave
        self.jump_strength = -21  # força inicial do pulo
        self.is_jumping = False

        # animação
        self.animation_index = 0
        self.animation_speed = 0.15

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_strength
            self.is_jumping = True
            if pygame.mixer.get_init():
                jump_sound.play()

    def update(self):
        # movimento vertical
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
    # Tipos de obstáculos com tamanhos fixos
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
        self.speed = 8  # velocidade inicial

        # Reduzir 10% da hitbox
        shrink_x = int(self.rect.width * 0.3)
        shrink_y = int(self.rect.height * 0.3)
        self.rect = self.rect.inflate(-shrink_x, -shrink_y)  # negativo = menor

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# --- FUNÇÃO PRINCIPAL ---
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

    # --- CARREGAR FUNDO ---
    background = pygame.image.load(os.path.join(ASSETS_DIR, "img", "bg.png")).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # Controle do movimento do fundo
    bg_x = 0
    bg_speed = 1  # quanto maior, mais rápido o fundo se move

    # Sprites
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    player = Dino()
    all_sprites.add(player)

    # Timer de obstáculos
    OBSTACLE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(OBSTACLE_EVENT, 1500)

    font = pygame.font.Font(None, 40)

    while running:
        screen.fill(WHITE)
        now = pygame.time.get_ticks()

        # Aumenta gradualmente a velocidade a cada 5s
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

        # Input
        keys = pygame.key.get_pressed()
        if keys[JUMP_KEY]:
            player.jump()

        # Update
        all_sprites.update()

        # --- RENDERIZAÇÃO COM FUNDO EM MOVIMENTO ---
        bg_x -= bg_speed
        if bg_x <= -SCREEN_WIDTH:
            bg_x = 0
        screen.blit(background, (bg_x, 0))
        screen.blit(background, (bg_x + SCREEN_WIDTH, 0))

        # Colisões
        if pygame.sprite.spritecollide(player, obstacles, False):
            if pygame.mixer.get_init():
                die_sound.play()
            time.sleep(0.5)
            running = False

        # Desenho
        all_sprites.draw(screen)

        # Score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (SCREEN_WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(60)
        score += 1

    # Limpar
    all_sprites.empty()
    obstacles.empty()
    return


if __name__ == "__main__":
    game_loop()
