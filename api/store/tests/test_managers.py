from django.test import TestCase
from ..factories import FavoriteFactory
from ..models import Product


class ProductManagerTest(TestCase):
    def test_product_with_favorite_exists(self):
        favorite = FavoriteFactory.create()
        expected = favorite.id

        product = (
            Product.objects.filter(id=favorite.product.id)
            .with_favorite(favorite.user)
            .first()
        )
        self.assertEquals(product.favorite_id, expected)
