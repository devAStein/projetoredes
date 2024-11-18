import socket as sock
import threading

clients = {}  # Dicionário para armazenar os clientes conectados e seus sockets

def mostrar_clientes():
    """Função para listar todos os clientes conectados."""
    print("\nAtualizando lista de clientes conectados:")
    if clients:
        for nome in clients.keys():
            print(f"- {nome}")
    else:
        print("Nenhum cliente conectado no momento.")
    print("\n")

def broadcast(mensagem, remetente):
    """Envia uma mensagem para todos os clientes, exceto o remetente."""
    for cliente_nome, sock_conn in clients.items():
        if sock_conn != remetente:  # Evitar enviar para o próprio remetente
            try:
                sock_conn.send(mensagem.encode())
            except:
                remover(sock_conn, cliente_nome)

def unicast(mensagem, remetente_nome, nome_destinatario):
    """Envia uma mensagem apenas para o destinatário especificado."""
    if nome_destinatario in clients:
        try:
            clients[nome_destinatario].send(f"Privado de {remetente_nome} >> {mensagem}".encode())
        except:
            remover(clients[nome_destinatario], nome_destinatario)
    else:
        clients[remetente_nome].send(f"Cliente {nome_destinatario} não encontrado.".encode())

def remover(sock_conn, nome):
    """Remove o cliente do dicionário e fecha sua conexão."""
    if nome in clients:
        del clients[nome]
        print(f"Cliente {nome} ({sock_conn.getpeername()}) foi desconectado.")
        sock_conn.close()
        mostrar_clientes()  # Atualiza a lista de clientes

def receber_dados(sock_conn, endereco):
    """Recebe e processa as mensagens dos clientes."""
    try:
        nome = sock_conn.recv(50).decode()
        if not nome:
            raise ValueError("Nome vazio recebido.")
        print(f"Conexão estabelecida com {nome} : {endereco}")

        # Adicionar o cliente ao dicionário
        clients[nome] = sock_conn
        mostrar_clientes()  # Atualiza a lista de clientes

        while True:
            mensagem = sock_conn.recv(1024).decode()
            if mensagem:
                if mensagem.upper() == "SAIR":
                    print(f"{nome} solicitou para sair.")
                    remover(sock_conn, nome)
                    break
                elif mensagem.startswith("@"):
                    nome_destinatario, msg = mensagem[1:].split(" ", 1)
                    unicast(msg, nome, nome_destinatario)
                else:
                    print(f"{nome} >> {mensagem}")
                    broadcast(f"{nome} >> {mensagem}", sock_conn)
            else:
                remover(sock_conn, nome)
                break
    except Exception as e:
        print(f"Erro com o cliente {endereco} - {e}")
        remover(sock_conn, nome)

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORTA = 9999        # Porta do servidor

# Criar o socket do servidor
socket_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket_server.bind((HOST, PORTA))
socket_server.listen()

print(f"O servidor {HOST}:{PORTA} está aguardando conexões...")

# Loop principal para receber conexões
while True:
    sock_conn, ender = socket_server.accept()
    print(f"Nova conexão de {ender}")

    # Criar uma thread para lidar com o cliente
    thread_cliente = threading.Thread(target=receber_dados, args=(sock_conn, ender))
    thread_cliente.start()
