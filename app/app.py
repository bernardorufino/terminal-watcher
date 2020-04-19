from itertools import chain

import firebase_admin
from firebase_admin import firestore, messaging
from flask import Flask, jsonify, request

from app.ext import count
from app.model import User, Command, collection_to_dict, user_to_dict

app = Flask(__name__)
firebase_admin = firebase_admin.initialize_app()
db = firestore.client()


@app.route('/user/<user_id>/commands')
def get_commands(user_id):
    token = request.args['token']

    clients = db.collection(User.C).document(user_id).collection(User.Client.C)
    client = clients.document(token).get()
    if not client.exists:
        return jsonify({'error': 'Not authorized'}), 401

    commands = db.collection(Command.C).where(Command.USER_ID, '==', user_id)
    commands = collection_to_dict(commands)
    return jsonify(commands)


@app.route('/user/<user_id>/command/<command_id>/open', methods=['POST'])
def open_command(user_id, command_id):
    data = request.json

    command_id = 'u{}{}'.format(user_id, command_id)
    command_ref = db.collection(Command.C).document(command_id)
    command_data = {
        Command.ID: command_id,
        Command.USER_ID: user_id,
        Command.STRING: data['string'],
        Command.START_TIME: data['start_time'],
        Command.HOST: data['host'],
        Command.WORKING_DIRECTORY: data['working_directory'],
        Command.SESSION_PID: data['session_pid'],
    }
    command_ref.set(command_data)

    return jsonify(1)


def push_message(clients):
    tokens = [c.get('token') for c in clients]
    message = messaging.MulticastMessage(data={'action': 'update'}, tokens=tokens)
    # response = messaging.send_multicast(message)
    # print('{} messages were sent successfully'.format(response.success_count))


@app.route('/user/<user_id>/command/<command_id>/close', methods=['POST'])
def close_command(user_id, command_id):
    data = request.json

    command_id = 'u{}{}'.format(user_id, command_id)
    command_ref = db.collection(Command.C).document(command_id)
    command_data = {
        **command_ref.get().to_dict(),
        Command.END_TIME: data['end_time'],
        Command.STATUS_CODE: data['status_code'],
    }
    command_ref.set(command_data)

    user = db.collection(User.C).document(user_id)
    clients = user.collection(User.Client.C).stream()
    push_message(clients)

    return jsonify(1)


@app.route('/user/<user_id>/register', methods=['POST'])
def register_client(user_id):
    data = request.json

    user_ref = db.collection(User.C).document(user_id)
    user = user_ref.get()
    user_data = user.to_dict() if user.exists else {User.ID: user_id}
    user_ref.set(user_data)

    clients = user_ref.collection(User.Client.C)
    token = str(count(clients.stream()))
    client_data = {
        User.Client.TOKEN: token,
        User.Client.TOKEN_FCM: data['token_fcm'],
    }
    clients.document(token).set(client_data)

    return jsonify(1)


@app.route('/debug')
def debug():
    users = collection_to_dict(db.collection(User.C), user_to_dict)
    commands = collection_to_dict(db.collection(Command.C))
    return jsonify({
        'users':  users,
        'commands': commands
    })


@app.route('/reset', methods=['POST'])
def reset():
    users = db.collection(User.C)
    clients = [c for u in users.stream() for c in u.reference.collection(User.Client.C).stream()]
    commands = db.collection(Command.C).stream()
    for document in chain(clients, users.stream(), commands):
        document.reference.delete()
    return jsonify(1)

