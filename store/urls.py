from django.urls import path
from .viewsets import (
    BrandListAPIView,
    GroupListAPIView,
    ProductListAPIView,
    ProductRetrieveAPIView,
    ProductsCountGenericAPIView,
    FavoriteListAPIView,
    FavoriteDestroyAPIView,
    OrderListCreateAPIView,
)

app_name = "store"

urlpatterns = [
    path("brands/", BrandListAPIView.as_view(), name="brand-list"),
    path("groups/", GroupListAPIView.as_view(), name="group-list"),
    path("products/", ProductListAPIView.as_view(), name="product-list"),
    path(
        "products/count/", ProductsCountGenericAPIView.as_view(), name="products-count"
    ),
    path(
        "products/<str:brand_and_name>/",
        ProductRetrieveAPIView.as_view(),
        name="product-detail",
    ),
    path("favorites/", FavoriteListAPIView.as_view(), name="favorite-list"),
    path(
        "favorites/<int:pk>/", FavoriteDestroyAPIView.as_view(), name="favorite-detail"
    ),
    path("orders/", OrderListCreateAPIView.as_view(), name="order-list"),
]
