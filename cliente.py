import tkinter as tk
from tkinter import scrolledtext
import socket as sock
import threading

# Configurações do cliente
HOST = '127.0.0.1'  # IP do servidor
PORTA = 9999        # Porta do servidor

# Criamos o socket do cliente
socket_cliente = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket_cliente.connect((HOST, PORTA))

# Envia o nome do cliente ao servidor antes de entrar no loop
nome = input("1° Informe seu nome para entrar no chat:\n" "Para mandar uma mensagem privada coloque => @nome_destinatario mensagem\n" "Para sair do chat digite na interfaz => ""SAIR"" \n")
socket_cliente.sendall(nome.encode())

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        # Área de chat (Texto desplazable)
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=20)
        self.chat_area.grid(column=0, row=0, padx=10, pady=10, columnspan=2)
        self.chat_area.config(background="#58D3F7")

        # Entrada de mensagem
        self.mensagem_entry = tk.Entry(root, width=40)
        self.mensagem_entry.grid(column=0, row=1, padx=10, pady=10)
        self.mensagem_entry.bind("<Return>", self.enviar_mensagem)  # Enviar mensagem ao pressionar Enter

        # Botão para enviar
        self.enviar_button = tk.Button(root, text="Enviar", command=self.enviar_mensagem)
        self.enviar_button.grid(column=1, row=1, padx=10, pady=10)
        self.enviar_button.config(background="#01DF3A")

        # Iniciar thread para receber mensagens
        self.recibir_thread = threading.Thread(target=self.receber_mensagens)
        self.recibir_thread.daemon = True
        self.recibir_thread.start()

    def enviar_mensagem(self, event=None):
        mensagem = self.mensagem_entry.get()
        if mensagem.upper() == "SAIR":
            try:
                socket_cliente.sendall("SAIR".encode())
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "Você saiu do chat.\n")
                self.chat_area.config(state='disabled')
                socket_cliente.close()
                self.root.quit()  # Fechar a interface do Tkinter
            except:
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "Erro ao sair. Conexão já encerrada.\n")
                self.chat_area.config(state='disabled')
        else:
            # Envia a mensagem normal
            try:
                socket_cliente.sendall(mensagem.encode())
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, f"Você: {mensagem}\n")
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)
                self.mensagem_entry.delete(0, tk.END)
            except:
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "Erro ao enviar mensagem. Conexão encerrada.\n")
                self.chat_area.config(state='disabled')
                socket_cliente.close()

    def receber_mensagens(self):
        while True:
            try:
                mensagem = socket_cliente.recv(1024).decode()
                if mensagem:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, mensagem + "\n")
                    self.chat_area.config(state='disabled')
                    self.chat_area.yview(tk.END)
                else:
                    print("Conexão com o servidor encerrada.")
                    socket_cliente.close()
                    break
            except:
                print("Erro ao receber mensagem... fechando conexão")
                socket_cliente.close()
                break

# Iniciar a interface Tkinter
root = tk.Tk()
app = ChatApp(root)
root.mainloop()

