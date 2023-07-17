from uuid import uuid4

from peewee import Field, Model, SqliteDatabase, TextField

DATABASE_FILENAME: str = "db/db.sqlite3"
db: SqliteDatabase = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    class Meta:
        database = db

    id_ = TextField(primary_key="True", default=uuid4)

    def save(self, force_insert: bool = True, only: list[Field] = None):
        super().save(force_insert, only)
