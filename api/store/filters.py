from enum import Enum
from typing import List
from ninja import Field, FilterSchema
from django.db.models import Q


class GenderEnum(Enum):
    MALE = "M"
    FEMALE = "F"
    UNISEX = "U"


class SeasonEnum(Enum):
    AW = "AW"
    SS = "SS"
    ALL = "ALL"


class ProductFilter(FilterSchema):
    search: str = Field(None, q=["name__icontains", "brand__name__icontains"])
    gender: GenderEnum = Field(None)
    brands: List[str] = Field(None, q=["brand__slug__in"])
    groups: List[str] = Field(None, q=["groups__slug__in"])
    season: SeasonEnum = Field(None)

    def filter_gender(self, gender: GenderEnum) -> Q:
        if gender == GenderEnum.MALE:
            return Q(gender="M")
        elif gender == GenderEnum.FEMALE:
            return Q(gender="F")

        return Q()

    def filter_season(self, season: SeasonEnum) -> Q:
        if season is None or season == SeasonEnum.ALL:
            return Q()

        return Q(season=season.value)
