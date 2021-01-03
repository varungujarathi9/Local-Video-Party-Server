from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
import string
import random
import datetime
import pytz

#exception handling for each function 

#instantiate
app = Flask(__name__)
app.config['SECRET_KEY'] = 'videoparty100'

#wrapping flask instance with the socketio wrapper
socketIo = SocketIO(app,cors_allowed_origins="*")

timezone = pytz.timezone('Asia/Kolkata')

rooms_details = {}
messages = {}

def get_room_id(length):
    letters_and_digits = string.ascii_uppercase + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

@socketIo.on('connect')
def connection_event():
    print("socket is connected")

@socketIo.on('disconnect')
def disconnection_event():
    print("server is disconnected")

@socketIo.on('create-room')
def create_room(data):
    global rooms_details
    room_id = get_room_id(6)
    while(room_id in rooms_details.keys()):
        room_id = get_room_id(6)
    rooms_details[room_id] = {'members':{data['username']:True},'created_at':datetime.datetime.now(tz=timezone).strftime('%x @ %X'), 'started':False}
    messages[room_id] = []
    print(rooms_details)
    join_room(room_id)
    emit('room-created', {'room-id':room_id, 'room-details':rooms_details[room_id]})

@socketIo.on('rejoin-creator')
def rejoin_creator(data):
    global rooms_details
    print("48",rooms_details)
    room_id= data['id']
    print(data)
    rooms_details[room_id] = {'members':{data['creator_name']:True},'created_at':datetime.datetime.now(tz=timezone).strftime('%x @ %X'), 'started':False, 'video_name': None, 'paused':True, 'playing_at':0, 'total_duration': 0}
    messages[room_id] = []
    join_room(room_id)
    emit('room-created', {'room-id':room_id, 'room-details':rooms_details[room_id]})

@socketIo.on('join-room')
def joinroom(data):
    global rooms_details
    if(data['roomID'] in rooms_details.keys()):
        rooms_details[data['roomID']]['members'][data['username']] = False
        print(rooms_details)
        join_room(data['roomID'])
        emit('room-joined', {'room-id':data['roomID'], 'room-details':rooms_details[data['roomID']]})
        emit('update-room-details', rooms_details[data['roomID']], broadcast=True, include_self=False,room=data['roomID'])
    else:
        #print('\n room not found \n')
        emit('login-error',{'msg':'Invalid Room I.D. !! Please check again'})



@socketIo.on('rejoin-joinee')
def rejoin_creator(data):
    global rooms_details
    print("70",rooms_details)
    room_id= data['id']
    print(data)
    rooms_details[data['id']]['members'][data['joinee_name']] = False
    print(rooms_details)
    join_room(data['id'])
    emit('room-joined', {'room-id':data['id'], 'room-details':rooms_details[data['roomID']]})
    emit('update-room-details', rooms_details[data['roomID']], broadcast=True, include_self=False,room=data['roomID'])

@socketIo.on('update-member-status')
def update_member_status(data):
    global rooms_details
    rooms_details[data['roomID']]['members'][data['username']] = data['ready']
    emit('update-room-details',rooms_details[data['roomID']],broadcast=True, include_self=True, room=data['roomID'])

@socketIo.on('start-video')
def start_video(data):
    rooms_details[data['room_id']]['started'] = True
    emit('video-started',rooms_details[data['room_id']],broadcast=True, include_self=True, room=data['room_id'])

@socketIo.on('video-update')
def video_update(data):
    if(data['pauseDetails']['exited'] == True):
        rooms_details[data['pauseDetails']['roomID']]['started'] = False
    emit('updated-video',data, broadcast=True, include_self=False,room=data['pauseDetails']['roomID'] )

@socketIo.on('remove-member')
def remove_member(data):
    global rooms_details
    rooms_details[data['roomID']]['members'].pop(data['username'])
    leave_room(data['roomID'])
    emit('left_room',rooms_details[data['roomID']])
    emit('update-room-details', rooms_details[data['roomID']], broadcast=True, include_self=False,room=data['roomID'])


@socketIo.on('remove-all-member')
def remove_all_members(data):
    global rooms_details
    rooms_details[data['roomID']]['members'] = {}
    rooms_details[data['roomID']]['started'] = False
    emit('all_left',rooms_details[data['roomID']],broadcast=True, include_self=True, room=data['roomID'])
    leave_room(data['roomID'])

@socketIo.on('send-message')
def send_message(data):
    global messages
    data["timestamp"] = datetime.datetime.now(tz=timezone).strftime('%x @ %X')
    data["messageNumber"] = len(messages[data["roomID"]]) + 1
    messages[data["roomID"]].append(data)
    # TODO: delete messages if room is deleted
    emit('receive_message', messages[data["roomID"]], broadcast=True, include_self=True, room=data["roomID"])

@socketIo.on('get-all-messages')
def send_message(data):
    global messages
    emit('receive_message', messages[data["roomID"]], broadcast=False, include_self=True, room=data["roomID"])

# webrtc socket operation
@socketIo.on('send-offer')
def send_offer(data):
    emit('receive-offer', data, broadcast=True, include_self=False, room=data['roomID'])

@socketIo.on('send-answer')
def send_answer(data):
    emit('receive-answer', data, broadcast=True, include_self=False, room=data['roomID'])

if __name__ == '__main__':
    #automatic reloads again when made some changes
    app.debug=True
    # use this while running in gcsp server
    socketIo.run(app, host='0.0.0.0', port=5000)
# from flask import Flask
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello World!'

# if __name__ == '__main__':
#     app.run()