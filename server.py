import socket
import selectors

sel = selectors.DefaultSelector()
clients = {}  # Keep track of active connections

def accept(sock):
    conn, addr = sock.accept()
    print(f"[+] Accepted connection from {addr}")
    conn.setblocking(False)
    clients[conn] = addr
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn):
    data = conn.recv(1024)
    if data:
        msg = f"[{clients[conn][0]}:{clients[conn][1]}] {data.decode().strip()}"
        print(msg)
        broadcast(msg.encode(), conn)
    else:
        print(f"[-] Closing connection {clients[conn]}")
        sel.unregister(conn)
        conn.close()
        del clients[conn]

def broadcast(message, sender=None):
    for conn in clients:
        if conn != sender:  # Don’t echo back to sender
            try:
                conn.sendall(message)
            except Exception as e:
                print(f"[!] Error sending to {clients[conn]}: {e}")

def start_server(host="127.0.0.1", port=42000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    server.setblocking(False)
    sel.register(server, selectors.EVENT_READ, accept)

    print(f"[*] Chat server running on {host}:{port}")
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj)


start_server()