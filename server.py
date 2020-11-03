# 0 - create room
# 1 - join room
# 2 - play
# 3 - pause
# 4 - play at

# libraries
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gethostbyaddr
import _thread
import time
import datetime
import json
import configparser
from server_utility import get_room_id, send_to_all_clients
# import ServerConfigs

# variables
ServerConfigs = configparser.SafeConfigParser()
ServerConfigs.read('configs.ini')
HOST = ServerConfigs['GeneralSettings']['Host']
PORT = int(ServerConfigs['GeneralSettings']['Port'])
addr = (HOST, PORT)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(addr)
print("socket binded to required address")
serverSocket.listen(10)
client_sockets = []
room_details = {}
room_sockets = {}

def handler():
    global client_sockets
    while True:
        # iterate through all clients
        for client_socket in client_sockets:
            try:
                room_id = None
                sendDataFlag = False
                data = json.loads(client_socket.recv(1024))
                if data['action_id'] == 0:
                    # check if the client_socket is already present some other room
                    if len(room_details.values()) > 0 and client_socket.getpeername() in [list(y.values()) for y in [x['members'] for x in room_details.values()]][0]:
                        client_socket.send(bytes(json.dumps({'error':"Sorry! Cannot create room, please logout from previous room"}), encoding='utf8'))
                        print("CREATE ROOM VALIDATED",json.dumps({'error':"Sorry! Cannot create room, please logout from previous room"}))
                        # TODO: remove the user from previous room and join in new room
                    else:
                        # create room
                        room_id = get_room_id(6)
                        room_details[room_id] = {'members':{data['username']:client_socket.getpeername()},'video_name': None, 'paused':True, 'playing_at':0, 'total_duration': 0}
                        room_sockets[room_id] = {data['username']:client_socket}
                        
                        client_socket.send(bytes(json.dumps({'created':room_id, 'room':room_details[room_id]}), encoding='utf8'))
                        print("CREATE ROOM",json.dumps({'created':room_id, 'room':room_details[room_id]}))

                elif data['action_id'] == 1:
                    # join a room
                    if data['room_id'] not in room_details:
                        client_socket.send(bytes(json.dumps({'error':"Sorry! Room doesn't exist"}), encoding='utf8'))

                    elif data['username'] in room_sockets[room_id].keys() :
                        client_socket.send(bytes(json.dumps({'error':"User with this "+data['username']+" already exists"}), encoding='utf8'))

                    else:
                        if len(room_details.values()) > 0 and client_socket.getpeername() in [list(y.values()) for y in [x['members'] for x in room_details.values()]][0]:
                            client_socket.send(bytes(json.dumps({'error':"Sorry! Cannot create room, please logout from previous room"}), encoding='utf8'))
                            print("JOIN ROOM VALIDATED",json.dumps({'error':"Sorry! Cannot create room, please logout from previous room"}))
                            # TODO: remove the user from previous room and join in new room
                        else:
                            room_id = data['room_id']
                            room_details[room_id]['members'].append(data['username'])
                            room_sockets[room_id][data['username']] = client_socket

                            sendDataFlag = True
                            print("JOIN ROOM",json.dumps({'join':room_id, 'room':room_details[room_id]}))

                elif data['action_id'] == 2:
                    # play video
                    if data['room_id'] in room_details:
                        room_id = data['room_id']
                        room_details[room_id]['paused'] = False

                        sendDataFlag = True
                    else:
                        client_socket.send(bytes(json.dumps({'error':"Sorry! Room doesn't exist"}), encoding='utf8'))

                elif data['action_id'] == 3:
                    # pause video
                    if data['room_id'] in room_details:
                        room_id = data['room_id']
                        room_details[room_id]['paused'] = True
                        # client_socket.send(bytes(json.dumps({room_id:room_details[room_id]}), encoding='utf8'))
                        sendDataFlag = True
                    else:
                        client_socket.send(bytes(json.dumps({'error':"Sorry! Room doesn't exist"}), encoding='utf8'))

                if(sendDataFlag):

                    send_to_all_clients(room_sockets[room_id].values(), json.dumps({'join':room_id, 'room':room_details[room_id]}))
                    sendDataFlag = False

            except BlockingIOError:
                pass
            except KeyboardInterrupt:
                # for client_socket in client_sockets:
                #     client_socket.close()
                client_sockets.clear()
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except json.decoder.JSONDecodeError:
                # client_socket.close()
                client_sockets.remove(client_socket)

            except (ConnectionResetError, OSError):
                # client_socket.close()
                client_sockets.remove(client_socket)

# start handler thread which syncs all clients

_thread.start_new_thread(handler, ())
while True:
    try:
        # accpet new client and add client's socket to list
        client_socket, client_addr = serverSocket.accept()
        print("Got new client",client_socket)
        if client_socket not in client_sockets:
            client_sockets.append(client_socket)
            client_socket.setblocking(0)
    except KeyboardInterrupt:
        print("Closing server socket...")
        serverSocket.close()
        # for client_socket in client_sockets:
        #     client_socket.close()
        client_sockets.clear()
        break
    except OSError:
        client_sockets.remove(client_socket)