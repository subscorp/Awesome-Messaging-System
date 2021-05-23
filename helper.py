import pymysql


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

def db_connection():
    conn = None
    try:
        conn = pymysql.connect(
        host = 'sql6.freesqldatabase.com',
        database = 'sql6414222',
        user = 'sql6414222',
        password = 'hBfZ7hzQMV',
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )
    except pymysql.Error as e:
        print(e)
    return conn