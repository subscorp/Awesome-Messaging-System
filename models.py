import pymysql

conn = pymysql.connect(
    host = 'sql6.freesqldatabase.com',
    database = 'sql6414162',
    user = 'sql6414162',
    password = 'Q6bmEyE9am',
    charset = 'utf8mb4',
    cursorclass = pymysql.cursors.DictCursor
)

cursor = conn.cursor()
query1 = """ CREATE TABLE users (
    id integer PRIMARY KEY AUTO_INCREMENT,
    username text NOT NULL
)"""
query2 = """ CREATE TABLE messages (
    id integer PRIMARY KEY AUTO_INCREMENT,
    sender text NOT NULL,
    receiver text NOT NULL,
    message text NOT NULL,
    subject text,
    creation_date text NOT NULL,
    viewed integer NOT NULL
)"""
query3 = """ CREATE TABLE inbox (
    user_id integer NOT NULL,
    message_id integer NOT NULL
)"""
query4 = """ CREATE TABLE outbox (
    user_id integer NOT NULL,
    message_id integer NOT NULL
)"""
query5 = " INSERT INTO users (username) VALUES('Ori')"
query6 = " INSERT INTO users (username) VALUES('Sagi')"
query7 = " INSERT INTO users (username) VALUES('Daniel')"
query8 = " INSERT INTO users (username) VALUES('Or')"

cursor.execute(query1)
cursor.execute(query2)
cursor.execute(query3)
cursor.execute(query4)
cursor.execute(query5)
cursor.execute(query6)
cursor.execute(query7)
cursor.execute(query8)

conn.commit()
conn.close()