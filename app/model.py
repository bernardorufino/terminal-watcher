from pprint import pprint

from google.cloud.firestore_v1 import DocumentSnapshot


class User:
    C = 'users'
    ID = 'id'

    class Client:
        C = 'clients'
        TOKEN = 'token'
        TOKEN_FCM = 'token_fcm'


class Command:
    C = 'commands'
    ID = 'id'
    USER_ID = 'user_id'
    STRING = 'string'
    START_TIME = 'start_time'
    END_TIME = 'end_time'
    STATUS_CODE = 'status_code'
    WORKING_DIRECTORY = 'working_directory'
    SESSION_PID = 'session_pid'
    HOST = 'host'


def user_to_dict(user):
    clients = user.reference.collection(User.Client.C)
    clients = collection_to_dict(clients)
    pprint(user)
    return {'clients': clients, **user.to_dict()}


def collection_to_dict(collection, func=DocumentSnapshot.to_dict):
    documents = collection.stream()
    return {d.id: func(d) for d in documents}

