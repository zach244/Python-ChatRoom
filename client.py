from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import json
import datetime
import time
import tkinter
from tkinter.simpledialog import askstring


top = tkinter.Tk()
top.title("ChatRoomAsylum")
host = askstring("Host", "Enter Host")
username = askstring("username  ", "Enter Username")
port = 1134  # Default value.
buffer_size = 1024
address = (host, port)
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(address)


def username_request(username):
    username_request = {}
    username_request["username"] = username
    username_json = json.dumps(username_request)
    client_socket.send(bytes(username_json, "utf8"))


def date_time():
    current_time = datetime.datetime.now(datetime.timezone.utc)
    current_time = str(current_time)
    return current_time


def message_handler(msg):
    try:
        j_obj = json.loads(msg)
        if len(j_obj) == 2 and 'errorCode' in j_obj:
            if j_obj.get('errorCode') is 1:
                msg_list.insert(tkinter.END, "username is taken")

                exit(0)
            elif j_obj.get('errorCode') is 2:
                msg_list.insert(tkinter.END, "chatroom is full")

                exit(0)
            elif j_obj.get('errorCode') is -1:
                msg_list.insert(tkinter.END, "connection successful")
        else:
            username = j_obj.get("sender")
            message = j_obj.get("message")
            formatted_message = "{}: {}".format(username, message)
            msg_list.insert(tkinter.END, formatted_message)
    except ValueError:
        msg_list.insert(tkinter.END, msg)


def receive():
    # infinitely looping to recieve messaages
    while True:
        try:
            msg = client_socket.recv(buffer_size).decode("utf8")
            message_handler(msg)
        except OSError:
            break


def send(message):
    message_object = {}
    msg = message
    print(msg)
    if len(msg) > 140:
        error_message = "ERROR: MESSAGE TOO LONG"
        msg_list.insert(tkinter.END, error_message)
    else:
        if msg == "\disconnect":
            message_object["sender"] = username
            message_object["disconnect"] = True
            message_json = json.dumps(message_object)
            client_socket.send(bytes(message_json, "utf8"))
            client_socket.close()
            top.quit()
            exit(0)
        else:
            message_object["dm"] = None
            message_object["sender"] = username
            message_object["message"] = msg
            message_object["length"] = len(msg)
            message_object["date"] = date_time()
            message_json = json.dumps(message_object)
            formatted_message = "{}: {}".format("me", msg)
            msg_list.insert(tkinter.END, formatted_message)
            client_socket.send(bytes(message_json, "utf8"))


def chatting(event=None):
    try:
        message = my_msg.get()
        my_msg.set("")
        send(message)

    except Exception as e:
        print(e)


def clear_entry(event):
    entry_field.delete(0, 'end')


def tkinter_gui(top):
    global my_msg
    global entry_field
    global msg_list
    messages_frame = tkinter.Frame(
        top, width=768, height=576, bg="pale turquoise", colormap="new")
    messages_frame.pack()
    my_msg = tkinter.StringVar()  # For the messages to be sent.
    my_msg.set("Type your messages here.")
    # To navigate through past messages.
    scrollbar = tkinter.Scrollbar(messages_frame, bg="pale turquoise")
    # Following will contain the messages.
    msg_list = tkinter.Listbox(messages_frame, height=15,
                               width=50, yscrollcommand=scrollbar.set, bg="pale turquoise")
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()
    entry_field = tkinter.Entry(top, textvariable=my_msg, bg="pale turquoise")
    entry_field.bind("<Button-1>", clear_entry)
    entry_field.bind("<Return>", chatting)
    entry_field.pack()
    send_button = tkinter.Button(
        top, text="Send", command=chatting, bg="pale turquoise")
    send_button.pack()


if __name__ == "__main__":
    tkinter_gui(top)
    username_request(username)
    # tkinter_gui()
    receive_thread = Thread(target=receive)
    # chatting_thread = Thread(target=chatting)
    receive_thread.start()
    # chatting_thread.start()
    tkinter.mainloop()
