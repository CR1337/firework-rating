import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from itertools import chain
from string import digits
from threading import Lock
from typing import Callable, Iterator

import requests
from bs4 import BeautifulSoup
from peewee import DoesNotExist
from product import Product
import re
from math import ceil


class ProductProperties:

    _properties: dict
    _soup: BeautifulSoup

    def __init__(self, product_soup: BeautifulSoup):
        self._properties = {}
        self._soup = product_soup
        self._extract_properties()

    def _extract_properties(self):
        trs = (
            self._soup.find_all('tr', "attr-custom")
            + self._soup.find_all('tr', "attr-custom attr-custom-header")
        )
        for tr in trs:
            try:
                key = tr.find('td', "h6").text.strip()
                key = key.replace(":", "").strip().lower().replace("ß", "ss")
                key = key.replace("ä", "ae").replace("ö", "oe")
                key = key.replace("ü", "ue").split()[0]
                value = tr.find('td', "attr-value").text.strip()
                self._properties[key] = value
            except (KeyError, AttributeError):
                continue

    def _extract_min_max(self, string: str) -> tuple[float, float]:
        string = "".join(
            c if c in digits + ",." else "X"
            for c in string if c in digits
        )
        splits = (s.replace(",", ".") for s in string.split("X") if len(s))
        values = [float(s) for s in splits]
        return min(values), max(values)

    def caliber(self) -> tuple[int, int]:
        if 'kaliber' not in self._properties:
            return None
        min_value, max_value = self._extract_min_max(
            self._properties['kaliber']
        )
        return int(min_value), int(max_value)

    def height(self) -> tuple[int, int]:
        if 'effekthoehe' not in self._properties:
            return None
        min_value, max_value = self._extract_min_max(
            self._properties['effekthoehe']
        )
        return int(min_value), int(max_value)

    def shot_count(self) -> int:
        if 'schussanzahl' not in self._properties:
            return None
        raw = self._properties['schussanzahl']
        raw = raw.split("und") if "und" in raw else [raw]
        result = 0
        for r in raw:
            r = "".join(c for c in r if c in digits + 'xX*').lower()
            for s in 'x*':
                if s in r:
                    a, b = r.split(s)
                    result += int(a) * int(b)
                    break
            else:
                result += int(r)
        return result

    def shot_count_has_multiplier(self) -> bool:
        for s in 'xX*':
            if s in self._properties['schussanzahl']:
                return True
        if "und" in self._properties['schussanzahl']:
            return True
        return False

    def duration(self) -> int:
        if 'brenndauer' not in self._properties:
            return None
        return int("".join(
            c for c in self._properties['brenndauer'] if c in digits
        ))

    def fan(self) -> bool:
        performance = self._properties.get('performance', '')
        return 'faecher' in performance.lower().replace("ä", "ae")

    def nem(self) -> int:
        if 'nem' not in self._properties:
            return None
        value = float("".join(
            c for c in self._properties['nem'] if c in digits + ".,"
        ).replace(",", "."))
        return int(value * 1000)

    def name(self) -> str:
        return self._soup.find('h1', "product-title h2").text.strip()

    def article_number(self) -> str:
        return self._soup.find('span', {'itemprop': "sku"}).text.strip()

    def price(self) -> int:
        try:
            meta = self._soup.find('meta', {'itemprop': "price"})
            price_string = meta.get('content')
            return int(float(price_string) * 100)
        except Exception:
            return None

    def youtube_handle(self) -> str:
        iframe = self._soup.find('iframe', "youtube")
        url = iframe.get('src')
        return url.split("/")[-1].split("?")[0]

    def weight(self) -> int:
        td = self._soup.find(
            'td', "weight-unit"
        )
        span = td.find('span', {'itemprop': "value"})
        value = float("".join(
            c for c in span.text.strip() if c in digits + ".,"
        ).replace(",", "."))
        return int(value * 1000)

    def availability(self) -> bool:
        return not any(
            len(self._soup.body.findAll(string=string)) > 0
            for string in ("ausverkauft", "Ausverkauft")
        )

    EXTRACTION_METHODS: dict[str, tuple[bool, Callable, int]] = {
        'name': name,
        'price': price,
        'youtube_handle': youtube_handle,
        'weight': weight,
        'min_caliber': caliber,
        'max_caliber': caliber,
        'min_height': height,
        'max_height': height,
        'raw_shot_count': shot_count,
        'duration': duration,
        'fan': fan,
        'nem': nem,
        'availability': availability,
        'shot_count_has_multiplier': shot_count_has_multiplier
    }.items()


