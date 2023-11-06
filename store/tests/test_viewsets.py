from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from django.urls import reverse
from ..factories import (
    BrandFactory,
    GroupFactory,
    ProductFactory,
    FavoriteFactory,
    OrderFactory,
)
from ..models import Favorite, Order, OrderItem, Product
from account.factories import UserFactory


class BrandListAPIViewTest(APITestCase):
    def setUp(self):
        self.brands = BrandFactory.create_batch(5)

    def test_brand_list(self):
        res = self.client.get(reverse("store:brand-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(self.brands))


class GroupListAPIViewTest(APITestCase):
    def setUp(self):
        self.groups = GroupFactory.create_batch(5)

    def test_group_list(self):
        res = self.client.get(reverse("store:group-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(self.groups))


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "PAGE_SIZE": 1000,
    }
)
class ProductListAPIView(APITestCase):
    BRANDS_SIZE = 5
    GROUPS_SIZE = 5
    PRODUCTS_SIZE_PER_BRAND = 5
    PRODUCTS_SIZE = PRODUCTS_SIZE_PER_BRAND * 5

    def setUp(self):
        self.brands = BrandFactory.create_batch(self.BRANDS_SIZE)
        self.groups = GroupFactory.create_batch(self.GROUPS_SIZE)
        self.products = [
            ProductFactory.create_batch(
                self.PRODUCTS_SIZE_PER_BRAND,
                groups=self.groups[: (i + 1)],
                brand=self.brands[i],
            )
            for i in range(0, self.BRANDS_SIZE)
        ]

    def test_product_list(self):
        res = self.client.get(reverse("store:product-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], len(self.products * 5))

    def test_product_list_single_brand_filter(self):
        brand = self.brands[0]
        res = self.client.get(reverse("store:product-list"), {"brands": brand.slug})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], self.PRODUCTS_SIZE_PER_BRAND * 1)

    def test_product_list_multiple_brand_filter(self):
        filter_brands_size = 3
        brands = self.brands[:filter_brands_size]
        res = self.client.get(
            reverse("store:product-list"), [("brands", brand.slug) for brand in brands]
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["count"], self.PRODUCTS_SIZE_PER_BRAND * filter_brands_size
        )

    def test_product_list_groups_filter(self):
        groups_used_times = 5
        for group in self.groups:
            res = self.client.get(
                reverse("store:product-list"),
                {"groups": group.slug},
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(
                res.data["count"], self.PRODUCTS_SIZE_PER_BRAND * groups_used_times
            )
            groups_used_times -= 1

    def test_product_list_gender_filter(self):
        res = self.client.get(reverse("store:product-list"), {"gender": "m"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], Product.objects.filter(gender="M").count())

    def test_product_list_season_filter(self):
        res = self.client.get(reverse("store:product-list"), {"season": "AW"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], Product.objects.filter(season="AW").count())


class ProductRetrieveAPIViewTest(APITestCase):
    def setUp(self):
        self.product = ProductFactory()

    def test_product_detail(self):
        res = self.client.get(self.product.get_absolute_url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["slug"], self.product.slug)


class FavoriteListAPIViewTest(APITestCase):
    USER_FAVORITES_SIZE = 2

    def setUp(self):
        self.user = UserFactory()
        self.favorites = FavoriteFactory.create_batch(
            self.USER_FAVORITES_SIZE, user=self.user
        )
        FavoriteFactory.create_batch(3)

    def test_favorites_list(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("store:favorite-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), self.USER_FAVORITES_SIZE)

    def test_favorites_list_unauth(self):
        res = self.client.get(reverse("store:favorite-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class FavoriteCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_favorite_create(self):
        self.client.force_login(self.user)
        product = ProductFactory()
        res = self.client.post(
            reverse("store:favorite-list"), {"product_id": product.id}
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Favorite.objects.filter(user=self.user, product=product).exists()
        )

    def test_favorite_create_empty(self):
        self.client.force_login(self.user)
        res = self.client.post(reverse("store:favorite-list"), {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_create_not_existing_product(self):
        self.client.force_login(self.user)
        res = self.client.post(reverse("store:favorite-list"), {"product_id": 1})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_create_already_existing_product(self):
        self.client.force_login(self.user)
        favorite = FavoriteFactory(user=self.user)
        res = self.client.post(
            reverse("store:favorite-list"), {"product_id": favorite.product.id}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_create_unauth(self):
        product = ProductFactory()
        res = self.client.post(
            reverse("store:favorite-list"), {"product_id": product.id}
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class FavoriteDestroyAPIViewTest(APITestCase):
    USER_FAVORITES_SIZE = 2

    def setUp(self):
        self.user = UserFactory()
        self.favorites = FavoriteFactory.create_batch(
            self.USER_FAVORITES_SIZE, user=self.user
        )
        FavoriteFactory.create_batch(3)

    def test_favorite_destroy(self):
        self.client.force_login(self.user)
        favorite_id = self.favorites[0].id
        res = self.client.delete(self.favorites[0].get_absolute_url())
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(id=favorite_id).exists())

    def test_favorite_destroy_another(self):
        self.client.force_login(self.user)
        favorite = FavoriteFactory()
        res = self.client.delete(favorite.get_absolute_url())
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite_destroy_unauth(self):
        favorite = FavoriteFactory()
        res = self.client.delete(favorite.get_absolute_url())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class OrderListAPIView(APITestCase):
    USER_ORDER_SIZE = 2

    def setUp(self):
        self.user = UserFactory()
        self.order = OrderFactory.create_batch(self.USER_ORDER_SIZE, user=self.user)
        OrderFactory.create_batch(3)

    def test_order_list(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("store:order-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), self.USER_ORDER_SIZE)

    def test_order_list_unauth(self):
        res = self.client.get(reverse("store:order-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class OrderCreateAPIView(APITestCase):
    ORDER_PRODUCT_SIZE = 3

    def setUp(self):
        self.phone = "+994504448899"
        self.address = "Baki seheri, Narimanov r."
        self.products = ProductFactory.create_batch(self.ORDER_PRODUCT_SIZE)
        self.items = [
            {
                "product_id": product.id,
                "size": 15,
                "quantity": 1,
            }
            for product in self.products
        ]
        self.user = UserFactory()

    def test_order_create(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("store:order-list"),
            {"phone": self.phone, "address": self.address, "items": self.items},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Order.objects.filter(
                user=self.user, phone=self.phone, address=self.address
            ).exists()
        )

        order_items = OrderItem.objects.filter(order__user=self.user)

        for i, item in enumerate(order_items):
            self.assertTrue(item.product.id, self.items[i]["product_id"])
            self.assertTrue(item.quantity, self.items[i]["quantity"])
            self.assertTrue(item.size, self.items[i]["size"])

    def test_order_create_empty(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("store:order-list"),
            {},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_create_empty_phone(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("store:order-list"),
            {"address": self.address, "items": self.items},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_create_empty_address(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("store:order-list"),
            {"phone": self.phone, "items": self.items},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_create_empty_items(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("store:order-list"),
            {"phone": self.phone, "address": self.address},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_order_create_unauth(self):
        res = self.client.post(
            reverse("store:order-list"),
            {"phone": self.phone, "address": self.address, "items": self.items},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_create_wrong_size(self):
        self.client.force_login(self.user)
        WRONG_SIZE = 45
        items = [
            {
                "product_id": ProductFactory().id,
                "size": WRONG_SIZE,
                "quantity": 1,
            }
        ]
        res = self.client.post(
            reverse("store:order-list"),
            {"phone": self.phone, "address": self.address, "items": items},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_create_wrong_qty(self):
        self.client.force_login(self.user)
        WRONG_QUANTITY = 29
        items = [
            {
                "product_id": ProductFactory().id,
                "size": 15,
                "quantity": WRONG_QUANTITY,
            }
        ]
        res = self.client.post(
            reverse("store:order-list"),
            {"phone": self.phone, "address": self.address, "items": items},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
