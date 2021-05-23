from helper import db_connection


conn = db_connection()
cursor = conn.cursor()
query1 = """ CREATE TABLE users (
    id integer PRIMARY KEY AUTO_INCREMENT,
    username text NOT NULL,
    email text NOT NULL,
    password text NOT NULL
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

queries = [query1, query2, query3, query4]
for query in queries:
    cursor.execute(query)
conn.commit()