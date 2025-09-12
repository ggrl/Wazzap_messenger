import socket
import threading
import getpass

def receive_messages(sock):
    """Continuously receive messages from the server."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("[-] Disconnected from server")
                break
            text = data.decode()
            print(text, end="")  # print without extra newline
        except Exception as e:
            print(f"[!] Error receiving: {e}")
            break
    sock.close()

def start_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[*] Connected to chat server {host}:{port}")

    
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    
    try:
        username = input("Enter username: ")
        sock.sendall((username + "\n").encode())
        password = password = getpass.getpass("Enter password: ")
        sock.sendall((password + "\n").encode())

        
        while True:
            msg = input()
            if msg.lower() in ("quit", "exit"):
                break
            sock.sendall(msg.encode())
    except KeyboardInterrupt:
        print("\n[!] Client shutting down")
    finally:
        sock.close()


start_client(host="bcbxs-92-210-207-199.a.free.pinggy.link", port=34165)