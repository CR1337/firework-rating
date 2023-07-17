from uuid import uuid4
from datetime import datetime

from peewee import Field, Model, SqliteDatabase, TextField, DateTimeField

DATABASE_FILENAME: str = "db/db.sqlite3"
db: SqliteDatabase = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    class Meta:
        database = db

    id_ = TextField(primary_key="True", default=uuid4)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, force_insert: bool = True, only: list[Field] = None):
        self.updated_at = datetime.now()
        super().save(force_insert, only)
