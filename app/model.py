import pickle


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
    return {'clients': clients, **user.to_dict()}


def collection_to_dict(collection, func=lambda d: d.to_dict()):
    documents = collection.stream()
    return {d.id: func(d) for d in documents}


class Database(dict):
    @staticmethod
    def root():
        return Database('root', None)

    def __init__(self, id, parent):
        self.id = id
        self._parent = parent
        self._collections = set()

    def collection(self, key):
        self._collections.add(key)
        return self.setdefault(key, Database(key, self))

    def document(self, key):
        return self.setdefault(key, Database(key, self))

    def get(self, key=None):
        if not key:
            return self
        return super().get(key)

    def to_dict(self):
        return self

    def stream(self):
        return self.values()

    def where(self, key, op, value):
        new = Database(self.id, self._parent)
        new.update({k: v for k, v in self.items() if self.__test(v, key, op, value)})
        return new

    def set(self, data):
        collections = {c: self[c] for c in self._collections}
        self.clear()
        self.update(collections)
        self.update(data)

    def exists(self):
        return bool(self)

    @property
    def reference(self):
        return self

    def __test(self, document, key, op, value):
        if op != '==':
            raise NotImplementedError('Operation {} not supported'.format(op))
        return key in document and document[key] == value

    def delete(self):
        k = next(k for k, v in self._parent.items() if v == self)
        del self._parent[k]


class DataManager(object):
    def __init__(self, file_path):
        self._file = file_path

    def save(self, db):
        with open(self._file, 'wb') as file:
            pickle.dump(db, file, pickle.HIGHEST_PROTOCOL)

    def load(self):
        try:
            with open(self._file, 'rb') as file:
                return pickle.load(file)
        except (EOFError, FileNotFoundError):
            return Database.root()
