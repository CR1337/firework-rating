from __future__ import annotations
from product import Product, Color, ColorXProduct, Tag, TagXProduct
from peewee import fn, DoesNotExist
from abc import ABC, abstractmethod


class Token(ABC):
    pass


class OperatorToken(Token):

    OR: str = 'or'
    AND: str = 'and'
    NOT: str = 'not'

    _operator: str

    def __init__(self, operator: str):
        self._operator = operator

    def __lt__(self, other: OperatorToken) -> bool:
        if isinstance(other, ParenthesisToken):
            return False
        elif isinstance(other, OperatorToken):
            if self._operator == self.AND:
                return other._operator == self.OR
            elif self._operator == self.OR:
                return False
            elif self._operator == self.NOT:
                return True

    def __eq__(self, other: OperatorToken) -> bool:
        if not isinstance(other, OperatorToken):
            return False
        return self._operator == other._operator


class ParenthesisToken(Token):

    OPEN: str = '('
    CLOSE: str = ')'

    _parenthesis: str

    def __init__(self, parenthesis: str):
        self._parenthesis = parenthesis

    def __eq__(self, other: ParenthesisToken) -> bool:
        return self._parenthesis == other._parenthesis

    def is_open(self) -> bool:
        return self._parenthesis == self.OPEN

    def is_close(self) -> bool:
        return self._parenthesis == self.CLOSE


class FilterToken(Token):

    filter_: ProductFilter

    def __init__(self, filter_: ProductFilter):
        self.filter_ = filter_

    def __invert__(self) -> ProductFilter:
        return self.__class__(~self.filter_)


class ProductFilter(ABC):

    _value: any
    _operation: str
    _inverted: bool
    _column_name: str

    def __init__(
        self, value: any, operation: str, inverted: bool, column_name: str
    ):
        self._value = value
        self._operation = operation
        self._inverted = inverted
        self._column_name = column_name

    def __invert__(self) -> ProductFilter:
        return self.__class__(self._value, self._operation, not self._inverted)

    @abstractmethod
    def run(self) -> set[Product]:
        pass


class TextFilter(ProductFilter):

    _show_null: bool
    _case_sensitive: bool

    def __init__(
        self, value: str, operation: str, inverted: bool, column_name: str,
        show_null: bool, case_sensitive: bool
    ):
        super().__init__(str(value), operation, inverted, column_name)
        self._show_null = show_null
        self._case_sensitive = case_sensitive
        if not self._case_sensitive:
            self._value = self._value.lower()

    def run(self) -> set[Product]:
        attribute = getattr(Product, self._column_name)
        wildcard = '*' if self._case_sensitive else '%'

        if self._operation == 'is':
            products = Product.select().where(
                (
                    attribute == self._value
                    if self._case_sensitive
                    else attribute.ilike(self._value)
                ) != self._inverted
            )
        elif self._operation == 'startswith':
            products = Product.select().where(
                attribute.ilike(f"{self._value}{wildcard}") != self._inverted
            )
        elif self._operation == 'endswith':
            products = Product.select().where(
                attribute.ilike(f"{wildcard}{self._value}") != self._inverted
            )
        elif self._operation == 'contains':
            products = Product.select().where(
                attribute.ilike(
                    f"{wildcard}{self._value}{wildcard}"
                ) != self._inverted
            )

        if self._show_null:
            products = products | Product.select().where(attribute.is_null())

        return set([product for product in products])


class NumberFilter(ProductFilter):

    _show_null: bool

    def __init__(
        self, value: str, operation: str, inverted: bool, column_name: str,
        show_null: bool
    ):
        self._show_null = show_null
        super().__init__(float(value), operation, inverted, column_name)

    def run(self) -> set[Product]:
        attribute = getattr(Product, self._column_name)

        if self._operation == '==':
            products = Product.select().where(
                (attribute == self._value) != self._inverted
            )
        elif self._operation == '!=':
            products = Product.select().where(
                (attribute != self._value) != self._inverted
            )
        elif self._operation == '<':
            products = Product.select().where(
                (attribute < self._value) != self._inverted
            )
        elif self._operation == '<=':
            products = Product.select().where(
                (attribute <= self._value) != self._inverted
            )
        elif self._operation == '>':
            products = Product.select().where(
                (attribute > self._value) != self._inverted
            )
        elif self._operation == '>=':
            products = Product.select().where(
                (attribute >= self._value) != self._inverted
            )

        if self._show_null:
            products = products | Product.select().where(attribute.is_null())

        return set([product for product in products])


