import mysql.connector
from mysql.connector import Error

def get_db_connection():

        return mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password='1234@a',
            database='cabinet_medical'
        )
       
