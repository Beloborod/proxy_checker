from mongoengine import connect

db_name = "YOUR_DB_NAME"

def connection():
    connect(db_name,
            host="HOST_NAME",
            username="USER_NAME",
            password="USER_PASSWORD",
            authentication_source='AUTHENTICATION_DB',
            port=0 #YOUR PORT
            )
