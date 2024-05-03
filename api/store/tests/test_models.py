from django.test import TestCase
from ..factories import ProductFactory, OrderItemFactory, OrderFactory, FavoriteFactory


class ProductModelTest(TestCase):
    def setUp(self):
        self.product = ProductFactory()

    def test_product_str_func(self):
        expected = f"{self.product.brand} {self.product.name}"
        self.assertEquals(str(self.product), expected)

    def test_product_prices(self):
        expectings = {
            15: self.product.price_per_gram * 15,
            30: self.product.price_per_gram * 30,
            50: self.product.price_per_gram * 50,
        }

        for key, val in expectings.items():
            expected = expectings[key]
            self.assertEquals(self.product.prices[key], expected)  # type: ignore

    def test_product_absolute_url(self):
        expected = f"/api/products/{self.product.brand.slug}_{self.product.slug}"  # type: ignore
        self.assertEquals(self.product.get_absolute_url(), expected)  # type: ignore


# class FavoriteTest(TestCase):
#     def setUp(self):
#         self.favorite = FavoriteFactory.create()

#     def test_favorite_absolute_url(self):
#         expected = f"/api/favorites/{self.favorite.id}/"
#         self.assertEquals(self.favorite.get_absolute_url(), expected)


# class OrderItemTest(TestCase):
#     def setUp(self):
#         self.item = OrderItemFactory()

#     def test_order_item_price(self):
#         expected = (
#             self.item.product.price_per_gram * self.item.size * self.item.quantity  # type: ignore
#         )
#         self.assertEquals(self.item.price, expected)  # type: ignore


# class OrderTest(TestCase):
#     def setUp(self):
#         self.order = OrderFactory()

#     def test_order_price(self):
#         price = 0

#         for item in self.order.items.all():  # type: ignore
#             price += item.price

#         expected = price
#         self.assertEquals(self.order.price, expected)  # type: ignore

#     def test_order_complete(self):
#         self.order.complete()  # type: ignore
#         expected = True
#         self.assertTrue(self.order.completed)
