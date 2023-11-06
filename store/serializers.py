from rest_framework import serializers
from .models import Brand, Group, Product, Favorite, Order, OrderItem
from account.serializers import UserSerializer
from .signals import order_created


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name", "slug")


class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer()
    detail_url = serializers.URLField(source="get_absolute_url")
    favorite_id = serializers.IntegerField(default=None)

    class Meta:
        model = Product
        fields = (
            "id",
            "brand",
            "display_name",
            "name",
            "slug",
            "price_per_gram",
            "prices",
            "detail_url",
            "favorite_id",
        )


class ProductSerializer(ProductListSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    gender = serializers.CharField(source="get_gender_display")
    season = serializers.CharField(source="get_season_display")

    class Meta:
        model = ProductListSerializer.Meta.model
        fields = ProductListSerializer.Meta.fields + (
            "groups",
            "gender",
            "season",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = serializers.SerializerMethodField(required=False, read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "product_id", "product", "user"]
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(), fields=["product_id", "user"]
            )
        ]

    def get_product(self, obj):
        product = obj.product
        product.favorite_id = obj.id
        return ProductListSerializer(instance=product).data

    def create(self, validated_data):
        product_id = validated_data["product_id"]
        user = validated_data["user"]

        if not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError("Product doesn't exist")

        return Favorite.objects.create(product_id=product_id, user=user)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(required=False)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "size", "quantity", "price"]
        read_only_fields = ("price", "product")

    def validate_size(self, size):
        if size not in Product.SIZES:
            raise serializers.ValidationError("Wrong size")

        return size

    def validate_quantity(self, qty):
        if qty < 1 or qty > 10:
            raise serializers.ValidationError("Wrong quantity")

        return qty


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "phone",
            "address",
            "commentary",
            "completed",
            "ordered_at",
            "price",
            "items",
        ]
        read_only_fields = ("user", "completed", "ordered_at")

    def validate_items(self, items):
        if len(items) == 0:
            raise serializers.ValidationError("Empty items")

        for item in items:
            OrderItemSerializer(data=item).is_valid(raise_exception=True)

        return items

    def create(self, validated_data):
        user = validated_data["user"]
        phone = validated_data["phone"]
        address = validated_data["address"]
        commentary = validated_data.get("commentary")
        order = Order.objects.create(
            user=user, phone=phone, address=address, commentary=commentary
        )

        for item in validated_data["items"]:
            product_id = item["product_id"]
            size = item["size"]
            quantity = item["quantity"]

            if not Product.objects.filter(id=product_id).exists():
                order.delete()
                raise serializers.ValidationError

            OrderItem.objects.create(
                order=order, product_id=product_id, size=size, quantity=quantity
            )

        order = Order.objects.prefetch_def(user).get(id=order.id)  # type: ignore
        order_created.send(Order, order=order)

        return order
