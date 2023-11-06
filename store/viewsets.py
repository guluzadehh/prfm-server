from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    GenericAPIView,
    ListCreateAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from .models import Brand, Group, Product, Favorite, Order, OrderItem
from .serializers import (
    BrandSerializer,
    GroupSerializer,
    ProductListSerializer,
    ProductSerializer,
    FavoriteSerializer,
    OrderSerializer,
)
from .filters import ProductFilter, BelongsToUserFilter
from .pagination import CustomPagination


class BrandListAPIView(ListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()


class GroupListAPIView(ListAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    ordering_fields = ["name", "price_per_gram"]
    filter_backends = [OrderingFilter, SearchFilter, ProductFilter]
    search_fields = ["brand__name", "name"]
    queryset = Product.objects.all().distinct()
    pagination_class = CustomPagination

    def paginate_queryset(self, queryset):
        if self.request.query_params.get("omit_page", False):
            return None
        return super().paginate_queryset(queryset)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_favorite(self.request.user)
            .order_by("brand__name")
        )


class ProductsCountGenericAPIView(GenericAPIView):
    filter_backends = [SearchFilter, ProductFilter]
    search_fields = ["brand__name", "name"]
    queryset = Product.objects.all().distinct()

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response({"count": queryset.count()})


class ProductRetrieveAPIView(RetrieveAPIView):
    lookup_url_kwarg = "brand_and_name"
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.prefetch_related("groups").with_favorite(  # type: ignore
            self.request.user
        )

    def get_object(self):
        brand_and_name = self.kwargs[self.lookup_url_kwarg].split("_")
        brand = brand_and_name[0]
        name = brand_and_name[1]
        obj = get_object_or_404(self.get_queryset(), brand__slug=brand, slug=name)
        return obj


class FavoriteListAPIView(ListCreateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [BelongsToUserFilter]
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.select_related("product", "product__brand").all()


class FavoriteDestroyAPIView(DestroyAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [BelongsToUserFilter]
    queryset = Favorite.objects.all()


class OrderListCreateAPIView(ListCreateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [BelongsToUserFilter]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_def(self.request.user)
            .order_by("-ordered_at")
        )
