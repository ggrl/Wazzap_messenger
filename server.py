import socket
import selectors

sel = selectors.DefaultSelector()
clients = {}        
usernames = {}      
login_state = {}    


USER_DB = {
    "maryam": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
    "gregor": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
    "mahmoud": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
}

def accept(sock):
    conn, addr = sock.accept()
    print(f"[+] Accepted connection from {addr}")
    conn.setblocking(False)
    clients[conn] = addr
    login_state[conn] = {"stage": "username"}  
    sel.register(conn, selectors.EVENT_READ, login)
    conn.sendall(b"Welcome! Please log in.\nUsername: ")

def login(conn):
    
    try:
        data = conn.recv(1024).decode().strip()
    except ConnectionResetError:
        close_connection(conn)
        return

    if not data:
        close_connection(conn)
        return

    state = login_state.get(conn, {})

    if state.get("stage") == "username":
        state["username_candidate"] = data
        state["stage"] = "password"
        login_state[conn] = state
        conn.sendall(b"Password: ")

    elif state.get("stage") == "password":
        username = state.get("username_candidate")
        password = data
        if username in USER_DB and USER_DB[username] == password:
            usernames[conn] = username
            sel.modify(conn, selectors.EVENT_READ, read)  
            conn.sendall(f"Login successful! Welcome, {username}.\n".encode())
            broadcast(f"*** {username} has joined the chat ***".encode(), conn)
            print(f"[+] {username} logged in from {clients[conn]}")
            del login_state[conn]  # no longer needed
        else:
            conn.sendall(b"Invalid login. Try again.\nUsername: ")
            login_state[conn] = {"stage": "username"}  # restart


def handle_command(conn, command):
    username = usernames.get(conn, "Unknown")
    if command == "/quit":
        conn.sendall(b"Goodbye!\n")
        close_connection(conn)
    elif command == "/help":
        conn.sendall(b"Available commands: /help, /users, /quit\n")
    elif command == "/users":
        all_users = list(usernames.values())
        conn.sendall(f"Users currently logged in:\n".encode())
        for user in all_users:
            conn.sendall(f"{user}\n".encode())
    else:
        conn.sendall(f"Unknown command: {command}\n".encode())

def read(conn):
    try:
        data = conn.recv(1024)
    except ConnectionResetError:
        close_connection(conn)
        return

    if data:
        username = usernames.get(conn, "Unknown")
        msg_text = data.decode().strip()
        if msg_text.startswith("/"):
            handle_command(conn, msg_text)
        else:
            msg = f"[{username}] {data.decode().strip()}"
            print(msg)
            broadcast(msg.encode(), conn)
    else:
        close_connection(conn)

def broadcast(message, sender=None):
    for conn in list(usernames.keys()):
        if conn != sender:
            try:
                conn.sendall(message + b"\n")
            except Exception as e:
                print(f"[!] Error sending to {clients.get(conn)}: {e}")
                close_connection(conn)

def close_connection(conn):
    addr = clients.get(conn)
    username = usernames.pop(conn, None)
    login_state.pop(conn, None)
    if username:
        broadcast(f"*** {username} has left the chat ***".encode(), conn)
    if conn in clients:
        del clients[conn]
    try:
        sel.unregister(conn)
    except Exception:
        pass
    conn.close()
    print(f"[-] Connection closed {addr} ({username})")

def start_server(host="127.0.0.1", port=5000):
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


start_server("127.0.0.1", 42000)