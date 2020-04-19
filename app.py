import os

import firebase_admin
from flask import Flask, jsonify, request
from firebase_admin import firestore

app = Flask(__name__)
firebase_admin = firebase_admin.initialize_app()
db = firestore.client()


@app.route('/')
def hello_world():
    return "Firesds_xapp = {}\n".format(firebase_admin.project_id)


@app.route('/debug')
def debug():
    users = db.collection('users')
    doc_ref = users.document('alovelace')
    doc_ref.set({
        'first': 'Ada',
        'last': 'Lovelace',
        'born': 1815
    })
    s = users.stream()
    for doc in s:
        print('{} => {}'.format(doc.id, doc.to_dict()))
    return str(len(list(s)))


@app.route('/users')
def get_users():
    users = db.collection('users')
    docs = users.stream()

    ans = []
    for doc in docs:
        ans.append(doc.id)

    return jsonify(ans)


@app.route('/user', methods=['GET', 'POST'])
def create_user():
    data = request.json
    users = db.collection('users')
    document = users.document(data['id'])
    document.set(data)
    return jsonify(1)