import pymysql

OK = 200
CREATED = 201
NOT_FOUND = 404
MESSAGES_NOT_FOUND = 'No messages available', NOT_FOUND
MESSAGE_CREATED = "The message was created successfully", CREATED
MESSAGE_DELETED = "The message was deleted successfully", OK
WRONG_MESSAGE_ID = 'Wrong message id', NOT_FOUND


def db_connection():
    conn = None
    try:
        conn = pymysql.connect(
        host = 'sql6.freesqldatabase.com',
        database = 'sql6414162',
        user = 'sql6414162',
        password = 'Q6bmEyE9am',
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )
    except pymysql.Error as e:
        print(e)
    return conn