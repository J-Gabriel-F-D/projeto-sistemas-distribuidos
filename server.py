import socket
import threading

# Lista para armazenar os sockets dos clientes conectados
clients = []

# Função para lidar com cada cliente
def handle_client(client_socket, client_address):
    print(f"Conexão recebida de {client_address}")
    clients.append(client_socket)
    try:
        while True:
            # Receber a mensagem
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                # Finaliza a conexão se o cliente encerrar
                print(f"Cliente {client_address} desconectado.")
                break
            print(f"Mensagem recebida de {client_address}: {message}")
            # Redirecionar a mensagem para todos os outros clientes
            broadcast_message(message, client_socket)
    except ConnectionResetError:
        print(f"Cliente {client_address} desconectado abruptamente.")
    finally:
        clients.remove(client_socket)
        client_socket.close()

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
