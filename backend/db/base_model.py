from datetime import datetime
from uuid import uuid4

from peewee import DateTimeField, Field, Model, SqliteDatabase, TextField

DATABASE_FILENAME: str = "backend/db/db.sqlite3"
db: SqliteDatabase = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    class Meta:
        database = db

    id_ = TextField(primary_key="True", default=uuid4)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, force_insert: bool, only: list[Field] = None):
        self.updated_at = datetime.now()
        super().save(force_insert, only)
