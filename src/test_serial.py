from src.serial_reader import ArduinoSerialReader
import time

# Altere a porta conforme seu sistema:
#   Linux/Mac -> '/dev/ttyUSB0'  ou '/dev/ttyACM0'
#   Windows    -> 'COM3', 'COM4', etc.
PORT = '/dev/ttyUSB0'
BAUD = 115200

reader = ArduinoSerialReader(PORT, BAUD)

try:
    reader.start()
    time.sleep(2)  # dá tempo para a conexão estabilizar
    print("Leitura iniciada. Pressione Ctrl+C para sair.\n")

    while True:
        print(reader.control_state)
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nEncerrando...")
finally:
    reader.stop()
