import pygame
import sys, os
import random
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# Assumimos que o módulo serial_reader.py está na pasta src/ e está importável
from src.serial_reader import ArduinoSerialReader

# --- CONFIGURAÇÕES DA APLICAÇÃO ---
# Use um nome fictício que não cause erro de permissão no Linux (ex: 'COM_FICTICIA')
# Ou use a porta COM correta se o Arduino estiver conectado e o SO for Windows.
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 2
SCORE = 0
LAST_ENEMY_SPAWN_TIME = 0
ENEMY_SPAWN_RATE = 1500

# --- CONFIGURAÇÕES DE TELA ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# --- Grupos de Sprites Globais e Variáveis de Estado (Para o escopo do jogo) ---
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
player = None
game_over = False
waiting_for_input = False

# --- Sons globais ---
laser_sound = None
explosion_sound = None



# --- Classes de Sprites (Omitidas para brevidade, mas devem estar aqui: Nave, Projetil, Inimigo, ProjetilInimigo) ---

class Nave(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "nave.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)

        self.health = 3
        self.last_shot = 0
        self.shoot_delay = 100

    def update_position(self, dx, dy):
        self.rect.x += dx * SPEED;
        self.rect.y += dy * SPEED
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40))

class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "laser_nave.png")).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (20, 40))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        # movimento da bala
        self.rect.y -= BULLET_SPEED * 1.5
        if self.rect.bottom < 0:
            self.kill()


class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__();
        self.image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "enemy.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect();
        self.rect.x = random.randrange(0, SCREEN_WIDTH - 40)
        self.rect.y = random.randrange(-100, -40);
        self.speedy = ENEMY_SPEED
        self.last_shot = pygame.time.get_ticks();
        self.shoot_delay = random.randrange(1000, 3000)

    def update(self):
        self.rect.y += self.speedy
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.rect.y < SCREEN_HEIGHT / 2:
            self.last_shot = now;
            self.shoot()
        if self.rect.top > SCREEN_HEIGHT: self.kill()

    def shoot(self):
        bullet = ProjetilInimigo(self.rect.centerx, self.rect.bottom);
        all_sprites.add(bullet);
        enemy_bullets.add(bullet)


class ProjetilInimigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__();
        self.original_image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "laser_enemy.png")).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (20, 40))
        self.rect = self.image.get_rect();
        self.rect.centerx = x;
        self.rect.top = y

    def update(self):
        self.rect.y += BULLET_SPEED / 2
        if self.rect.bottom > SCREEN_HEIGHT: self.kill()


class Explosao(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join(ASSETS_DIR, "img", "explosion.png")).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (60, 60))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.max_frames = 15  # quanto maior, mais longa a animacao

    def update(self):
        self.frame += 1
        scale = 1 + self.frame * 0.2  # vai crescendo
        size = int(self.original_image.get_width() * scale)
        self.image = pygame.transform.scale(self.original_image, (size, size))
        self.rect = self.image.get_rect(center=self.rect.center)

        # fade out
        alpha = max(255 - self.frame * 20, 0)
        self.image.set_alpha(alpha)

        # apaga depois do fim
        if self.frame > self.max_frames:
            self.kill()



# --- FUNÇÕES DE LÓGICA GERAL (Omitidas para brevidade, mas essenciais) ---
def initialize_game():
    global player, all_sprites, bullets, enemies, enemy_bullets, SCORE, game_over
    all_sprites.empty();
    bullets.empty();
    enemies.empty();
    enemy_bullets.empty()
    SCORE = 0;
    game_over = False
    player = Nave();
    all_sprites.add(player)


def spawn_enemy():
    enemy = Inimigo();
    all_sprites.add(enemy);
    enemies.add(enemy)


def shoot():
    global SCORE
    now = pygame.time.get_ticks()
    if now - player.last_shot > player.shoot_delay:
        player.last_shot = now
        bullet = Projetil(player.rect.centerx, player.rect.top);
        all_sprites.add(bullet);
        bullets.add(bullet)
        laser_sound.play()
        pygame.time.set_timer(pygame.USEREVENT, 150)
        #SCORE += 1



def draw_text(screen, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size);
    text_surface = font.render(text, True, color);
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y);
    screen.blit(text_surface, text_rect)


