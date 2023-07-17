from product import Product, Tag, TagXProduct
from db.base_model import db


def main():
    db.connect()
    db.create_tables([Product, Tag, TagXProduct])
    db.close()


if __name__ == "__main__":
    main()
