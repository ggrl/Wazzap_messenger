import socket
import selectors
from datetime import datetime 

sel = selectors.DefaultSelector()
clients = {}
usernames = {}
login_state = {}
buffers = {} 

USER_DB = {}

def fill_DB():
    USER_DB.clear()
    with open('users.dat', 'r') as f:
        for line in f:
            if not line.strip():
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            USER_DB[key.strip()] = value.strip()    

def recv_line(conn): #Full line reading
    try:
        chunk = conn.recv(1024).decode()
    except ConnectionResetError:
        return None
    if not chunk: 
        return None

    buffers[conn] = buffers.get(conn, "") + chunk
    if "\n" in buffers[conn]:
        line, rest = buffers[conn].split("\n", 1)
        buffers[conn] = rest
        return line.strip()
    return None


def accept(sock):
    conn, addr = sock.accept()
    print(f"[+] Accepted connection from {addr}")
    conn.setblocking(False)
    clients[conn] = addr
    login_state[conn] = {"stage": "username"}
    buffers[conn] = ""  # initialize buffer
    sel.register(conn, selectors.EVENT_READ, login)


def login(conn):
    data = recv_line(conn)
    if data is None:
        return  # no full line yet

    state = login_state.get(conn, {})

    if state.get("stage") == "username":
        state["username_candidate"] = data
        state["stage"] = "password"
        login_state[conn] = state
        conn.sendall(b"[*]")

    elif state.get("stage") == "password":
        username = state.get("username_candidate")
        pw_hash = data  

        if username in USER_DB and USER_DB[username] == pw_hash:
            usernames[conn] = username
            sel.modify(conn, selectors.EVENT_READ, read)  # switch to chat
            conn.sendall(f"Login successful! Welcome, {username}.\n".encode())
            broadcast(f"*** {username} has joined the chat ***".encode(), conn)
            print(f"[+] {username} logged in from {clients[conn]}")
            del login_state[conn]
        elif username not in USER_DB:
            usernames[conn] = username
            with open('users.dat', "a") as f:
                        f.write(f"{username}:{pw_hash}\n")
            fill_DB()
            sel.modify(conn, selectors.EVENT_READ, read)  
            conn.sendall(f"User created successfully! Welcome, {username}.\n".encode())
            broadcast(f"*** {username} has joined the chat ***".encode(), conn)
            print(f"[+] {username} logged in from {clients[conn]}")
        
        else:
            conn.sendall(b"Username and password does not match.\n")
            login_state[conn] = {"stage": "username"}


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
    data = recv_line(conn)
    if data is None:
        return  

    username = usernames.get(conn, "Unknown")

    if data.startswith("/"):
        handle_command(conn, data)
    else:
        msg = f"[{datetime.now().strftime("%H:%M:%S")}][{username}] {data}"
        print(msg)
        broadcast(msg.encode(), conn)


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
    buffers.pop(conn, None)
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
    fill_DB()
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