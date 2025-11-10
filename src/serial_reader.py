import serial
import threading
import time
import sys

# --- CONFIGURAÇÕES DO HARDWARE ---
CENTER_VALUE = 512
DEADZONE = 50


class ArduinoSerialReader(threading.Thread):
    def __init__(self, port, baud_rate, timeout=0.01):
        super().__init__()
        self.daemon = True
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.running = True

        # Estrutura de estado LÓGICO universal que o jogo irá ler
        self.control_state = {
            'LEFT': False, 'RIGHT': False, 'UP': False, 'DOWN': False,
            'BTN_SW': False, 'BTN_A': False
        }

    def connect(self):
        """Tenta abrir a porta serial."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)
            self.ser.reset_input_buffer()
            print(f"SerialReader: Conectado em {self.port}")
            return True
        except serial.SerialException as e:
            print(f"SerialReader ERRO: Falha ao abrir a porta serial {self.port}. {e}", file=sys.stderr)
            return False

    def _translate_to_logic(self, x, y, sw, btn_a):
        """CONVERTE VALORES BRUTOS (0-1023) EM COMANDOS LÓGICOS (True/False)."""

        # 1. Eixo X (Movimento Horizontal)
        self.control_state['LEFT'] = (x < CENTER_VALUE - DEADZONE)
        self.control_state['RIGHT'] = (x > CENTER_VALUE + DEADZONE)

        # 2. Eixo Y (Movimento Vertical) - LÓGICA INVERTIDA CORRIGIDA
        self.control_state['UP'] = (y > CENTER_VALUE + DEADZONE)
        self.control_state['DOWN'] = (y < CENTER_VALUE - DEADZONE)

        # 3. Botões (0 = Pressionado devido ao INPUT_PULLUP)
        self.control_state['BTN_SW'] = (sw == 0)
        self.control_state['BTN_A'] = (btn_a == 0)

    def read_line(self):
        """Lê a linha, traduz e atualiza o estado."""
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    x, y, sw, btn_a = map(int, line.split(','))
                    self._translate_to_logic(x, y, sw, btn_a)
            except (ValueError, serial.SerialException):
                pass

    def run(self):
        """Loop principal do Thread."""
        if not self.connect():
            self.running = False
            return

        while self.running:
            self.read_line()
            time.sleep(0.005)

    def stop(self):
        """Para o thread e fecha a porta serial."""
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("SerialReader: Thread encerrado.")