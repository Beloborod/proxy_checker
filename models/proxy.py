from mongoengine import *
from models.connector import connection

connection()


class ProxyModel(Document):
    meta = {"collection": "proxy"}
    ip = StringField()
    port = IntField()
    protocols = ListField()
    valid = BooleanField()
    validation_date = DateTimeField()
    anonymity = StringField()
    country = StringField()
    redirects = BooleanField()
    total_checks = IntField(default=0)
    success_checks = IntField(default=0)
    judge_invalid_count = IntField(default=0)
    judge_valid_count = IntField(default=0)
    judged = BooleanField(default=False)
