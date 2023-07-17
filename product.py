from peewee import BooleanField, IntegerField, TextField, ForeignKeyField

from db.base_model import BaseModel

import matplotlib.pyplot as plt
import os
from typing import Iterator


class Product(BaseModel):
    url = TextField(unique=True)
    name = TextField()
    article_number = TextField(unique=True)
    price = IntegerField()
    youtube_handle = TextField(null=True)
    weight = IntegerField(null=True)
    min_caliber = IntegerField(null=True)
    max_caliber = IntegerField(null=True)
    min_height = IntegerField(null=True)
    max_height = IntegerField(null=True)
    shot_count = IntegerField(null=True)
    duration = IntegerField(null=True)
    fan = BooleanField(default=False)
    nem = IntegerField(null=True)
    availability = BooleanField(default=True)

    rating = BooleanField(default=False)
    rated = BooleanField(default=False)

    PLOTS_DIRECTORY: str = "static/product_plots"
    LIGHTRED = (1, 0.5, 0.5, 1)
    LIGHTGREEN = (0.5, 1, 0.5, 1)

    FIELDS_TO_COLORS = {
        'price': LIGHTRED,
        'weight': LIGHTGREEN,
        'min_caliber': LIGHTGREEN,
        'max_caliber': LIGHTGREEN,
        'min_height': LIGHTGREEN,
        'max_height': LIGHTGREEN,
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
        'shot_count': False,
        'duration': False,
        'nem': False,
        'nem_per_second': True,
        'nem_per_shot': True,
        'shots_per_second': True,
        'price_per_shot': True,
        'price_per_second': True,
        'price_per_nem': True
    }

    @property
    def youtube_link(self) -> str:
        BASE_URL = "https://youtube.com"
        if self.youtube_handle is None:
            return f"{BASE_URL}/404"
        return f"{BASE_URL}/watch?v={self.youtube_handle}"

    @property
    def nem_per_second(self) -> float:
        try:
            return round(self.nem / self.duration, 2)
        except TypeError:
            return

    @property
    def nem_per_shot(self) -> float:
        try:
            return round(self.nem / self.shot_count, 2)
        except TypeError:
            return

    @property
    def shots_per_second(self) -> float:
        try:
            return (self.shot_count / self.duration, 2)
        except TypeError:
            return

    @property
    def price_per_shot(self) -> float:
        try:
            return round(self.price / self.shot_count, 2)
        except TypeError:
            return

    @property
    def price_per_second(self) -> float:
        try:
            return round(self.price / self.duration, 2)
        except TypeError:
            return

    @property
    def price_per_nem(self) -> float:
        try:
            return round(self.price / self.nem, 2)
        except TypeError:
            return

    def _property_values(self, field_name: str) -> Iterator[any]:
        for product in Product.select():
            try:
                value = getattr(product, field_name)
                if value is not None:
                    yield value
            except TypeError:
                pass

    def _create_plot(self, field_name: str) -> str:
        if self.IS_PROPERTY[field_name]:
            values = list(self._property_values(field_name))
        else:
            values = [
                getattr(p, field_name) for p in
                Product.select()
                .where(getattr(Product, field_name).is_null(False))
            ]
        fig, ax = plt.subplots()
        fig.set_figwidth(10)
        fig.set_figheight(1)
        medianprops = {'color': 'black'}

        boxplot = ax.boxplot(
            x=values, vert=False, whis=[5, 95], notch=True,
            medianprops=medianprops, patch_artist=True,
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
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        filename = os.path.join(
            self.PLOTS_DIRECTORY, f"{self.id_}_{field_name}.svg"
        )
        fig.savefig(filename)
        plt.close(fig)
        return filename

    def create_plots(self) -> dict[str, str]:
        return {
            field_name: self._create_plot(field_name)
            for field_name in self.FIELDS_TO_COLORS
        }

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
            'price_per_nem': self.price_per_nem
        }

    def update_field(self, key: str, value: any):
        if key == 'tags':
            ...  # TODO
        elif hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Invalid Key: {key}")


class Tag(BaseModel):
    name = TextField


class TagXProduct(BaseModel):
    tag = ForeignKeyField(Tag, backref='tag_x_product')
    product = ForeignKeyField(Product, backref='tag_x_product')


if __name__ == "__main__":
    p = Product.get()
    p.create_plots()
