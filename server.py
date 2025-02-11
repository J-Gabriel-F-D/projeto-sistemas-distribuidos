import socket
import threading
import json
import os

LOCK = threading.Lock()
DATA_FILE = 'server_data.json'
SERVER_PORT = 1234

def load_data():
    with LOCK:
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, 'r') as file:
            return json.load(file)

def save_data(data):
    with LOCK:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file)

def handle_client(client_socket, client_address, data):
    client_ip = client_address[0]
    
    try:
        while (message := client_socket.recv(1024).decode()):
            print(f"[LOG] {client_ip} sent: {message}")
            command, *args = message.split()
            response = process_command(command, args, client_ip, data)
            client_socket.sendall(response.encode())
    except Exception as e:
        print(f"[ERROR] {client_ip}: {e}")
    finally:
        client_socket.close()

def process_command(command, args, client_ip, data):
    if command == 'JOIN':
        if client_ip not in data:
            data[client_ip] = []
            save_data(data)
            return "CONFIRMJOIN"
        return "CLIENTALREADYCONNECTED"
    
    elif command == 'CREATEFILE':
        if len(args) != 2:
            return "INVALIDCOMMAND"
        filename, size = args
        size = int(size)
        if any(f['filename'] == filename for f in data.get(client_ip, [])):
            return "FILEALREADYEXISTS"
        data[client_ip].append({"filename": filename, "size": size})
        save_data(data)
        return "CONFIRMCREATEFILE"
    
    elif command == 'DELETEFILE':
        if len(args) != 1:
            return "INVALIDCOMMAND"
        filename = args[0]
        if any(f['filename'] == filename for f in data.get(client_ip, [])):
            data[client_ip] = [f for f in data[client_ip] if f['filename'] != filename]
            save_data(data)
            return "CONFIRMDELETEFILE"
        return "FILENOTFOUND"
    
    elif command == 'SEARCH':
        if len(args) != 1:
            return "INVALIDCOMMAND"
        filename = args[0]
        results = [f"FILE {f['filename']} {ip} {f['size']}" for ip, files in data.items() for f in files if f['filename'] == filename]
        return "\n".join(results) if results else "FILENOTFOUND"
    
    elif command == 'LEAVE':
        if client_ip in data:
            del data[client_ip]
            save_data(data)
            return "CONFIRMLEAVE"
        return "CLIENTNOTFOUND"
    
    elif command == 'LISTFILES':
        # files = data.get(client_ip, [])
        # return "\n".join(f"{file['filename']} {file['size']}" for file in files) if files else "NOFILES"
        files = [f"FILE {file['filename']} {ip} {file['size']}" for ip, files in data.items() for file in files]
        return "\n".join(files) if files else "NOFILES"
    # elif command == 'LISTALLFILES':
    
    return "UNKNOWNCOMMAND"

def main():
    data = load_data()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("", SERVER_PORT))
        server_socket.listen(5)
        print(f"[SERVER] Listening on port {SERVER_PORT}")
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"[CONNECTION] {client_address} connected.")
                threading.Thread(target=handle_client, args=(client_socket, client_address, data), daemon=True).start()
        except KeyboardInterrupt:
            print("[SERVER] Shutting down.")

if __name__ == "__main__":
    main()