class Scraper:

    THREADS_PER_CORE: int = 3
    BASE_URL: str = "https://pyroland.de"
    PRODUCTS_PER_PAGE: int = 50
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
        # li = soup.find('li', "pages")
        # span = next(li.children)
        # return int(span.text.strip().split("/")[-1].strip())
        div = soup.find(
            'div',
            "col productlist-item-info productlist-item-border col-auto"
        )
        text = div.text.strip()
        matches = re.findall(
            r"Artikel\s*(?P<first_index>[1-9][0-9]*)\s*-\s*"
            r"(?P<last_index>[1-9][0-9]*)\s*von\s*"
            r"(?P<amount>[1-9][0-9]*)",
            text
        )
        first_index, last_index, amount = matches[0]
        return int(ceil(
            int(amount) / (int(last_index) - int(first_index) + 1)
        ))

    def _subpage_urls(self, index: int, page_count: int) -> Iterator[str]:
        return (
            f"{self.MAIN_PAGE_URLS[index]}_s{i + 1}"
            f"?af={self.PRODUCTS_PER_PAGE}"
            for i in range(page_count)
        )

    def _product_urls(self, subpage_soup: BeautifulSoup) -> Iterator[str]:
        divs = subpage_soup.find_all(
            'div',
            "productbox-images list-gallery"
        )
        a_s = (div.find('a') for div in divs)
        return (a.get('href') for a in a_s)

    def _create_product(self, product_url: str) -> Product:
        soup = self._request_soup(product_url)
        properties = ProductProperties(soup)

        def get_value(method: Callable, index: int) -> any:
            try:
                if (value := method(properties)) is None:
                    return None
            except (KeyError, AttributeError):
                return None
            if index >= 0:
                value = value[index]
            return value

        def get_index(name: str) -> int:
            try:
                return ["min", "max"].index(name[:3])
            except ValueError:
                return -1

        exists = False
        try:
            product = Product.get(
                Product.article_number == properties.article_number()
            )
            exists = True
            for name, method in properties.EXTRACTION_METHODS:
                setattr(product, name, get_value(method, get_index(name)))
        except DoesNotExist:
            product = Product(**{
                name: get_value(method, get_index(name))
                for name, method
                in properties.EXTRACTION_METHODS
            })
        finally:
            product.url = product_url
            product.article_number = properties.article_number()
            with self._db_lock:
                product.save(force_insert=not exists)

        return product

    def scrape(self):
        print("Scraping product urls...")
        main_page_soups = (
            self._request_soup(f"{url}?af={self.PRODUCTS_PER_PAGE}")
            for url in self.MAIN_PAGE_URLS
        )
        page_counts = (
            self._page_count(soup) for soup in main_page_soups
        )
        subpage_urls = (chain.from_iterable(
            self._subpage_urls(i, pc) for i, pc in enumerate(page_counts)
        ))
        subpage_soups = (
            self._request_soup(url) for url in subpage_urls
        )
        product_urls = list(chain.from_iterable(
            self._product_urls(soup) for soup in subpage_soups
        ))

        all_products = Product.select()

        print("Scraping products...")
        threaded = False
        if threaded:
            process_count = self.THREADS_PER_CORE * multiprocessing.cpu_count()
            with ThreadPoolExecutor(max_workers=process_count) as executor:
                found_products = executor.map(
                    self._create_product, product_urls
                )
                executor.shutdown(wait=True)
        else:
            found_products = []
            for idx, url in enumerate(product_urls):
                print(f"{idx + 1}/{len(product_urls)}: {url}")
                found_products.append(self._create_product(url))

        for product in all_products:
            if product not in found_products:
                product.availability = False
                product.save(force_insert=False)

        print(len(all_products))


if __name__ == "__main__":
    from db.base_model import db
    db.connect()
    s = Scraper()
    try:
        s.scrape()
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
