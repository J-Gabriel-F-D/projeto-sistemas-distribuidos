import socket
import threading
import os
import sys

SERVER_PORT = 1234
CLIENT_PORT = 1235
PUBLIC_FOLDER = "./public"

if not os.path.exists(PUBLIC_FOLDER):
    os.makedirs(PUBLIC_FOLDER)

def send_request(server_ip, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(10)  # Timeout para evitar bloqueio
            client_socket.connect((server_ip, SERVER_PORT))
            client_socket.sendall(message.encode())
            response = client_socket.recv(4096).decode()
            if not response:
                return "[ERROR] No response from server."
            return response
    except socket.timeout:
        return "[ERROR] Connection timed out."
    except socket.error as e:
        return f"[ERROR] Socket error: {e}"
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"

def join_server(server_ip):
    response = send_request(server_ip, f"JOIN {server_ip}\n")
    print(response)

def refresh_list(server_ip):
    try:
        files_local = {f for f in os.listdir(PUBLIC_FOLDER) if os.path.isfile(os.path.join(PUBLIC_FOLDER, f))}
        response = send_request(server_ip, "LISTFILES\n")
        files_server = set() if response == "NOFILES" else {line.split()[0] for line in response.split("\n") if line}
        
        for file in files_local - files_server:
            try:
                size = os.path.getsize(os.path.join(PUBLIC_FOLDER, file))
                print(send_request(server_ip, f"CREATEFILE {file} {size}\n"))
            except OSError as e:
                print(f"[ERROR] Could not get size of file {file}: {e}")
        
        for file in files_server - files_local:
            print(send_request(server_ip, f"DELETEFILE {file}\n"))
    except Exception as e:
        print(f"[ERROR] Error refreshing list: {e}")

def search_file(server_ip, filename):
    response = send_request(server_ip, f"SEARCH {filename}\n")
    print(response)
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    if total == 0:
        total = 1

    percent = f"{100 * (iteration / float(total)):.{decimals}f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if iteration >= total:
        print() 

def get_file(client_ip, filename, offset_start, offset_end=None):
    try:
        # Verifica se o arquivo existe no servidor antes de tentar baixar
        response = send_request(client_ip, f"SEARCH {filename}\n")
        if "not found" in response.lower():
            print(f"[ERROR] File {filename} not found on the server.")
            return

        # Converter offsets para inteiros
        int_offset_start = int(offset_start)
        if offset_end:
            int_offset_end = int(offset_end)
            total_bytes = int_offset_end - int_offset_start
            message = f"GET {filename} {int_offset_start} {int_offset_end}\n"
        else:
            # Tenta extrair o tamanho do arquivo a partir da resposta da SEARCH.
            # Supondo que a resposta esteja no formato: "FOUND <filename> <filesize>"
            tokens = response.split()
            if len(tokens) >= 3 and tokens[0].upper() == "FOUND":
                filesize = int(tokens[2])
                total_bytes = filesize - int_offset_start
            else:
                total_bytes = None
            message = f"GET {filename} {int_offset_start}\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(10)  # Timeout para evitar bloqueio
            client_socket.connect((client_ip, CLIENT_PORT))
            client_socket.sendall(message.encode())
            downloaded = 0
            with open(os.path.join(PUBLIC_FOLDER, filename), 'wb') as file:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    downloaded += len(data)
                    # Se o tamanho total for conhecido, atualiza a barra com porcentagem
                    if total_bytes:
                        print_progress_bar(downloaded, total_bytes, prefix="Downloading", suffix="Complete", length=50)
                    else:
                        # Caso o total não seja conhecido, mostra apenas os bytes baixados
                        sys.stdout.write(f"\rDownloading: {downloaded} bytes")
                        sys.stdout.flush()
            if not total_bytes:
                sys.stdout.write("\n")
            print(f"[INFO] File {filename} downloaded successfully.")
    except socket.timeout:
        print(f"[ERROR] Connection timed out while downloading {filename}.")
    except socket.error as e:
        print(f"[ERROR] Socket error while downloading {filename}: {e}")
    except OSError as e:
        print(f"[ERROR] File system error while downloading {filename}: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while downloading {filename}: {e}")

def handle_file_request(client_socket):
    try:
        request = client_socket.recv(1024).decode().split()
        if request[0] == "GET" and len(request) >= 3:
            filename, offset_start = request[1], int(request[2])
            offset_end = int(request[3]) if len(request) == 4 else None
            file_path = os.path.join(PUBLIC_FOLDER, filename)
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file.seek(offset_start)
                    data = file.read(offset_end - offset_start if offset_end else None)
                    client_socket.sendall(data)
            else:
                client_socket.sendall(b"FILENOTFOUND")
    except ValueError:
        print("[ERROR] Invalid offset value in request.")
    except OSError as e:
        print(f"[ERROR] File system error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error handling file request: {e}")
    finally:
        client_socket.close()

def start_file_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("", CLIENT_PORT))
            server_socket.listen(5)
            while True:
                client_socket, _ = server_socket.accept()
                threading.Thread(target=handle_file_request, args=(client_socket,), daemon=True).start()
    except socket.error as e:
        print(f"[ERROR] Server socket error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected server error: {e}")
        sys.exit(1)

