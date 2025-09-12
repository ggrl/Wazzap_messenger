import socket
import threading
import getpass
import hashlib

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

def prestart():
    print("How do you want to connect? Choose '1' for local or '2' for remote.")
    choice = input("Enter (1/2): ")
    if choice == '1':
        start_client(host="127.0.0.1", port=42000)
    elif choice == '2':
        print("Enter pinggy link in this format: 'tcp://bcbxs-92-210-207-199.a.free.pinggy.link:34165'")
        link = input("Enter link: ")
        try:
            if link.startswith("tcp:"):
                link = link.replace('tcp://', '')
            host, port = link.split(':')
            port = int(port)
            start_client(host, port)
        except:
            print("Invalid Link!")
            prestart()    
    else:
        print("Error! Invalid choice!")
        prestart()

def start_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[*] Connected to chat server {host}:{port}")
 
    try:
        while True: 
            
            username = input("Enter username: ")
            sock.sendall((username + "\n").encode())
            prompt = sock.recv(1024).decode()
            #print(prompt, end="")

            password  = getpass.getpass("Enter password: ")
            encoded_pw = password.encode()
            hashed_pw = hashlib.sha256(encoded_pw)
            pw_hash = hashed_pw.hexdigest()
            sock.sendall((pw_hash + "\n").encode())
            response = sock.recv(1024).decode().strip()
            print(response)

            if "successful" in response.lower():
                break  
            else:
                print("[!] Login failed, try again...\n")
        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
        while True:
            msg = input()
            sock.sendall((msg + "\n").encode())
    except KeyboardInterrupt:
        print("\n[!] Client shutting down")
        try:
            sock.sendall(("/quit\n").encode())
        except:
            pass
        
    finally:
        sock.close()


prestart()