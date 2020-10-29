# JOIN, PLAY, PAUSE, FORWARD

import socket
import json
import time
import configparser
import _thread

server_socket = None
client_configs = configparser.SafeConfigParser()
client_configs.read('configs.ini')
HOST = client_configs['GeneralSettings']['Host']
PORT = int(client_configs['GeneralSettings']['Port'])

message_queue = []
users = []

def connect_server():
    global server_socket, HOST, PORT

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((HOST, PORT))
        return True
    except Exception as e:
        print("EXCEPTION IN CONNECT SERVER: " + str(e))
        return False

def create_room(username):
    global server_socket

    data = {'action_id':0, 'username':username}
    try:
        server_socket.send(bytes(json.dumps(data), encoding='utf8'))
        return True
    except Exception as e:
        print("EXCEPTION IN CREATE ROOM: " + str(e))
        return False

def join_room(username, room_id):
    global server_socket

    data = {'action_id':1, 'username':username, 'room_id':room_id}

    try:
        server_socket.send(bytes(json.dumps(data), encoding='utf8'))
        return True
    except Exception as e:
        print("EXCEPTION IN JOIN ROOM: " +str(e))
        return False

def disconnect_server():
    global server_socket

    try:
        message_queue = []
        server_socket.close()
        return False
    except Exception as e:
        print("EXCEPTION IN DISCONNECT SERVER: " + str(e))
        return True

def get_users_in_room():
    return users

def receive_messages():
    while True:
        message_queue.append(str(server_socket.recv(1024).decode("utf-8")))
        # TODO: check what the message is 
_thread.start_new_thread(receive_messages, ())