import factory
from factory.faker import faker
from .models import User

faker = faker.Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@gmail.com")
    first_name = faker.first_name()
    last_name = faker.last_name()
    password = factory.django.Password("parol123")
