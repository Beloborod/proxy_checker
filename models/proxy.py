from mongoengine import *
from models.connecter import connection

connection()


class ProxyModel(Document):
    meta = {"collection": "proxy"}
    ip = StringField()
    port = IntField()
    protocols = ListField()
    validation_date = DateTimeField()
    anonymity = StringField()
    country = StringField()
    redirects = BooleanField()