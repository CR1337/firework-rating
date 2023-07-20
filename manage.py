from product import Product, Tag, TagXProduct
from db.base_model import db
import sys
import os
from scraper import Scraper


TAGS: list[str] = [
    'impact', 'intro', 'finale', 'howler'
]


def main():
    arg = sys.argv[1]
    if arg == 'db_create':
        db.connect()
        db.create_tables([Product, Tag, TagXProduct])
        for tag in TAGS:
            Tag.create(name=tag)
        db.close()
    elif arg == 'del_plots':
        for filename in os.listdir("static/product_plots"):
            full_filename = os.path.join("static/product_plots", filename)
            os.remove(full_filename)
    elif arg == 'scrape':
        scraper = Scraper()
        scraper.scrape()
    elif arg == 'del_db':
        os.remove("db/db.sqlite3")
        with open("db/db.sqlite3", 'w') as file:
            file.write("")


if __name__ == "__main__":
    main()
