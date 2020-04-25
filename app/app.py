import os
from itertools import chain

import firebase_admin
from firebase_admin import messaging
from flask import Flask, jsonify, request

from app.ext import count
from app.model import User, Command, collection_to_dict, user_to_dict, DataManager, Database

app = Flask(__name__)
firebase_admin = firebase_admin.initialize_app()
manager = DataManager('database.db')


@app.route('/user/<user_id>/commands')
def get_commands(user_id):
    db = manager.load()
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
    db = manager.load()
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

    manager.save(db)
    return jsonify(True)


def push_message(clients):
    tokens = [c.get('token') for c in clients]
    message = messaging.MulticastMessage(data={'action': 'update'}, tokens=tokens)
    response = messaging.send_multicast(message)
    print('{} messages were sent successfully'.format(response.success_count))


@app.route('/user/<user_id>/command/<command_id>/close', methods=['POST'])
def close_command(user_id, command_id):
    db = manager.load()
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

    manager.save(db)
    return jsonify(True)


@app.route('/user/<user_id>/register', methods=['POST'])
def register_client(user_id):
    db = manager.load()
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

    manager.save(db)
    return jsonify(token)


@app.route('/debug/cred')
def debug_cred():
    path = "keys/terminal-watcher-firebase-adminsdk-303ol-36674b1a6e.json"
    cred = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
    cred = ('exists' if os.path.isfile(cred) else 'NOT') if cred else 'NO ENV'
    same_dir = 'exists' if os.path.isfile(path) else 'NOT'
    parent_dir = 'exists' if os.path.isfile('../' + path) else 'NOT'
    return jsonify({
        'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None),
        'wd': os.getcwd(),
        path: same_dir,
        '../{}'.format(path): parent_dir,
        'GOOGLE_APPLICATION_CREDENTIALS file': cred,
        'ls .': os.listdir('.'),
        'ls wd': os.listdir(os.getcwd()),
    })


@app.route('/debug')
def debug():
    db = manager.load()
    users = collection_to_dict(db.collection(User.C), user_to_dict)
    commands = collection_to_dict(db.collection(Command.C))
    return jsonify({
        'users':  users,
        'commands': commands
    })


@app.route('/reset', methods=['POST'])
def reset():
    db = manager.load()
    users = db.collection(User.C)
    clients = [c for u in users.stream() for c in u.reference.collection(User.Client.C).stream()]
    commands = db.collection(Command.C).stream()
    for document in chain(clients, users.stream(), commands):
        document.reference.delete()
    return jsonify(True)


@app.route('/local/reset', methods=['POST'])
def local_reset():
    db = Database.root()
    manager.save(db)
    return jsonify(True)


@app.route('/local/debug')
def local_debug():
    db = manager.load()
    return jsonify(db)
