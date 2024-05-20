from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import Field, Schema
from phonenumber_field.validators import validate_international_phonenumber
from pydantic import ValidationInfo, field_validator
from django.utils.translation import gettext_lazy as _

from .models import Product


class BrandOutSchema(Schema):
    id: int
    name: str
    slug: str


class GroupOutSchema(Schema):
    id: int
    name: str
    slug: str


class ProductOutSchema(Schema):
    brand: BrandOutSchema

    id: int
    name: str
    slug: str

    gender: str
    season: str

    price_per_gram: Decimal
    prices: Dict[int, Decimal]

    display_name: str

    detail_url: str = Field(alias="get_absolute_url")
    favorite_id: Optional[int] = None


class ProductListOutSchema(Schema):
    data: List[ProductOutSchema]
    count: int
    next: Optional[int]
    previous: Optional[int]


class FavoriteOutSchema(Schema):
    id: int
    product: ProductOutSchema


class FavoriteInSchema(Schema):
    product_id: int


class OrderItemOutSchema(Schema):
    id: int
    product_id: int
    product: ProductOutSchema
    size: int
    quantity: int
    price: Decimal


class OrderOutSchema(Schema):
    id: int
    items: List[OrderItemOutSchema]
    email: str
    phone: str
    address: str
    commentary: Optional[str] = None
    completed: bool
    ordered_at: datetime
    price: Decimal

    @staticmethod
    def resolve_phone(obj):
        return str(obj.phone.as_international)


class OrderItemInSchema(Schema):
    product_id: int
    size: int
    quantity: int

    @field_validator("size")
    def validate_size(cls, v, info: ValidationInfo):
        assert v in Product.SIZES, _(
            _("Wrong %(field_name)s format") % {"field_name": info.field_name}
        )
        return v

    @field_validator("quantity")
    def validate_quantity(cls, q, info: ValidationInfo):
        assert q >= 1 and q <= 10, _(
            _("The %(field_name)s value must be between 1 and 10")
            % {"field_name": info.field_name}
        )
        return q


class OrderInSchema(Schema):
    phone: str
    address: str
    commentary: Optional[str] = None
    items: List[OrderItemInSchema]

    @field_validator("items")
    def validate_items(cls, items, info: ValidationInfo):
        assert len(items) > 0, _("%(field_name)s can't be empty") % {
            "field_name": info.field_name
        }

        variants = list(
            map(lambda item: str(item.product_id) + "_" + str(item.size), items)
        )

        assert len(variants) == len(set(variants)), _(
            _("%(field_name)s cannot contain duplicate products")
            % {"field_name": info.field_name}
        )

        return items

    @field_validator("phone")
    def validate_phone(cls, p):
        try:
            validate_international_phonenumber(p)
            return p
        except DjangoValidationError as e:
            raise ValueError(_(e.message))
