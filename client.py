import socket
import threading

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("[-] Disconnected from server")
                break
            print(data.decode())
        except Exception as e:
            print(f"[!] Error receiving: {e}")
            break
    sock.close()

def start_client(host="127.0.0.1", port=42000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[*] Connected to chat server {host}:{port}")

    
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    # Main loop: read user input and send to server
    try:
        while True:
            msg = input(r"[You] ")
            if msg.lower() in ("quit", "exit"):
                break
            sock.sendall(msg.encode())
    except KeyboardInterrupt:
        print("\n[!] Client shutting down")
    finally:
        sock.close()


start_client()