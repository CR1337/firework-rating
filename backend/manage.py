import os
import sys
from multiprocessing import Pool, cpu_count

from db.base_model import db
from product import Product, Tag, TagXProduct
from scraper import Scraper
from temp_directory import TempDirectory

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
    for idx, p in enumerate(products):
        print(f"{idx + 1}/{len(products)}: {p.name}")
        p.create_plots()


def _download_video_entrypoint(
    product_id: str, temp_directory: str, index: int
):
    product = Product.get(Product.id_ == product_id)
    print(product.name)
    product.download_video(temp_directory, index)


def download_videos():
    pool = Pool(1)#cpu_count())
    temp_directory = TempDirectory().directory
    args = [(p.id_, temp_directory, i) for i, p in enumerate(Product.select())]
    # pool.starmap(_download_video_entrypoint, args)
    for arg in args:
        _download_video_entrypoint(*arg)
    pool.close()
    pool.join()


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
    elif arg == 'download_videos':
        download_videos()


if __name__ == "__main__":
    main()
