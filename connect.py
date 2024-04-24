import mysql.connector

def connect():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="wordity"
        )
        return mydb
    except BaseException as err:
        print(err)
    return False