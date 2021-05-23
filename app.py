import bcrypt
from datetime import date
from flask import Flask, request, session, jsonify
from helper import (LOGIN_ERROR, LOGIN_OK, MESSAGE_CREATED, MESSAGE_DELETED,
                    MESSAGES_NOT_FOUND, NOT_LOGGED_IN, OK, SIGN_UP_OK, db_connection)


app = Flask(__name__)
app.secret_key = 'secretkey!'


@app.route('/')
def welcome_user():
    return 'Welcome to our Messaging System!', OK


@app.route('/messages', methods=['GET'])
@app.route('/messages/outbox', methods=['GET'])
@app.route("/messages/unread", methods=['GET'])
def get_messages():
    if not 'user_id' in session:
        return NOT_LOGGED_IN

    user_id = session['user_id']
    conn = db_connection()
    cursor = conn.cursor()
    mailbox = 'outbox' if request.url.endswith('outbox') else 'inbox'
    cursor.execute(f"SELECT message_id FROM {mailbox} WHERE user_id='{user_id}'")
    mailbox_ids = tuple(one_res['message_id'] for one_res in cursor.fetchall())
    if len(mailbox_ids) == 1:
        mailbox_ids = f'({mailbox_ids[0]})'

    if not mailbox_ids:
        return MESSAGES_NOT_FOUND

    if request.url.endswith('unread'):
        cursor.execute(f"SELECT * FROM messages WHERE id in {mailbox_ids} AND viewed=0")
    else:
        cursor.execute(f"SELECT * FROM messages WHERE id in {mailbox_ids}")
    messages = [
        dict(id=row['id'], sender=row['sender'], receiver=row['receiver'], message=row['message'],
                subject=row['subject'], creation_date=row['creation_date'])
        for row in cursor.fetchall()
    ]
    if not messages:
        return MESSAGES_NOT_FOUND

    return jsonify(messages), OK


@app.route("/message", methods=['POST'])
def write_message():
    conn = db_connection()
    cursor = conn.cursor()

    sender = request.form['sender']
    receiver = request.form['receiver']
    message = request.form['message']
    subject = request.form['subject']
    creation_date = date.today().strftime('%d/%m/%Y')

    cursor.execute(f"SELECT id from users WHERE username='{sender}'")
    sender_id = cursor.fetchone()['id']
    receiver_id = cursor.execute(f"SELECT id from users WHERE username='{receiver}'")
    receiver_id = cursor.fetchone()['id']
    sql = """INSERT INTO messages (sender, receiver, message, subject, creation_date, viewed)
                            VALUES(%s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (sender, receiver, message, subject, creation_date, 0))
    message_id = cursor.lastrowid

    sql2 = """INSERT INTO inbox (user_id, message_id)
                            VALUES(%s, %s)"""
    cursor.execute(sql2, (receiver_id, message_id))
    sql3 = """INSERT INTO outbox (user_id, message_id)
                            VALUES(%s, %s)"""
    cursor.execute(sql3, (sender_id, message_id))
    conn.commit()

    return MESSAGE_CREATED


@app.route('/message/<int:message_id>', methods=['PUT', 'DELETE'])
def handle_message(message_id):
    if not 'user_id' in session:
        return NOT_LOGGED_IN

    user_id = session['user_id']
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM messages WHERE id='{message_id}'")
    messages = [
        dict(id=row['id'], sender=row['sender'], receiver=row['receiver'], message=row['message'],
            subject=row['subject'], creation_date=row['creation_date'], viewed=row['viewed'])
        for row in cursor.fetchall()
    ]
    if not messages:
        return MESSAGES_NOT_FOUND
    message = messages[0]
    cursor.execute(f"SELECT id FROM users WHERE username='{message['sender']}'")
    sender_id = cursor.fetchone()['id']
    cursor.execute(f"SELECT id FROM users WHERE username='{message['receiver']}'")
    receiver_id = cursor.fetchone()['id']
    
    if request.method == "PUT":
        cursor.execute(f"SELECT id FROM users WHERE username='{message['receiver']}'")
        if user_id != receiver_id and user_id != sender_id:
            return MESSAGES_NOT_FOUND

        if user_id == receiver_id and message['viewed'] == 0:
            cursor.execute(f"UPDATE messages SET viewed=1 WHERE id='{message_id}'")
            conn.commit()
        
        del message['viewed']
        return jsonify(message), OK
    
    else:
        deleted = False
        if user_id == sender_id:
            res = cursor.execute(f"DELETE FROM outbox WHERE message_id='{message_id}'")
            if res:
                deleted = True
    
            exist = cursor.execute(f"SELECT * FROM inbox WHERE user_id='{receiver_id}' AND message_id='{message_id}'")
            if not exist:
                cursor.execute(f"DELETE FROM messages WHERE id='{message_id}'")
        elif user_id == receiver_id:
            res = cursor.execute(f"DELETE FROM inbox WHERE message_id='{message_id}'")
            if res:
                deleted = True
            exist = cursor.execute(f"SELECT * FROM outbox WHERE user_id='{sender_id}' AND message_id='{message_id}'")
            if not exist:
                cursor.execute(f"DELETE FROM messages WHERE id='{message_id}'")
        else:
            return MESSAGES_NOT_FOUND

        conn.commit()
        if deleted:
            return MESSAGE_DELETED
        
        return MESSAGES_NOT_FOUND


@app.route('/sign_up', methods=['POST'])
def sign_up():
    conn = db_connection()
    cursor = conn.cursor()
    salt = bcrypt.gensalt(prefix=b'2b', rounds=10)
    unhashed_password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(unhashed_password, salt)
    username = request.form['username']
    email = request.form['email']
    sql = """INSERT INTO users (username, email, password)
                            VALUES(%s, %s, %s)"""
    cursor.execute(sql, (username, email, hashed_password))
    conn.commit()
    cursor.execute(f"SELECT id from users WHERE username='{username}'")
    session['user_id'] = cursor.fetchone()['id']
    return SIGN_UP_OK



@app.route('/login', methods=['POST'])
def login():
    conn = db_connection()
    cursor = conn.cursor()
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    cursor.execute(f"SELECT id, password from users WHERE username='{username}'")
    user = cursor.fetchone()
    print(user)
    if not user:
        return LOGIN_ERROR
    actual_password = user['password'].encode('utf-8')
    print(actual_password)
    if not bcrypt.checkpw(password, actual_password):
        return LOGIN_ERROR
    
    session['user_id'] = user['id']
    return LOGIN_OK


if __name__ == '__main__':
    app.run(threaded=True, port=5000)