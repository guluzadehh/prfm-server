import factory
from factory.faker import faker
from factory.fuzzy import FuzzyChoice
from datetime import datetime
from account.factories import UserFactory
from .models import Brand, Group, Product, Favorite, Order, OrderItem

faker = faker.Faker("az_AZ")


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = faker.text(max_nb_chars=20)
    slug = factory.Sequence(lambda n: "slug%d" % n)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = faker.text(max_nb_chars=20)
    slug = factory.Sequence(lambda n: "slug%d" % n)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    brand = factory.SubFactory(BrandFactory)
    name = faker.text(max_nb_chars=20)
    slug = factory.Sequence(lambda n: "slug%d" % n)
    price_per_gram = faker.pydecimal(left_digits=2, right_digits=2, positive=True)
    gender = factory.Sequence(lambda n: Product.GENDERS[n % 3][0])
    season = factory.Sequence(lambda n: Product.SEASONS[n % 2][0])

    @factory.post_generation
    def groups(self, create, extracted):
        if not create or not extracted:
            return

        self.groups.add(*extracted)  # type: ignore


class FavoriteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Favorite

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    phone = faker.cellphone_number()
    address = faker.address()
    completed = False
    ordered_at = factory.LazyFunction(datetime.now)

    @factory.post_generation
    def items(self, create, extracted):
        if not create or not extracted:
            return

        self.items.add(*extracted)  # type: ignore


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem
        exclude = ("sizes",)

    order = factory.SubFactory(OrderFactory)
    sizes = [15, 30, 50]
    product = factory.SubFactory(ProductFactory)
    quantity = faker.random_number(digits=1)

    @factory.lazy_attribute_sequence
    def size(self, n):
        return self.sizes[n % 3]