class BooleanFilter(ProductFilter):

    _show_null: bool

    def __init__(
        self, value: str, operation: str, inverted: bool, column_name: str,
        show_null: bool
    ):
        self._show_null = show_null
        super().__init__(bool(value), operation, inverted, column_name)

    def run(self) -> set[Product]:
        attribute = getattr(Product, self._column_name)

        products = Product.select().where(
            (attribute != self._inverted)
        )

        if self._show_null:
            products = products | Product.select().where(attribute.is_null())

        return set([product for product in products])


class TagFilter(ProductFilter):

    def __init__(
        self, value: str, operation: str, inverted: bool, column_name: str
    ):
        super().__init__(str(value), operation, inverted, column_name)

    def run(self) -> set[Product]:
        if self._operation == 'has':
            products = (
                Product.select().distinct()
                .join(TagXProduct)
                .join(Tag).where(
                    (Tag.name == self._value) != self._inverted
                )
            )
        elif self._operation == 'has_only':
            products = (
                Product.select().distinct()
                .join(TagXProduct)
                .join(Tag).where(Tag.name == self._value)
                .group_by(Product)
                .having(
                    fn.COUNT(TagXProduct.id_) == 1
                    if not self._inverted
                    else fn.COUNT(TagXProduct.id_) > 1
                )
            )

        return set([product for product in products])


class ColorFilter(ProductFilter):

    def __init__(
        self, value: str, operation: str, inverted: bool, column_name: str
    ):
        super().__init__(str(value), operation, inverted, column_name)

    def run(self) -> set[Product]:
        if self._operation == 'has':
            products = (
                Product.select().distinct()
                .join(ColorXProduct)
                .join(Color).where(
                    (Color.name == self._value) != self._inverted
                )
            )
        elif self._operation == 'has_only':
            products = (
                Product.select().distinct()
                .join(ColorXProduct)
                .join(Color).where(Color.name == self._value)
                .group_by(Product)
                .having(
                    fn.COUNT(ColorXProduct.id_) == 1
                    if not self._inverted
                    else fn.COUNT(ColorXProduct.id_) > 1
                )
            )

        return set([product for product in products])


