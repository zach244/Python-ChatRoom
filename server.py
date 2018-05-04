from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import json

clients = {}
addressesses = {}
usernames = []
connections_allowed = 5

host = ''
port = 1134
buffer_size = 1024
address = (host, port)
server = socket(AF_INET, SOCK_STREAM)
server.bind(address)


def accept_connections():
    while True:
        client, client_addressess = server.accept()
        addressesses[client] = client_addressess
        Thread(target=handle_client, args=(client,)).start()


def message_handler(msg, client):
    try:
        j_obj = json.loads(msg)
        message_return = {}
        print(j_obj)
        username = j_obj.get("sender")
        if len(j_obj) == 2 and j_obj.get("disconnect") is True:
            message_return["disconnect"] = True
            message_json = json.dumps(message_return)
            broadcast_disonnect = ("{} has disconnected".format(username))
            client.send(bytes(message_json, "utf8"))
            broadcast(broadcast_disonnect, client)
            client.close()
            usernames.remove(username)
            del clients[client]
        else:
            broadcast(msg, client)
    except OSError:  # disconnected client
        pass


def connection_check(username, client):
    message_return = {}
    username_jobj = json.loads(username)
    username = username_jobj.get("username")
    # handling username requets
    if len(username_jobj) == 1 and username is not None:
        if username in usernames:
            message_return["isConnect"] = False
            message_return["errorCode"] = 1
            message_json = json.dumps(message_return)
            client.send(bytes(message_json, "utf8"))
            client.close()
            del clients[client]
            usernames.remove(username)
        elif len(clients) > connections_allowed:
            message_return["isConnect"] = False
            message_return["errorCode"] = 2
            message_json = json.dumps(message_return)
            client.send(bytes(message_json, "utf8"))
            client.close()
            del clients[client]
            usernames.remove(username)
        else:
            message_return["isConnect"] = True
            message_return["errorCode"] = -1
            message_json = json.dumps(message_return)
            client.send(bytes(message_json, "utf8"))
            usernames.append(username)


def handle_client(client):  # Takes client socket as argument.
    name = client.recv(buffer_size).decode("utf8")
    connection_check(name, client)
    clients[client] = name
    while True:
        msg = client.recv(buffer_size).decode("utf8")
        message_handler(msg, client)


def broadcast(msg, client):
    # print(clients)
    for sock in clients:
        if sock is client:
            pass
        else:
            sock.send(bytes(msg, "utf8"))


if __name__ == "__main__":
    server.listen(connections_allowed)  # Listens for 5 connections at max.
    print("Waiting for connection...")
    connection_thread = Thread(target=accept_connections)
    connection_thread.start()  # Starts the infinite loop.
    connection_thread.join()
    server.close()
