// --- Definição dos Pinos ---

// Pinos Analógicos para o Joystick
// O Arduino Mega tem mais pinos analógicos, mas A0 e A1 são universais.
#define JOY_Y A0
#define JOY_X A1

// Pinos Digitais para os Botões
// D2 e D3 são usados como exemplo. Para o botão do joystick (SW), o pull-up interno é ideal.
#define BUTTON_SW 2 // Botão do joystick (SW)
#define BUTTON_A 3  // Botão extra (para o módulo de botão)

// Taxa de Comunicação: Rápida para garantir baixa latência
#define BAUD_RATE 115200 

void setup() {
  // 1. Inicializa a comunicação serial
  Serial.begin(BAUD_RATE);
  
  // 2. Configura os pinos dos botões como INPUT_PULLUP
  // Isso elimina a necessidade de resistores externos. O pino lê LOW (0) quando o botão é pressionado.
  pinMode(BUTTON_SW, INPUT_PULLUP);
  pinMode(BUTTON_A, INPUT_PULLUP);
  
  // Pinos analógicos (A0, A1) não precisam de pinMode em placas AVR (como o Uno/Mega)
}

void loop() {
  // --- 1. Leitura dos Valores ---
  
  // Valores Analógicos (0 a 1023)
  int xValue = analogRead(JOY_X);
  int yValue = analogRead(JOY_Y);
  
  // Valores Digitais (HIGH=1 = Não Pressionado; LOW=0 = Pressionado)
  int btnSW = digitalRead(BUTTON_SW); 
  int btnA = digitalRead(BUTTON_A);
  
  // --- 2. Envio da Saída Serial (Formato CSV) ---
  
  // Envia no formato: X,Y,SW,A\n
  // Exemplo de saída: 512,512,1,1
  
  Serial.print(xValue);
  Serial.print(",");
  Serial.print(yValue);
  Serial.print(",");
  Serial.print(btnSW); 
  Serial.print(",");
  Serial.println(btnA); // Usa println para adicionar a quebra de linha (\n)
  
  // Pequeno atraso para estabilidade e para o Python ter tempo de ler
  // Se o delay for muito alto, o controle fica lento. Se for muito baixo, pode haver congestionamento.
  delay(5); 
}
