import socket
import threading
import os

# Lista para armazenar os sockets dos clientes conectados
clients = []

# Função para lidar com cada cliente
def handle_client(client_socket, client_address):
    print(f"Conexão recebida de {client_address}")
    clients.append(client_socket)
    try:
        while True:
            # Receber a mensagem ou comando
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f"Cliente {client_address} desconectado.")
                break

            # Verificar se é um comando de envio de arquivo
            if data.startswith("UPLOAD"):
                _, filename, filesize = data.split("|")
                filesize = int(filesize)
                receive_file(client_socket, filename, filesize)
            elif data.startswith("DOWNLOAD"):
                _, filename = data.split("|")
                send_file(client_socket, filename)
            else:
                print(f"Mensagem recebida de {client_address}: {data}")
                # Redirecionar a mensagem para todos os outros clientes
                broadcast_message(data, client_socket)
    except ConnectionResetError:
        print(f"Cliente {client_address} desconectado abruptamente.")
    finally:
        clients.remove(client_socket)
        client_socket.close()

# Função para receber arquivos enviados por um cliente
def receive_file(client_socket, filename, filesize):
    with open(f"shared_{filename}", "wb") as f:
        received_bytes = 0
        while received_bytes < filesize:
            data = client_socket.recv(1024)
            if not data:
                break
            f.write(data)
            received_bytes += len(data)
    print(f"Arquivo {filename} recebido e salvo como shared_{filename}.")

# Função para enviar arquivos a um cliente
def send_file(client_socket, filename):
    if not os.path.exists(f"shared_{filename}"):
        client_socket.send("ERROR: File not found".encode('utf-8'))
        return

    filesize = os.path.getsize(f"shared_{filename}")
    client_socket.send(f"FILE|{filename}|{filesize}".encode('utf-8'))

    with open(f"shared_{filename}", "rb") as f:
        while chunk := f.read(1024):
            client_socket.send(chunk)
    print(f"Arquivo {filename} enviado ao cliente.")

# Função para redirecionar a mensagem para todos os clientes conectados
def broadcast_message(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

# Criando o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'  # Aceita conexões de qualquer IP
port = 12345
server_socket.bind((host, port))
server_socket.listen(5)  # Até 5 conexões pendentes
print(f"Servidor escutando na porta {port}...")

# Loop principal do servidor
try:
    while True:
        client_socket, client_address = server_socket.accept()
        # Criar uma nova thread para lidar com o cliente
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
except KeyboardInterrupt:
    print("\nServidor encerrado.")
finally:
    server_socket.close()
