import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")

conn.execute('CREATE TABLE user (email TEXT, apiKey TEXT, dateCreated DATETIME, lastRequest DATETIME)')
print("Table created successfully")
conn.close()