def show_game_over_screen(screen, clock, reader_thread, serial_active):
    global running, game_over, waiting_for_input
    waiting_for_input = True
    # [Lógica da tela de game over está aqui]
    while waiting_for_input:
        screen.fill(BLACK);
        draw_text(screen, "G A M E   O V E R", 80, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(screen, f"Pontuação Final: {SCORE}", 40, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(screen, "Pressione [AÇÃO] ou [ESPAÇO] para Reiniciar", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.7)
        draw_text(screen, "Pressione [START] ou [ENTER] para Sair", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.8)
        pygame.display.flip();
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; waiting_for_input = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                if keys[pygame.K_SPACE]: waiting_for_input = False
                if keys[pygame.K_RETURN]: waiting_for_input = False; running = False
            if serial_active:
                state = reader_thread.control_state
                if state['BTN_A']: waiting_for_input = False
                if state['BTN_SW']: waiting_for_input = False; running = False
        if serial_active: time.sleep(0.1)

    # --- FUNÇÕES DE INPUT (para escopo global) ---


# [As funções handle_input_arduino e handle_input_teclado estão definidas no final]
def handle_input_arduino(reader_thread):
    global player
    state = reader_thread.control_state
    dx, dy = 0, 0
    if state['LEFT']: dx += 1;
    if state['RIGHT']: dx -= 1
    if state['UP']: dy += 1
    if state['DOWN']: dy -= 1
    player.update_position(dx, dy)
    if state['BTN_A']: shoot()
    if not state['BTN_A']: player.can_shoot = True


def handle_input_teclado():
    global player
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]: dx -= 1
    if keys[pygame.K_RIGHT]: dx += 1
    if keys[pygame.K_UP]: dy -= 1
    if keys[pygame.K_DOWN]: dy += 1
    player.update_position(dx, dy)
    if keys[pygame.K_SPACE]: shoot()
    if not keys[pygame.K_SPACE]: player.can_shoot = True


# --- LOOP PRINCIPAL DO JOGO ---

def game_loop(arduino_reader=None):
    global LAST_ENEMY_SPAWN_TIME, running, game_over, SCORE
    global laser_sound, explosion_sound

    ''''# 1. Tenta Inicializar o Leitor Serial no Thread (SEMPRE DENTRO DE UM TRY/EXCEPT)
    arduino_reader = ArduinoSerialReader(SERIAL_PORT, BAUD_RATE)

    try:
        arduino_reader.start()
        time.sleep(2)
        serial_active = arduino_reader.ser is not None and arduino_reader.ser.is_open
        print(f"Serial ativo? {serial_active}")

    except Exception:
        # Falha total na inicialização do thread/serial.
        print("AVISO: Falha grave ao iniciar o Thread Serial. O controle Arduino está DESATIVADO.")
        serial_active = False
    '''

    serial_active = arduino_reader and arduino_reader.ser and arduino_reader.ser.is_open

    # 2. Inicialização Pygame (SEMPRE AQUI)
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Controle Arcade Shooter")
    pygame.font.init()
    clock = pygame.time.Clock()
    running = True

    # --- CARREGAR FUNDO ---
    background = pygame.image.load(os.path.join(ASSETS_DIR, "img", "bg.png")).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    # Controle do movimento do fundo
    bg_y = 0
    bg_speed = 1  # quanto maior, mais rápido o fundo se move

    # --- CARREGAR SONS ---
    pygame.mixer.music.load(os.path.join(ASSETS_DIR, "sounds", "SpaceMusic.mp3"))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)  # toca continuamente

    laser_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "laser.wav"))
    laser_sound.set_volume(0.3)

    explosion_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "explosion1.mp3"))
    explosion_sound.set_volume(0.4)

    initialize_game()

    try:
        while running:
            # [O restante do loop de jogo permanece o mesmo...]

            if player.health <= 0:
                # cria explosao na posicao da nave
                explosion_sound.play()
                explosao = Explosao(player.rect.center)
                all_sprites.add(explosao)

                # para a musica de fundo suavemente
                pygame.mixer.music.fadeout(800)

                # desenha um pequeno loop para mostrar a animacao da explosao
                for _ in range(30):  # 30 frames ~ meio segundo a 60fps
                    all_sprites.update()
                    screen.blit(background, (0, bg_y))
                    screen.blit(background, (0, bg_y - SCREEN_HEIGHT))
                    all_sprites.draw(screen)
                    pygame.display.flip()
                    clock.tick(60)

                game_over = True

            if game_over:
                show_game_over_screen(screen, clock, arduino_reader, serial_active)
                if not running: break
                initialize_game()
                LAST_ENEMY_SPAWN_TIME = pygame.time.get_ticks()
                continue

                # --- Lógica de Spawn ---
            now = pygame.time.get_ticks()
            if now - LAST_ENEMY_SPAWN_TIME > ENEMY_SPAWN_RATE:
                LAST_ENEMY_SPAWN_TIME = now
                spawn_enemy()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # --- PROCESSAMENTO DE ENTRADA ---
            handle_input_teclado()
            if serial_active:
                handle_input_arduino(arduino_reader)

            # --- VERIFICAÇÃO DE COLISÕES e ATUALIZAÇÃO ---
            # [Colisões e atualização de scores e vida...]
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            if hits:
                for hit in hits:
                    SCORE += 10
                    if explosion_sound: explosion_sound.play()
                    explosao = Explosao(hit.rect.center)
                    all_sprites.add(explosao)

            hits = pygame.sprite.spritecollide(player, enemies, True)
            if hits: player.health -= 1; SCORE -= 5
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            if hits: player.health -= 1; SCORE -= 5
            if player.health <= 0: game_over = True

            all_sprites.update()

            # --- RENDERIZAÇÃO COM FUNDO EM MOVIMENTO ---
            bg_y += bg_speed
            if bg_y >= SCREEN_HEIGHT:
                bg_y = 0

            # desenha o fundo duas vezes, pra dar efeito de rolagem infinita
            screen.blit(background, (0, bg_y))
            screen.blit(background, (0, bg_y - SCREEN_HEIGHT))

            all_sprites.draw(screen)

            draw_text(screen, f"SCORE: {SCORE}", 36, SCREEN_WIDTH / 2, 10, WHITE)
            draw_text(screen, f"VIDA: {player.health}", 36, 100, 10, WHITE)
            status_color = GREEN if serial_active else RED
            draw_text(screen, "Arduino OK" if serial_active else "Teclado (Serial OFF)", 24, 100, 50, status_color)

            pygame.display.flip()
            clock.tick(60)

    finally:
        # Para e reinicializa o mixer completamente
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()  # fecha completamente o mixer

        # Limpa sprites globais
        all_sprites.empty()
        bullets.empty()
        enemies.empty()
        enemy_bullets.empty()

        # Não fecha o Pygame nem sai do programa
        return  # volta para o menu



if __name__ == '__main__':
    try:
        game_loop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Erro! Pressione ENTER para sair...")
