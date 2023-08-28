import os
import sys

from db.base_model import db
from product import Product, Tag, TagXProduct
from scraper import Scraper

TAGS: list[str] = [
    'impact', 'intro', 'finale', 'howler', 'colorful'
]
DB_FILENAME: str = "backend/db/db.sqlite3"
PLOTS_DIRECTORY: str = "backend/static/product_plots"


def db_create():
    db.connect()
    db.create_tables([Product, Tag, TagXProduct])
    for tag in TAGS:
        Tag.create(name=tag)
    db.close()


def db_del():
    os.remove(DB_FILENAME)
    with open(DB_FILENAME, 'w') as file:
        file.write("")
    del_plots()


def db_recreate():
    db_del()
    db_create()


def del_plots():
    for filename in os.listdir(PLOTS_DIRECTORY):
        full_filename = os.path.join(
            PLOTS_DIRECTORY, filename
        )
        os.remove(full_filename)


def create_plots():
    products = Product.select()
    for p in products:
        p.create_plots()


def scrape():
    scraper = Scraper()
    scraper.scrape()


def main():
    arg = sys.argv[1]
    if arg == 'db_create':
        db_create()
    elif arg == 'del_plots':
        del_plots()
    elif arg == 'scrape':
        scrape()
    elif arg == 'db_del':
        db_del()
    elif arg == 'create_plots':
        create_plots()
    elif arg == 'db_recreate':
        db_recreate()


if __name__ == "__main__":
    main()