class ProductFilterEngine:

    COLUMN_NAME_REPLACEMENTS: dict[str, str] = {
        # "name": "short_name"
    }

    _raw_filters: list[dict[str, any]]
    _inverted: bool
    _tokens: list[Token]
    _products: set[Product]

    def __init__(self, raw_filters: list[dict[str, any]], inverted: bool):
        self._raw_filters = raw_filters
        self._inverted = inverted
        self._tokens = []

    def run(self):
        if len(self._raw_filters) == 0:
            self._products = set([product for product in Product.select()])
            return
        self._tokenize(self._raw_filters)
        self._shunting_yard()
        if self._inverted:
            self._tokens.append(OperatorToken(OperatorToken.NOT))
        self._filter_products()

    def _tokenize(
        self, raw_filters: list[dict[str, any]]
    ):
        is_first = True
        for raw_filter in raw_filters:
            if not is_first:
                self._tokens.append(
                    OperatorToken(raw_filter.get('operator', None))
                )
            is_first = False
            raw_filter['columnName'] = self.COLUMN_NAME_REPLACEMENTS.get(
                raw_filter.get('columnName', None),
                raw_filter.get('columnName', None)
            )
            if raw_filter.get('type', None) == 'group':
                if raw_filter.get('inverted', None):
                    self._tokens.append(OperatorToken(OperatorToken.NOT))
                self._tokens.append(ParenthesisToken(ParenthesisToken.OPEN))
                self._tokenize(raw_filter.get('filters', None))
                self._tokens.append(ParenthesisToken(ParenthesisToken.CLOSE))
            elif raw_filter.get('type', None) == 'text':
                self._tokens.append(
                    FilterToken(TextFilter(
                        raw_filter.get('value', None),
                        raw_filter.get('operation', None),
                        raw_filter.get('inverted', None),
                        raw_filter.get('columnName', None),
                        raw_filter.get('showNull', None),
                        raw_filter.get('caseSensitive', None)
                    ))
                )
            elif raw_filter.get('type', None) == 'number':
                self._tokens.append(
                    FilterToken(NumberFilter(
                        raw_filter.get('value', None),
                        raw_filter.get('operation', None),
                        raw_filter.get('inverted', None),
                        raw_filter.get('columnName', None),
                        raw_filter.get('showNull', None)
                    ))
                )
            elif raw_filter.get('type', None) == 'boolean':
                self._tokens.append(
                    FilterToken(BooleanFilter(
                        raw_filter.get('value', None),
                        raw_filter.get('operation', None),
                        raw_filter.get('inverted', None),
                        raw_filter.get('columnName', None),
                        raw_filter.get('showNull', None)
                    ))
                )
            elif raw_filter.get('type', None) == 'tag':
                self._tokens.append(
                    FilterToken(TagFilter(
                        raw_filter.get('value', None),
                        raw_filter.get('operation', None),
                        raw_filter.get('inverted', None),
                        None
                    ))
                )
            elif raw_filter.get('type', None) == 'color':
                self._tokens.append(
                    FilterToken(ColorFilter(
                        raw_filter.get('value', None),
                        raw_filter.get('operation', None),
                        raw_filter.get('inverted', None),
                        None
                    ))
                )

    def _shunting_yard(self):
        token_stack = []
        output_queue = []

        while self._tokens:
            token = self._tokens.pop(0)
            if isinstance(token, FilterToken):
                output_queue.append(token)
            elif isinstance(token, OperatorToken):
                while (
                    token_stack
                    and isinstance(token_stack[-1], OperatorToken)
                    and (
                        token > token_stack[-1]
                        or (
                            token == token_stack[-1]
                            and token != OperatorToken(OperatorToken.NOT)
                        )
                    )
                ):
                    output_queue.append(token_stack.pop())
                token_stack.append(token)
            elif isinstance(token, ParenthesisToken):
                if token.is_open():
                    token_stack.append(token)
                elif token.is_close():
                    while (
                        token_stack
                        and token_stack[-1] != ParenthesisToken(
                            ParenthesisToken.OPEN
                        )
                    ):
                        output_queue.append(token_stack.pop())
                    token_stack.pop()

        while token_stack:
            output_queue.append(token_stack.pop())
        self._tokens = output_queue

    def _filter_products(self):
        token_stack = []
        for token in self._tokens:
            if isinstance(token, FilterToken):
                try:
                    token_stack.append(token.filter_.run())
                except DoesNotExist:
                    token_stack.append(set())
            elif isinstance(token, OperatorToken):
                if token == OperatorToken(OperatorToken.NOT):
                    a = token_stack.pop()
                    token_stack.append(set([
                        p for p in
                        Product.select().where(Product.id_.not_in(a))
                    ]))
                    continue
                b = token_stack.pop()
                a = token_stack.pop()
                if token == OperatorToken(OperatorToken.OR):
                    token_stack.append(a | b)
                elif token == OperatorToken(OperatorToken.AND):
                    token_stack.append(a & b)
        self._products = token_stack.pop()

    @property
    def products(self) -> list[Product]:
        return list(self._products)


if __name__ == "__main__":
    inversed = True
    raw_filters = [{'uuid': '12b67bb6-966a-4f63-a05c-9778be25db84', 'type': 'boolean', 'inverted': False, 'columnName': 'availability', 'showNull': None, 'operator': 'and'}, {'uuid': 'bf4f1c6b-fcc6-4245-8abf-9929d4903566', 'type': 'boolean', 'inverted': False, 'columnName': 'rating', 'showNull': None, 'operator': 'and'}]
    engine = ProductFilterEngine(raw_filters, inversed)
    engine.run()
    print([p.name for p in engine.products])
