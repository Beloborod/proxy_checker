from mongoengine import connect


def connection():
    connect('DB_NAME',
            host="HOST_NAME",
            username="USER_NAME",
            password="USER_PASSWORD",
            authentication_source='AUTHENTICATION_DB',
            port=0 #YOUR PORT
            )
