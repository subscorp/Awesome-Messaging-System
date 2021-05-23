import bcrypt
from datetime import date
from flask import Flask, request, session, jsonify
from helper import (LOGIN_ERROR, LOGIN_OK, MESSAGE_CREATED, MESSAGE_DELETED,
                    MESSAGES_NOT_FOUND, NOT_LOGGED_IN, OK, SIGN_UP_OK,
                     WELCOME_MESSAGE, db_connection, delete_message, get_form_params_post,
                      get_mailbox_ids, get_messages_from_db, get_user_id, 
                      insert_into_mailbox, insert_into_messages)


app = Flask(__name__)
app.secret_key = 'secretkey!'


@app.route('/')
def welcome_user():
    return WELCOME_MESSAGE


@app.route('/messages', methods=['GET'])
@app.route('/messages/outbox', methods=['GET'])
@app.route("/messages/unread", methods=['GET'])
def get_messages():
    """Returns messages of the current logged in user. 
    Supports all messages, unread messages and messages sent by the user."""
    if not 'user_id' in session:
        return NOT_LOGGED_IN

    conn = db_connection()
    cursor = conn.cursor()
    user_id = session['user_id']
    mailbox = 'outbox' if request.url.endswith('outbox') else 'inbox'
    mailbox_ids = get_mailbox_ids(user_id, cursor, mailbox)
    if not mailbox_ids:
        return MESSAGES_NOT_FOUND

    if request.url.endswith('unread'):
        messages = get_messages_from_db(mailbox_ids, cursor, True)
    else:
        messages = get_messages_from_db(mailbox_ids, cursor)
    if not messages:
        return MESSAGES_NOT_FOUND

    return jsonify(messages), OK


@app.route("/message", methods=['POST'])
def write_message():
    """Sends a message to another user.
    Updates the sender's outbox as well as the receiver's inbox"""
    conn = db_connection()
    cursor = conn.cursor()
    sender, receiver, message, subject = get_form_params_post(request)
    creation_date = date.today().strftime('%d/%m/%Y')
    sender_id = get_user_id(sender, cursor)
    receiver_id = get_user_id(receiver, cursor)
    
    # Inserting into messages, inbox and outbox
    message_id = insert_into_messages(sender, receiver, message,
                                             subject, creation_date)
    insert_into_mailbox(receiver_id, message_id, cursor, 'inbox')
    insert_into_mailbox(sender_id, message_id, cursor, 'outbox')
    conn.commit()

    return MESSAGE_CREATED


@app.route('/message/<int:message_id>', methods=['PUT', 'DELETE'])
def handle_message(message_id):
    """Returns one message if method is PUT,
    or deletes one message if method is DELETE."""
    if not 'user_id' in session:
        return NOT_LOGGED_IN

    user_id = session['user_id']
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM messages WHERE id='{message_id}'")
    message = cursor.fetchone()
    if not message:
        return MESSAGES_NOT_FOUND
    
    sender_id = get_user_id(message['sender'], cursor)
    receiver_id = get_user_id(message['receiver'], cursor)
    if user_id != receiver_id and user_id != sender_id:
        return MESSAGES_NOT_FOUND

    if request.method == 'PUT':
        if user_id == receiver_id and message['viewed'] == 0:
            cursor.execute(f"UPDATE messages SET viewed=1 WHERE id='{message_id}'")
            conn.commit()
        del message['viewed']
        return jsonify(message), OK

    else:  # method is DELETE
        deleted = False
        if user_id == sender_id:
            deleted = delete_message(
                user_id, receiver_id,'outbox', 'inbox', message_id, cursor
            )

        elif user_id == receiver_id:
            deleted = delete_message(
                user_id, sender_id,'inbox', 'outbox', message_id, cursor
            )

        else:
            return MESSAGES_NOT_FOUND

        conn.commit()
        if deleted:
            return MESSAGE_DELETED
    
        return MESSAGES_NOT_FOUND


@app.route('/sign_up', methods=['POST'])
def sign_up():
    """Signs up a new user to the database"""
    conn = db_connection()
    cursor = conn.cursor()
    salt = bcrypt.gensalt(prefix=b'2b', rounds=10)
    unhashed_password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(unhashed_password, salt)
    username = request.form['username']
    email = request.form['email']
    query = """INSERT INTO users (username, email, password)
                            VALUES(%s, %s, %s)"""
    cursor.execute(query, (username, email, hashed_password))
    conn.commit()
    cursor.execute(f"SELECT id from users WHERE username='{username}'")
    session['user_id'] = cursor.fetchone()['id']
    return SIGN_UP_OK



@app.route('/login', methods=['POST'])
def login():
    """Allows the user to log in to the messaging system"""
    conn = db_connection()
    cursor = conn.cursor()
    username = request.form['username']
    password = request.form['password'].encode('utf-8')
    cursor.execute(f"SELECT id, password from users WHERE username='{username}'")
    user = cursor.fetchone()
    if not user:
        return LOGIN_ERROR
    actual_password = user['password'].encode('utf-8')
    if not bcrypt.checkpw(password, actual_password):
        return LOGIN_ERROR
    
    session['user_id'] = user['id']
    return LOGIN_OK


if __name__ == '__main__':
    app.run(threaded=True, port=5000)