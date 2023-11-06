from rest_framework.filters import BaseFilterBackend


class ProductFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        brands = request.query_params.getlist("brands", [])
        if len(brands) > 0:
            queryset = queryset.filter(brand__slug__in=brands)

        groups = request.query_params.getlist("groups", [])
        if len(groups) > 0:
            queryset = queryset.filter(groups__slug__in=groups)

        gender = request.query_params.get("gender", None)
        if gender and gender.upper() != "U":
            queryset = queryset.filter(gender=gender.upper())

        season = request.query_params.get("season", None)
        if season and season != "all":
            queryset = queryset.filter(season=season)

        return queryset


class BelongsToUserFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)
