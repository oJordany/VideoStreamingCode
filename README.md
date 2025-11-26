# 🎬 RTP/RTSP Streamer - Cliente e Servidor de Streaming de Vídeo

<p align="center">
  <font size="7">🎥</font> <font size="7">📡</font>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Protocol-RTSP%20%7C%20RTP-red" alt="RTSP | RTP">
  <img src="https://img.shields.io/badge/GUI-Tkinter-yellow" alt="Tkinter">
  <img src="https://img.shields.io/badge/M%C3%ADdia-MJPEG%20%7C%20Pillow-green" alt="MJPEG | Pillow">
</p>

---

### 🎓 Contexto Acadêmico

Este projeto foi desenvolvido como parte dos requisitos da disciplina de **Redes Multimídia** da **Universidade Federal do Pará (UFPA)**.

---

## 📌 Protocolos e Objetivo

| Protocolo | Função no Projeto |
| :--- | :--- |
| **RTSP** | Usado para controle da sessão de *streaming*, incluindo comandos como SETUP, PLAY, PAUSE, DESCRIBE e TEARDOWN . A comunicação RTSP é realizada sobre **TCP**. |
| **RTP** | Usado para o transporte dos dados de vídeo (quadros) do servidor para o cliente . A transmissão RTP é realizada sobre **UDP** . |
| **SDP** | Usado para descrever os parâmetros do fluxo de mídia (codificação MJPEG, Payload Type 26) na resposta ao comando DESCRIBE . |

O objetivo primário foi implementar o protocolo RTSP no lado do cliente e o empacotamento RTP no lado do servidor .

---

## 💻 Tecnologias Utilizadas

| Categoria | Tecnologia | Uso |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.x | Linguagem principal para desenvolvimento do cliente e servidor. |
| **Interface** | Tkinter | Usado pelo cliente (`Client.py`) para construir a interface gráfica e os botões de controle (Setup, Play, Pause, Teardown) . |
| **Mídia** | PIL/Pillow | Usado pelo cliente para processar e exibir os quadros de vídeo JPEG recebidos via RTP. |
| **Rede** | Módulo `socket` | Usado para criar conexões TCP (RTSP) e sockets de datagrama UDP (RTP). |

---

## 📄 Estrutura do Código

| Arquivo | Descrição | Status |
| :--- | :--- | :--- |
| `Server.py` | Ponto de entrada do servidor. Escuta conexões RTSP/TCP de entrada. | Completo |
| `ServerWorker.py` | Lida com sessões RTSP individuais. Processa comandos RTSP e gerencia o *thread* de envio de pacotes RTP/UDP . Implementa a lógica do comando `DESCRIBE` (Tarefa Bônus) . | Completo |
| `RtpPacket.py` | Implementa a estrutura e a lógica de empacotamento (`encode`) e desempacotamento (`decode`) do cabeçalho RTP . | **Implementado** |
| `VideoStream.py` | Classe utilitária para ler quadros de um arquivo de vídeo de formato específico (`movie.Mjpeg`) . | Completo |
| `ClientLauncher.py` | Ponto de entrada do cliente. Inicializa a interface gráfica (`Tkinter`) e a classe `Client` . | Completo |
| `Client.py` | Classe principal do cliente. Lida com a interface do usuário, a lógica de estado RTSP (INIT, READY, PLAYING), e a escuta de pacotes RTP . | **Implementado** |

---

## 🚀 Como Executar o Projeto

Para executar o projeto, siga estes passos para garantir que o ambiente Python esteja configurado corretamente e que o servidor e o cliente sejam iniciados na ordem correta.

### 1. ⚙️ Configuração do Ambiente

Primeiro, garanta que o Python 3.x esteja instalado e use o `pip` para instalar a dependência **Pillow** (necessária para processamento de imagem no cliente).

1.  **Crie e Ative o Ambiente Virtual (Recomendado):**
    ```bash
    # Cria o venv (se ainda não existir)
    python -m venv venv 
    
    # Ativa no Linux/macOS
    source venv/bin/activate
    
    # Ativa no Windows (CMD/PowerShell)
    .\venv\Scripts\activate
    ```

2.  **Instale as Dependências:**
    ```bash
    # Instalar as dependências necessárias, incluindo Pillow
    pip install -r requirements.txt
    ```

### 2. ▶️ Iniciar o Servidor

O servidor deve ser iniciado primeiro. Ele escutará as solicitações de controle RTSP/TCP na porta especificada . Escolha uma porta maior que 1024 .

| Argumento | Descrição |
| :--- | :--- |
| `<server_port>` | A porta na qual o servidor escutará conexões RTSP (e.g., 8888) . |

```bash
python Server.py <server_port>

Aqui está a seção que faltava, formatada como bloco de código Markdown, incluindo os exemplos `bash`:

````
```bash
python Server.py <server_port>
````

**Exemplo:**

```bash
python Server.py 8888
```

### 3\. ▶️ Iniciar o Cliente

O cliente deve ser iniciado em uma janela separada. Ele requer quatro argumentos para estabelecer a conexão e especificar o fluxo de mídia.

| Argumento | Descrição |
| :--- | :--- |
| `<server_host>` |  O nome da máquina onde o servidor está em execução (e.g., `localhost`) . |
| `<server_port>` |  A porta RTSP na qual o servidor está escutando . |
| `<RTP_port>` |  A porta UDP que o cliente abrirá para receber os pacotes RTP de vídeo . |
| `<video_file>` |  O nome do arquivo de vídeo que você deseja solicitar (e.g., `movie.Mjpeg`) . |

```bash
python ClientLauncher.py <server_host> <server_port> <RTP_port> <video_file>
```

**Exemplo (Rodando na mesma máquina):**

```bash
python ClientLauncher.py localhost 8888 9000 movie.Mjpeg
```

### 4\. 🖱️ Interação RTSP

Use os botões na interface do cliente para controlar a sessão de streaming, seguindo a ordem padrão do protocolo.

| Ação | Estado Inicial | Comando RTSP Enviado | Descrição |
| :--- | :--- | :--- | :--- |
| **Setup** | INIT | SETUP |  Configura a sessão e os parâmetros de transporte . |
| **Play** | READY | PLAY |  Inicia a reprodução do vídeo . |
| **Pause** | PLAYING | PAUSE |  Pausa a reprodução . |
| **Teardown** | READY ou PLAYING | TEARDOWN |  Encerra a sessão e fecha a conexão . |

-----

## 🧑‍💻 Autores

Este projeto foi desenvolvido por:

  * **Syanne Karoline Moreira Tavares**
  * **Luiz Jordany de Sousa Silva**

**Disciplina:** Redes Multimídia

**Instituição:** Universidade Federal do Pará (UFPA)

-----