def leave_server(server_ip):
    response = send_request(server_ip, "LEAVE\n")
    print(response)

def list_files(server_ip):
    """
    Solicita ao servidor a lista de arquivos disponíveis e a exibe.
    """
    response = send_request(server_ip, "LISTALLFILES\n")
    if response == "NOFILES":
        print("[INFO] No files available on the server.")
    else:
        print("Files available on the server:")
        for line in response.split("\n"):
            if line:  # Ignora linhas vazias
                print(f"- {line}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Welcome to the File Sharing Application!\n")

    while True:
        try:
            # Exibe o menu de opções
            print("Please select an option:")
            print("1 - JOIN")
            print("2 - REFRESH")
            print("3 - SEARCH")
            print("4 - GET")
            print("5 - LEAVE")
            print("6 - LIST FILES")
            print("7 - EXIT")
            choice = input("Enter the number of your choice: ").strip()

            # Processa a escolha do usuário
            if choice == "1":  # JOIN
                server_ip = input("Enter the server IP to join: ").strip()
                join_server(server_ip)
                input("\nPress Enter to continue...")

            elif choice == "2":  # REFRESH
                server_ip = input("Enter the server IP to refresh: ").strip()
                refresh_list(server_ip)
                input("\nPress Enter to continue...")

            elif choice == "3":  # SEARCH
                server_ip = input("Enter the server IP to search: ").strip()
                filename = input("Enter the filename to search: ").strip()
                search_file(server_ip, filename)
                input("\nPress Enter to continue...")

            elif choice == "4":  # GET
                client_ip = input("Enter the client IP to download from: ").strip()
                filename = input("Enter the filename to download: ").strip()
                offset_start = input("Enter the starting offset: ").strip()
                offset_end = input("Enter the ending offset (optional, press Enter to skip): ").strip()
                if offset_end:
                    get_file(client_ip, filename, offset_start, offset_end)
                else:
                    get_file(client_ip, filename, offset_start)
                input("\nPress Enter to continue...")

            elif choice == "5":  # LEAVE
                server_ip = input("Enter the server IP to leave: ").strip()
                leave_server(server_ip)
                input("\nPress Enter to continue...")

            elif choice == "6":  # LIST FILES
                server_ip = input("Enter the server IP to list files: ").strip()
                list_files(server_ip)
                input("\nPress Enter to continue...")

            elif choice == "7":  # EXIT
                print("[INFO] Exiting the application. Goodbye!")
                break

            else:
                print("[ERROR] Invalid choice. Please select a number between 1 and 7.")
                input("\nPress Enter to continue...")

            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
            os.system('cls' if os.name == 'nt' else 'clear')
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    threading.Thread(target=start_file_server, daemon=True).start()
    main()
