import os
import re
from functools import cached_property
from string import digits
from typing import Iterator

import matplotlib.pyplot as plt
from db.base_model import BaseModel
from peewee import (BooleanField, DoesNotExist, ForeignKeyField, IntegerField,
                    TextField)


class ProductPlottingMixin:

    PLOTS_DIRECTORY: str = "backend/static/product_plots"
    LIGHTRED = (1, 0.5, 0.5, 1)
    LIGHTGREEN = (0.5, 1, 0.5, 1)
    LIGHTBLUE = (0.5, 0.5, 1, 1)

    FIELDS_TO_COLORS = {
        'price': LIGHTRED,
        'weight': LIGHTGREEN,
        'min_caliber': LIGHTBLUE,
        'max_caliber': LIGHTBLUE,
        'min_height': LIGHTBLUE,
        'max_height': LIGHTBLUE,
        'shot_count': LIGHTGREEN,
        'duration': LIGHTGREEN,
        'nem': LIGHTGREEN,
        'nem_per_second': LIGHTGREEN,
        'nem_per_shot': LIGHTGREEN,
        'shots_per_second': LIGHTGREEN,
        'price_per_shot': LIGHTRED,
        'price_per_second': LIGHTRED,
        'price_per_nem': LIGHTRED
    }

    IS_PROPERTY: dict[str, bool] = {
        'price': False,
        'weight': False,
        'min_caliber': False,
        'max_caliber': False,
        'min_height': False,
        'max_height': False,
        'shot_count': True,
        'duration': False,
        'nem': False,
        'nem_per_second': True,
        'nem_per_shot': True,
        'shots_per_second': True,
        'price_per_shot': True,
        'price_per_second': True,
        'price_per_nem': True
    }

    def _property_values(self, field_name: str) -> Iterator[any]:
        for product in Product.select():
            try:
                value = getattr(product, field_name)
                if value is not None:
                    yield value
            except TypeError:
                pass

    def _create_plot(self, field_name: str) -> str:
        print(f"{self.name}: {field_name}")

        values = (
            list(self._property_values(field_name))
            if self.IS_PROPERTY[field_name]
            else [
                getattr(p, field_name) for p in
                Product.select()
                .where(getattr(Product, field_name).is_null(False))
            ]
        )

        fig, ax = plt.subplots()
        fig.set_figwidth(10)
        fig.set_figheight(1)

        boxplot = ax.boxplot(
            x=values, vert=False, whis=[5, 95], notch=True,
            medianprops={'color': 'black'}, patch_artist=True,
            showfliers=False,
            widths=[0.99]
        )
        boxplot['boxes'][0].set_facecolor(self.FIELDS_TO_COLORS[field_name])
        try:
            ax.axvline(
                getattr(self, field_name), 0, 1000, color='black',
                linewidth=3
            )
        except TypeError:
            return
        ax.legend_ = None
        for pos in ('top', 'right', 'bottom', 'left'):
            ax.spines[pos].set_visible(False)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        filename = os.path.join(
            self.PLOTS_DIRECTORY,
            f"{self.id_}_{field_name}.svg"
        )
        fig.savefig(filename)
        plt.close(fig)
        return filename

    def create_plots(self) -> dict[str, str]:
        return {
            field_name: self._create_plot(field_name)
            for field_name in self.FIELDS_TO_COLORS
        }


class ProductSerializeMixin:

    def to_dict(self) -> dict[str, any]:
        tags = (
            Tag.select().join(TagXProduct).join(Product)
            .where(Product.id_ == self.id_)
        )
        return {
            'id_': self.id_,
            'url': self.url,
            'name': self.name,
            'article_number': self.article_number,
            'price': self.price,
            'youtube_handle': self.youtube_handle,
            'weight': self.weight,
            'min_caliber': self.min_caliber,
            'max_caliber': self.max_caliber,
            'min_height': self.min_height,
            'max_height': self.max_height,
            'shot_count': self.shot_count,
            'duration': self.duration,
            'fan': self.fan,
            'nem': self.nem,
            'availability': self.availability,
            'rating': self.rating,
            'rated': self.rated,
            'tags': [t.name for t in tags],
            'nem_per_second': self.nem_per_second,
            'nem_per_shot': self.nem_per_shot,
            'shots_per_second': self.shots_per_second,
            'price_per_shot': self.price_per_shot,
            'price_per_second': self.price_per_second,
            'price_per_nem': self.price_per_nem,
            'short_name': self.short_name,
            'package_size': self.package_size
        }

    def _update_tags(self, tags: list[str]):
        my_tags = (
            Tag.select().join(TagXProduct).join(Product)
            .where(Product.id_ == self.id_)
        )
        for tag_str in tags:
            try:
                tag = Tag.get(Tag.name == tag_str)
            except DoesNotExist:
                tag = Tag.create(name=tag_str)
                TagXProduct.create(tag=tag, product=self)
                continue

            if tag not in my_tags:
                TagXProduct.create(tag=tag, product=self)

        for tag in my_tags:
            if tag.name in tags:
                continue
            tag_x_product = TagXProduct.get(
                TagXProduct.tag == tag,
                TagXProduct.product == self
            )
            tag_x_product.delete_instance()

    def update_field(self, key: str, value: any):
        if key == 'tags':
            self._update_tags(value)
        elif hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Invalid Key: {key}")


