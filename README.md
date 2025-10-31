## Componentes
Para o projeto são necessários:

1. Arduino Uno ou Mega.
2. Cabo de dados.
2. Módulo Joystick.
3. Módulo de Botão.
4. Jumpers de conexão.
5. Protoboard _(opcional)_.

## Conexões físicas
Esquema de ligações

<p align="center">
    <img src="imgs/esquema.png" width="600">
</p>

Siga os passos abaixo para conectar todos os fios nas portas corretas:

> ⚠️ **Atenção:**  Mantenha o Arduino desconectado/desligado durante o processo.

### Módulo de Botão 🔘
- <p style="color:purple;">Conecte o pino "S" do módulo, com a porta digital 3</p>
- <p style="color:red;">Conecte o pino central do módulo, com a porta digital 5v</p>
- <p style=";">Conecte o pino central do módulo, com a porta digital GND</p>

### Módulo de Joystick 🕹️
- <p style=";">Conecte o pino "GND" do módulo, com a porta digital GND</p>
- <p style="color:red;">Conecte o pino "+5v" do módulo, com a porta digital 5v</p>
- <p style="color:green;">Conecte o pino "VRx" do módulo, com a porta analógica A0</p>
- <p style="color:blue;">Conecte o pino "VRy" do módulo, com a porta analógica A1</p>
- <p style="color:orange;">Conecte o pino "SW" do módulo, com a porta digital 2</p>

## Conectando com o Arduino IDE
Usaremos o software Arduino IDE para programação.

👉 [**Baixe o Arduino IDE aqui**](https://www.arduino.cc/en/software)

### Configurando ambiente
Após iniciar o  software, você verá o ambiente de trabalho:
<p align="center">
    <img src="imgs/homeArduinoIDE.png" width="600">
</p>

Conecte o Arduino a uma porta USB.

#### Placa
No menu "Ferramentas", clique em "placa" e selecione: "Arduino Uno"
<p align="center">
    <img src="imgs/configBoard.png" width="600">
</p>

#### Porta
No mesmo menu, clique em "Porta" e selecione a porta disponível
<p align="center">
    <img src="imgs/configPort.png" width="600">
</p>

#### Monitor Serial
No mesmo menu, clique em "Monitor Serial". 
<p align="center">
    <img src="imgs/configMonSerial.png" width="600">
</p>

Uma nova janela abrirá. Este é o monitor serial, usaremos ele para observar as saídas do programa.

No canto inferior direito, clique na caixa e escolha _"115200 velocidade"_.
<p align="center">
    <img src="imgs/monSerial.png" width="600">
</p>
Esta é a velocidade que a nossa porta serial estará usando para comunicação. É essencial fazer este passo para que não ocorram erros de exibição dos dados.

## Movimentação na tela
O [Emulador de Joystick](https://github.com/VitorRibe/joystick_secomp/blob/main/joystick_emulador.py)
recebe os dados do Arduino e decide qual dos comandos de teclado abaixo enviar para o computador:

### joystick 🕹️
- **Seta para cima ⬆️** = _quando pressionado joystick para cima_
- **Seta para baixo ⬇️** = _quando pressionado joystick para baixo_
- **Seta para esquerda ⬅️** = _quando pressionado joystick para esquerda_
- **Seta para direita ➡️** = _quando pressionado joystick para direita_

### botões 🔘
- **letra z** = _quando pressionado botão da direita_
- **letra x** = _quando pressionado botão da esquerda_

<footer style="border-top: 1px solid #ccc; padding-top: 10px;">
  <div align="center">
    <br>
    <a href="https://prototipe.tec.br/" target="_blank">
      <img src="imgs/logo.png" width="100" alt="Logo Prototipe Jr.">
    </a>
    <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank"></a>
    <br>
    Projeto desenvolvido pelos membros discentes em Ciência da Computação da empresa júnior Prototipe Jr.<br>
    <br>
  </div>
</footer>
