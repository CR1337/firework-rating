import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from string import digits
from threading import Lock
from typing import Callable, Iterator

import requests
from bs4 import BeautifulSoup
from peewee import DoesNotExist
from product import Product


class Scraper:

    CORE_FACTOR: int = 3
    BASE_URL: str = "https://pyroland.de"
    MAIN_PAGE_URLS: list[str] = [
        "/".join([BASE_URL, "Feuerwerkbatterien"]),
        "/".join([BASE_URL, "Verbundfeuerwerk"])
    ]

    _db_lock: Lock

    def __init__(self):
        self._db_lock = Lock()

    def _request_soup(self, url: str) -> BeautifulSoup:
        wait_time = 0.01
        while True:
            try:
                response = requests.get(url)
            except requests.exceptions.Timeout:
                print(f"Timeout for {url}. Waiting {wait_time}...")
                time.sleep(wait_time)
                wait_time *= 2
            except requests.exceptions.TooManyRedirects:
                raise
            except requests.exceptions.HTTPError:
                raise
            except requests.exceptions.RequestException:
                raise
            else:
                return BeautifulSoup(response.content, 'html.parser')

    def _page_count(self, soup: BeautifulSoup) -> int:
        li = soup.find('li', "pages")
        span = next(li.children)
        return int(span.text.strip().split("/")[-1].strip())

    def _subpage_urls(self, index: int, page_count: int) -> Iterator[str]:
        return (
            f"{self.MAIN_PAGE_URLS[index]}_s{i + 1}"
            for i in range(page_count)
        )

    def _product_urls(self, subpage_soup: BeautifulSoup) -> Iterator[str]:
        a_s = subpage_soup.find_all('a', "image-wrapper")
        return (
            f"{self.BASE_URL}/{a.get('href')}" for a in a_s
        )

    def _product_name(self, product_soup: BeautifulSoup) -> str:
        return product_soup.find('h1', "fn product-title").text.strip()

    def _product_article_number(self, product_soup: BeautifulSoup) -> str:
        return product_soup.find('span', {'itemprop': "sku"}).text.strip()

    def _product_price(self, product_soup: BeautifulSoup) -> int:
        try:
            meta = product_soup.find('meta', {'itemprop': "price"})
            price_string = meta.get('content')
            return int(float(price_string) * 100)
        except Exception:
            return None

    def _product_youtube_handle(self, product_soup: BeautifulSoup) -> str:
        iframe = product_soup.find('iframe', "youtube")
        url = iframe.get('data-src')
        return url.split("/")[-1].split("?")[0]

    def _product_weight(self, product_soup: BeautifulSoup) -> int:
        td = product_soup.find(
            'td', "attr-value weight-unit weight-unit-article"
        )
        span = td.find('span', {'itemprop': "value"})
        value = float("".join(
            c for c in span.text.strip() if c in digits + ".,"
        ).replace(",", "."))
        return int(value * 1000)

    def _product_properties(
        self, product_soup: BeautifulSoup
    ) -> dict[str, str]:
        trs = (
            product_soup.find_all('tr', "attr-custom")
            + product_soup.find_all('tr', "attr-custom attr-custom-header")
        )
        result = {}
        for tr in trs:
            try:
                key = tr.find('td', "attr-label word-break").text.strip()
                key = key.replace(":", "").strip().lower().replace("ß", "ss")
                key = key.replace("ä", "ae").replace("ö", "oe")
                key = key.replace("ü", "ue").split()[0]
                value = tr.find('td', "attr-value").text.strip()
                result[key] = value
            except (KeyError, AttributeError):
                continue
        return result

    def _extract_min_max(self, string: str) -> tuple[float, float]:
        string = "".join(
            c if c in digits + ",." else "X"
            for c in string if c in digits
        )
        splits = (s.replace(",", ".") for s in string.split("X") if len(s))
        values = [float(s) for s in splits]
        return min(values), max(values)

    def _product_caliber(
            self, product_properties: dict[str, str]
    ) -> tuple[int, int]:
        if 'kaliber' not in product_properties:
            return None
        min_value, max_value = self._extract_min_max(
            product_properties['kaliber']
        )
        return int(min_value), int(max_value)

    def _product_height(
        self, product_properties: dict[str, str]
    ) -> tuple[int, int]:
        if 'effekthoehe' not in product_properties:
            return None
        min_value, max_value = self._extract_min_max(
            product_properties['effekthoehe']
        )
        return int(min_value), int(max_value)

    def _product_shot_count(self, product_properties: dict[str, str]) -> int:
        if 'schussanzahl' not in product_properties:
            return None
        return int("".join(
            c for c in product_properties['schussanzahl'] if c in digits
        ))

    def _product_duration(self, product_properties: dict[str, str]) -> int:
        if 'brenndauer' not in product_properties:
            return None
        return int("".join(
            c for c in product_properties['brenndauer'] if c in digits
        ))

    def _product_fan(self, product_properties: dict[str, str]) -> bool:
        performance = product_properties.get('performance', '')
        return 'faecher' in performance.lower().replace("ä", "ae")

    def _product_nem(self, product_properties: dict[str, str]) -> int:
        if 'nem' not in product_properties:
            return None
        value = float("".join(
            c for c in product_properties['nem'] if c in digits + ".,"
        ).replace(",", "."))
        return int(value * 1000)

    def _product_availability(self, product_soup: BeautifulSoup) -> bool:
        return not any(
            len(product_soup.body.findAll(string=string)) > 0
            for string in ("ausverkauft", "Ausverkauft")
        )

    EXTRACTION_METHODS: dict[str, tuple[bool, Callable, int]] = {
        'name': (True, _product_name, -1),
        'price': (True, _product_price, -1),
        'youtube_handle': (True, _product_youtube_handle, -1),
        'weight': (True, _product_weight, -1),
        'min_caliber': (False, _product_caliber, 0),
        'max_caliber': (False, _product_caliber, 1),
        'min_height': (False, _product_height, 0),
        'max_height': (False, _product_height, 1),
        'raw_shot_count': (False, _product_shot_count, -1),
        'duration': (False, _product_duration, -1),
        'fan': (False, _product_fan, -1),
        'nem': (False, _product_nem, -1),
        'availability': (True, _product_availability, -1)
    }.items()

    def _create_product(self, product_url: str) -> Product:
        soup = self._request_soup(product_url)
        properties = self._product_properties(soup)
        article_number = self._product_article_number(soup)

        def get_value(method: Callable, index: int, use_soup: bool) -> any:
            try:
                value = method(self, soup if use_soup else properties)
            except (KeyError, AttributeError):
                return None
            if value is None:
                return None
            if index >= 0:
                value = value[index]
            return value

        try:
            product = Product.get(Product.article_number == article_number)
            product.url = product_url
            for name, (use_soup, method, index) in self.EXTRACTION_METHODS:
                setattr(product, name, get_value(method, index, use_soup))
            with self._db_lock:
                product.save(force_insert=False)
        except DoesNotExist:
            product = Product(**{
                name: get_value(method, index, use_soup)
                for name, (use_soup, method, index)
                in self.EXTRACTION_METHODS
            })
            product.url = product_url
            product.article_number = article_number
            with self._db_lock:
                product.save(force_insert=True)

        print(product_url)
        return product

    def scrape(self):
        print("Scraping product urls...")
        main_page_soups = (
            self._request_soup(url) for url in self.MAIN_PAGE_URLS
        )
        page_counts = (
            self._page_count(soup) for soup in main_page_soups
        )
        subpage_urls = chain.from_iterable(
            self._subpage_urls(i, pc) for i, pc in enumerate(page_counts)
        )
        subpage_soups = (
            self._request_soup(url) for url in subpage_urls
        )
        product_urls = list(chain.from_iterable(
            self._product_urls(soup) for soup in subpage_soups
        ))

        all_products = Product.select()

        print("Scraping products...")
        process_count = self.CORE_FACTOR * multiprocessing.cpu_count()
        process_count = 1
        with ThreadPoolExecutor(max_workers=process_count) as executor:
            found_products = executor.map(self._create_product, product_urls)

        for product in all_products:
            if product not in found_products:
                product.availability = False
                product.save(force_insert=False)

        print("Creating plots...")
        for product in all_products:
            product.create_plots()

        print(len(product_urls))


if __name__ == "__main__":
    from db.base_model import db
    db.connect()
    s = Scraper()
    try:
        s.scrape()
    except KeyboardInterrupt:
        pass
    finally:
        db.commit()
        db.close()