class ProductPropertyMixin:

    remove_from_name_pattern: re.Pattern = re.compile(
        r"(?P<to_remove>[0-9]+[\s-]((Schus(s)?)|(Effekte))[\s-].*)"
    )

    @cached_property
    def package_size(self) -> int:
        n_packages = 1
        if "er Pack" in self.name:
            idx = self.name.index("er Pack") - 1
            n_digits = 1
            while self.name[idx - 1] in digits:
                idx -= 1
                n_digits += 1
            n_packages = int(self.name[idx:idx + n_digits])
        return n_packages

    @property
    def youtube_link(self) -> str:
        BASE_URL = "https://youtube.com"
        if self.youtube_handle is None:
            return f"{BASE_URL}/404"
        return f"{BASE_URL}/watch?v={self.youtube_handle}"

    @property
    def nem_per_second(self) -> float:
        try:
            return round(
                0.001 * self.nem / self.duration / self.package_size, 3
            )
        except TypeError:
            return

    @property
    def nem_per_shot(self) -> float:
        try:
            return round(0.001 * self.nem / self.shot_count, 3)
        except TypeError:
            return

    @property
    def shots_per_second(self) -> float:
        try:
            return round(self.shot_count / self.duration, 2)
        except TypeError:
            return

    @property
    def price_per_shot(self) -> float:
        try:
            return round(0.01 * self.price / self.shot_count, 2)
        except TypeError:
            return

    @property
    def price_per_second(self) -> float:
        try:
            return round(0.01 * self.price / self.duration, 2)
        except TypeError:
            return

    @property
    def price_per_nem(self) -> float:
        try:
            return round(10 * self.price / self.nem, 2)
        except TypeError:
            return

    @property
    def shot_count(self) -> int:
        p_size = self.package_size
        if p_size == 1:
            return self.raw_shot_count
        if (
            (self.raw_shot_count or p_size) < p_size
            or (self.raw_shot_count or p_size) % p_size != 0
            or (
                not self.shot_count_has_multiplier
                and self.raw_shot_count is not None
            )
        ):
            return self.raw_shot_count * self.package_size
        return self.raw_shot_count

    @cached_property
    def short_name(self) -> str:
        matches = self.remove_from_name_pattern.findall(self.name)
        if len(matches) == 0:
            return self.name
        matches = matches[0]
        if matches:
            return self.name.replace(matches[0], "")
        else:
            return self.name


class Product(
    BaseModel, ProductPlottingMixin,
    ProductSerializeMixin, ProductPropertyMixin
):
    url = TextField(unique=True)
    name = TextField()
    article_number = TextField(unique=True)
    price = IntegerField(null=True)
    youtube_handle = TextField(null=True)
    weight = IntegerField(null=True)
    min_caliber = IntegerField(null=True)
    max_caliber = IntegerField(null=True)
    min_height = IntegerField(null=True)
    max_height = IntegerField(null=True)
    raw_shot_count = IntegerField(null=True)
    duration = IntegerField(null=True)
    fan = BooleanField(default=False)
    nem = IntegerField(null=True)
    availability = BooleanField(default=True)
    shot_count_has_multiplier = BooleanField(null=True)

    rating = BooleanField(default=None, null=True)
    rated = BooleanField(default=False)


class Tag(BaseModel):
    name = TextField(unique=True)


class TagXProduct(BaseModel):
    tag = ForeignKeyField(Tag, backref='tag_x_product')
    product = ForeignKeyField(Product, backref='tag_x_product')


if __name__ == "__main__":
    p = Product.get()
    p.create_plots()
