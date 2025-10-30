import serial
import time
from pynput.keyboard import Key, Controller
import sys

# --- CONFIGURAÇÕES CRÍTICAS ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
DEADZONE = 50  # Centro (512) +/- 50. Range de centro: 462 a 562.
CENTER_VALUE = 512

# --- Mapeamento de Teclas para Emuladores ---
KEY_MAPPINGS = {
    'UP': Key.up,
    'DOWN': Key.down,
    'LEFT': Key.left,
    'RIGHT': Key.right,
    'BUTTON_SW': 'z',  # Botão do Joystick (SW) -> Ação Principal
    'BUTTON_A': 'x'  # Botão Extra (A) -> Ação Secundária
}
# -------------------------------------------

keyboard = Controller()
current_keys_pressed = set()


# --- Funções Auxiliares ---

def _press_key(key_char):
    if key_char not in current_keys_pressed:
        try:
            keyboard.press(key_char)
            current_keys_pressed.add(key_char)
        except Exception as e:
            # Captura exceções para não interromper a execução do loop
            pass


def _release_key(key_char):
    if key_char in current_keys_pressed:
        try:
            keyboard.release(key_char)
            current_keys_pressed.remove(key_char)
        except Exception as e:
            # Captura exceções para não interromper a execução do loop
            pass

        # --- Lógica de Controle do Joystick (COM INVERSÃO DE Y) ---


# ... (código anterior)

def handle_joystick(x, y):
    """Traduz as leituras X e Y em comandos de SETA (Y invertido para corrigir o hardware)."""

    # 1. Movimento Horizontal (X) - Permanece o mesmo (Não invertido)
    if x < CENTER_VALUE - DEADZONE:
        # Pressiona Esquerda (baixo valor)
        _press_key(KEY_MAPPINGS['LEFT'])
        _release_key(KEY_MAPPINGS['RIGHT'])
    elif x > CENTER_VALUE + DEADZONE:
        # Pressiona Direita (alto valor)
        _press_key(KEY_MAPPINGS['RIGHT'])
        _release_key(KEY_MAPPINGS['LEFT'])
    else:
        # Eixo X no centro: Solta ambas
        _release_key(KEY_MAPPINGS['LEFT'])
        _release_key(KEY_MAPPINGS['RIGHT'])

    # 2. Movimento Vertical (Y) - LÓGICA INVERTIDA APLICADA AQUI
    if y < CENTER_VALUE - DEADZONE:
        # Valor BAIXO (perto de 0) -> Corrigimos para BAIXO (DOWN)
        _press_key(KEY_MAPPINGS['DOWN'])
        _release_key(KEY_MAPPINGS['UP'])
    elif y > CENTER_VALUE + DEADZONE:
        # Valor ALTO (perto de 1023) -> Corrigimos para CIMA (UP)
        _press_key(KEY_MAPPINGS['UP'])
        _release_key(KEY_MAPPINGS['DOWN'])
    else:
        # Eixo Y no centro: Solta ambas
        _release_key(KEY_MAPPINGS['UP'])
        _release_key(KEY_MAPPINGS['DOWN'])


# --- Lógica de Controle dos Botões ---

def handle_buttons(sw, btn_a):
    """Traduz os estados digitais (0/1) em comandos de tecla."""

    # Lembre-se: 0 = Pressionado (por causa do INPUT_PULLUP no Arduino)

    # Botão SW (Terceiro valor na Serial)
    if sw == 0:
        _press_key(KEY_MAPPINGS['BUTTON_SW'])
    else:
        _release_key(KEY_MAPPINGS['BUTTON_SW'])

    # Botão A (Quarto valor na Serial)
    if btn_a == 0:
        _press_key(KEY_MAPPINGS['BUTTON_A'])
    else:
        _release_key(KEY_MAPPINGS['BUTTON_A'])


# --- LOOP PRINCIPAL ---

try:
    # 1. Tenta abrir a comunicação serial
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
    time.sleep(2)
    print(f"--- Conectado com sucesso ao Arduino em {SERIAL_PORT} ---")
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()

            if line:
                try:
                    # 3. Processa a string
                    x, y, sw, btn_a = map(int, line.split(','))

                    # 4. Envia os comandos de teclado
                    handle_joystick(x, y)
                    handle_buttons(sw, btn_a)

                except ValueError:
                    continue

        time.sleep(0.005)

except serial.SerialException as e:
    print(f"\nERRO DE COMUNICAÇÃO SERIAL: Verifique a porta {SERIAL_PORT}.", file=sys.stderr)
    print(f"Detalhes do erro: {e}", file=sys.stderr)

except KeyboardInterrupt:
    print("\n\nEncerrado pelo usuário (Ctrl+C).", file=sys.stderr)

except Exception as e:
    print(f"\nOCORREU UM ERRO INESPERADO: {e}", file=sys.stderr)

finally:
    # 5. GARANTE que todas as teclas pressionadas sejam liberadas ao encerrar o script.
    if current_keys_pressed:
        print("\nLiberando todas as teclas ativas...", file=sys.stderr)
        for key in list(current_keys_pressed):
            _release_key(key)
    print("Script encerrado.", file=sys.stderr)