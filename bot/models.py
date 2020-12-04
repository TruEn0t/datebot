from peewee import *

db = SqliteDatabase('users.db')

class Users(Model):
    user_id = IntegerField()
    date = CharField(null=True)
    state = CharField()
    time = CharField(null=True)

    class Meta:
        database = db


Users.create_table()