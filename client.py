import socket
import os

# Função para enviar uma mensagem ao servidor
def send_message(client_socket):
    message = input("Digite a mensagem: ")
    client_socket.send(message.encode('utf-8'))
    print("Mensagem enviada.")

# Função para fazer upload de um arquivo para o servidor
def upload_file(client_socket):
    filename = input("Digite o nome do arquivo para enviar: ").strip()
    if not os.path.exists(filename):
        print(f"Arquivo {filename} não encontrado!")
        return

    filesize = os.path.getsize(filename)
    client_socket.send(f"UPLOAD|{filename}|{filesize}".encode('utf-8'))

    with open(filename, "rb") as f:
        while chunk := f.read(1024):
            client_socket.send(chunk)
    print(f"Arquivo {filename} enviado com sucesso.")

# Função para fazer download de um arquivo do servidor
def download_file(client_socket):
    filename = input("Digite o nome do arquivo para baixar: ").strip()
    client_socket.send(f"DOWNLOAD|{filename}".encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')

    if response.startswith("FILE"):
        _, filename, filesize = response.split("|")
        filesize = int(filesize)
        with open(f"downloaded_{filename}", "wb") as f:
            received_bytes = 0
            while received_bytes < filesize:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                received_bytes += len(data)
        print(f"Arquivo {filename} baixado com sucesso.")
    else:
        print(response)

# Função principal do cliente
def client_program():
    server_ip = input("Digite o IP do servidor (padrão: localhost): ").strip() or "localhost"
    server_port = int(input("Digite a porta do servidor (padrão: 12345): ").strip() or 12345)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, server_port))
        print("Conectado ao servidor.")
        print("\nComandos disponíveis:")
        print("1 - Enviar mensagem")
        print("2 - Fazer upload de arquivo")
        print("3 - Fazer download de arquivo")
        print("4 - Sair")

        while True:
            command = input("\nEscolha uma opção (1/2/3/4): ").strip()
            if command == "1":
                send_message(client_socket)
            elif command == "2":
                upload_file(client_socket)
            elif command == "3":
                download_file(client_socket)
            elif command == "4":
                print("Encerrando conexão...")
                break
            else:
                print("Comando inválido. Tente novamente.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client_socket.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    client_program()
