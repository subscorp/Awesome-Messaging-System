import pymysql
from app import app


# Constants

OK = 200
CREATED = 201
FORBIDDEN = 403 
NOT_FOUND = 404
MESSAGES_NOT_FOUND = 'No messages available', NOT_FOUND
MESSAGE_CREATED = "The message was created successfully", CREATED
MESSAGE_DELETED = "The message was deleted successfully", OK
WRONG_MESSAGE_ID = 'Wrong message id', NOT_FOUND
SIGN_UP_OK = "Signed up successfully", OK
LOGIN_OK = "Logged in successfully", OK
LOGIN_ERROR = "Wrong username or password", FORBIDDEN
NOT_LOGGED_IN = "Please log in with your credentials", FORBIDDEN
WELCOME_MESSAGE = "Welcome to our Messaging System!", OK

# Helper functions

def db_connection():
    """Returns a database connection."""
    conn = None
    try:
        conn = pymysql.connect(
        host = 'sql6.freesqldatabase.com',
        database = 'sql6414237',
        user = app.config["DB_USER"],
        password = app.config["DB_PASS"],
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )
    except pymysql.Error as e:
        print(e)
    return conn


def get_mailbox_ids(user_id, cursor, mailbox):
    cursor.execute(f"SELECT message_id FROM {mailbox} WHERE user_id='{user_id}'")
    mailbox_ids = tuple(one_res['message_id'] for one_res in cursor.fetchall())
    if len(mailbox_ids) == 1:
        mailbox_ids = f'({mailbox_ids[0]})'
    return mailbox_ids


def get_messages_from_db(mailbox_ids, cursor, unread=False):
    query = f"SELECT * FROM messages WHERE id in {mailbox_ids}"
    if unread:
        query += "AND viewed=0"
    cursor.execute(query)
    messages = [
        dict(id=row['id'], sender=row['sender'], receiver=row['receiver'], message=row['message'],
                subject=row['subject'], creation_date=row['creation_date'], viewed=row['viewed'])
        for row in cursor.fetchall()
    ]
    return messages



def get_user_id(username, cursor):
    cursor.execute(f"SELECT id from users WHERE username='{username}'")
    return cursor.fetchone()['id']


def insert_into_messages(sender, receiver, message, subject, creation_date, cursor):
    query = """INSERT INTO messages (sender, receiver, message, subject,
                creation_date, viewed) VALUES(%s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (sender, receiver, message, subject, creation_date, 0))
    return cursor.lastrowid
    

def insert_into_mailbox(user_id, message_id, cursor, mailbox):
    query = f"""INSERT INTO {mailbox} (user_id, message_id)
                            VALUES(%s, %s)"""
    cursor.execute(query, (user_id, message_id))


def get_form_params_post(request):
    sender = request.form['sender']
    receiver = request.form['receiver']
    message = request.form['message']
    subject = request.form['subject']
    return (sender, receiver, message, subject)


def delete_message(user_id, communicator_id,
                     mailbox1, mailbox2, message_id, cursor):
    res = cursor.execute(f"DELETE FROM {mailbox1} WHERE message_id='{message_id}'")
    if res:
        deleted = True

    exist = cursor.execute(
        f"""SELECT * FROM {mailbox2} WHERE user_id='{communicator_id}'
        AND message_id='{message_id}'"""
    )
    if not exist:
        cursor.execute(f"DELETE FROM messages WHERE id='{message_id}'")
    return deleted