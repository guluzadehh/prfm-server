from django.db.models import (
    Manager,
    QuerySet,
    Prefetch,
    OuterRef,
    Value,
    Subquery,
    BooleanField,
)
from django.apps import apps
from django.db.models.query import QuerySet


class ProductQuerySet(QuerySet):
    def with_favorite(self, user=None):
        favorite = apps.get_model("store", "Favorite")

        return self.annotate(
            favorite_id=(
                Subquery(
                    favorite.objects.values_list("id", flat=True).filter(
                        product=OuterRef("id"), user=user
                    )[:1]
                )
                if (user and user.is_authenticated)
                else Value(None, output_field=BooleanField())
            )
        )


class ProductManager(Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db).select_related("brand")


class OrderQuerySet(QuerySet):
    def prefetch_def(self, user):
        order_item = apps.get_model("store", "OrderItem")
        product = apps.get_model("store", "Product")
        return self.prefetch_related(
            Prefetch(
                "items",
                queryset=order_item.objects.prefetch_related(
                    Prefetch(
                        "product",
                        queryset=product.objects.all().with_favorite(user),  # type: ignore
                    )
                ),
            )
        )
