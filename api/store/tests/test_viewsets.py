from ninja.testing import TestClient
from django.test import TestCase
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
from ..api import router


class NinjaTestCase(TestCase):
    def __init__(self, method_name: str = "runTest"):
        super().__init__(method_name)
        self.client = TestClient(router_or_app=router)


class BrandListAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.brands = BrandFactory.create_batch(5)

    def test_brand_list(self):
        res = self.client.get(reverse("api-1.0.0:brand_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), len(self.brands))


class GroupListAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.groups = GroupFactory.create_batch(5)

    def test_group_list(self):
        res = self.client.get(reverse("api-1.0.0:group_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), len(self.groups))


# @override_settings(
#     REST_FRAMEWORK={
#         "DEFAULT_AUTHENTICATION_CLASSES": [
#             "rest_framework.authentication.SessionAuthentication",
#         ],
#         "PAGE_SIZE": 1000,
#     }
# )
class ProductListAPIView(NinjaTestCase):
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
        res = self.client.get(reverse("api-1.0.0:product_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], len(self.products * 5))

    def test_product_list_single_brand_filter(self):
        brand = self.brands[0]
        res = self.client.get(reverse("api-1.0.0:product_list"), {"brands": brand.slug})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], self.PRODUCTS_SIZE_PER_BRAND * 1)

    def test_product_list_multiple_brand_filter(self):
        filter_brands_size = 3
        brands = self.brands[:filter_brands_size]
        res = self.client.get(
            reverse("api-1.0.0:product_list"),
            [("brands", brand.slug) for brand in brands],
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json()["count"], self.PRODUCTS_SIZE_PER_BRAND * filter_brands_size
        )

    def test_product_list_groups_filter(self):
        groups_used_times = 5
        for group in self.groups:
            res = self.client.get(
                reverse("api-1.0.0:product_list"),
                {"groups": group.slug},
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(
                res.json()["count"], self.PRODUCTS_SIZE_PER_BRAND * groups_used_times
            )
            groups_used_times -= 1

    def test_product_list_gender_filter(self):
        res = self.client.get(reverse("api-1.0.0:product_list"), {"gender": "M"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json()["count"], Product.objects.filter(gender="M").count()
        )

    def test_product_list_season_filter(self):
        res = self.client.get(reverse("api-1.0.0:product_list"), {"season": "AW"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.json()["count"], Product.objects.filter(season="AW").count()
        )


class ProductRetrieveAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.product = ProductFactory.create()

    def test_product_detail(self):
        res = self.client.get(self.product.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["slug"], self.product.slug)


class FavoriteListAPIViewTest(NinjaTestCase):
    USER_FAVORITES_SIZE = 2

    def setUp(self):
        self.user = UserFactory.create()
        self.favorites = FavoriteFactory.create_batch(
            self.USER_FAVORITES_SIZE, user=self.user
        )
        FavoriteFactory.create_batch(3)

    def test_favorites_list(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("api-1.0.0:favorite_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), self.USER_FAVORITES_SIZE)

    def test_favorites_list_unauth(self):
        res = self.client.get(reverse("api-1.0.0:favorite_list"))
        self.assertEqual(res.status_code, 401)


class FavoriteCreateAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_favorite_create(self):
        self.client.force_login(self.user)
        product = ProductFactory.create()
        res = self.client.post(
            reverse("api-1.0.0:favorite_list"),
            {"product_id": product.id},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(
            Favorite.objects.filter(user=self.user, product=product).exists()
        )

    def test_favorite_create_empty(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:favorite_list"), {}, content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_favorite_create_not_existing_product(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:favorite_list"),
            {"product_id": 1},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 422)

    def test_favorite_create_already_existing_product(self):
        self.client.force_login(self.user)
        favorite = FavoriteFactory.create(user=self.user)
        res = self.client.post(
            reverse("api-1.0.0:favorite_list"),
            {"product_id": favorite.product.id},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 409)

    def test_favorite_create_unauth(self):
        product = ProductFactory.create()
        res = self.client.post(
            reverse("api-1.0.0:favorite_list"),
            {"product_id": product.id},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)


class FavoriteDestroyAPIViewTest(NinjaTestCase):
    USER_FAVORITES_SIZE = 2

    def setUp(self):
        self.user = UserFactory.create()
        self.favorites = FavoriteFactory.create_batch(
            self.USER_FAVORITES_SIZE, user=self.user
        )
        FavoriteFactory.create_batch(3)

    def test_favorite_destroy(self):
        self.client.force_login(self.user)
        favorite_id = self.favorites[0].id
        res = self.client.delete(
            reverse("api-1.0.0:favorite_destroy", kwargs={"favorite_id": favorite_id})
        )
        self.assertEqual(res.status_code, 204)
        self.assertFalse(Favorite.objects.filter(id=favorite_id).exists())

    def test_favorite_destroy_another(self):
        self.client.force_login(self.user)
        favorite = FavoriteFactory.create()
        res = self.client.delete(
            reverse(
                "api-1.0.0:favorite_destroy",
                kwargs={"favorite_id": favorite.id},
            )
        )
        self.assertEqual(res.status_code, 404)

    def test_favorite_destroy_unauth(self):
        res = self.client.delete(
            reverse(
                "api-1.0.0:favorite_destroy",
                kwargs={"favorite_id": self.favorites[0].id},
            )
        )
        self.assertEqual(res.status_code, 401)


class OrderListAPIView(NinjaTestCase):
    USER_ORDER_SIZE = 2

    def setUp(self):
        self.user = UserFactory.create()
        self.order = OrderFactory.create_batch(self.USER_ORDER_SIZE, user=self.user)
        OrderFactory.create_batch(3)

    def test_order_list(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("api-1.0.0:order_list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), self.USER_ORDER_SIZE)

    def test_order_list_unauth(self):
        res = self.client.get(reverse("api-1.0.0:order_list"))
        self.assertEqual(res.status_code, 401)


class OrderCreateAPIView(NinjaTestCase):
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
        self.user = UserFactory.create()

    def test_order_create(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": self.items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 201)
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
            reverse("api-1.0.0:order_list"),
            {},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_order_create_empty_phone(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"address": self.address, "items": self.items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_order_create_empty_address(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "items": self.items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_order_create_empty_items(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_order_create_empty_items_list(self):
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": []},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_order_create_unauth(self):
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": self.items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)

    def test_order_create_wrong_size(self):
        self.client.force_login(self.user)
        WRONG_SIZE = 45
        items = [
            {
                "product_id": ProductFactory.create().id,
                "size": WRONG_SIZE,
                "quantity": 1,
            }
        ]
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_order_create_wrong_qty(self):
        self.client.force_login(self.user)
        WRONG_QUANTITY = 29
        items = [
            {
                "product_id": ProductFactory.create().id,
                "size": 15,
                "quantity": WRONG_QUANTITY,
            }
        ]
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_order_create_unexisting_product(self):
        self.client.force_login(self.user)
        WRONG_PRODUCT_ID = 2142
        items = [
            {
                "product_id": WRONG_PRODUCT_ID,
                "size": 15,
                "quantity": 1,
            }
        ]
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 422)

    def test_order_create_repeating_products(self):
        self.client.force_login(self.user)
        product = ProductFactory.create()
        items = [
            {
                "product_id": product.id,
                "size": 15,
                "quantity": 1,
            },
            {
                "product_id": product.id,
                "size": 15,
                "quantity": 4,
            },
        ]
        res = self.client.post(
            reverse("api-1.0.0:order_list"),
            {"phone": self.phone, "address": self.address, "items": items},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
