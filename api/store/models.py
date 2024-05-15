from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from account.models import User
from .managers import OrderQuerySet, ProductManager


class Brand(models.Model):
    class Meta:
        verbose_name = "Brend"
        verbose_name_plural = "Brendlər"

    name = models.CharField("Ad", max_length=120)
    slug = models.SlugField(max_length=130, unique=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    class Meta:
        verbose_name = "Qrup"
        verbose_name_plural = "Qruplar"

    name = models.CharField("Ad", max_length=120)
    slug = models.SlugField(max_length=130, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        verbose_name = "Ətir"
        verbose_name_plural = "Ətirlər"

    objects = ProductManager()

    GENDERS = [
        ("M", "Kişi"),
        ("F", "Qadın"),
        ("U", "Unisex"),
    ]

    SEASONS = [("AW", "Payız/Qış"), ("SS", "Yaz/Yay")]
    SIZES = [15, 30, 50]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    groups = models.ManyToManyField(Group, related_name="products")
    name = models.CharField("Ad", max_length=120)
    slug = models.SlugField(max_length=130, unique=True)
    price_per_gram = models.DecimalField(
        "Qiymət 1 qram",
        max_digits=4,
        decimal_places=2,
    )
    gender = models.CharField("Cins", max_length=1, choices=GENDERS, default="U")
    season = models.CharField("Fəsil", max_length=2, choices=SEASONS)
    sales = models.PositiveIntegerField("Satış sayı", default=0)

    def __str__(self):
        return f"{self.brand} {self.name}"

    @property
    def prices(self):
        return {
            15: self.price_per_gram * 15,
            30: self.price_per_gram * 30,
            50: self.price_per_gram * 50,
        }

    @property
    def display_name(self):
        return str(self)

    def get_absolute_url(self):
        return reverse(
            "api-1.0.0:product_detail",
            kwargs={"brand_slug": self.brand.slug, "product_slug": self.slug},
        )


class Favorite(models.Model):
    class Meta:
        verbose_name = "Seçilmiş"
        verbose_name_plural = "Seçilmişlər"
        unique_together = (("product", "user"),)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # def get_absolute_url(self):
    #     return reverse("api-1.0.0:favorite_detail", kwargs={"pk": self.pk})


class Order(models.Model):
    class Meta:
        verbose_name = "Sifariş"
        verbose_name_plural = "Sifarişlər"

    objects = OrderQuerySet.as_manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    email = models.EmailField()
    phone = PhoneNumberField()
    address = models.TextField("ünvan")
    commentary = models.TextField("rəy", null=True, blank=True)
    completed = models.BooleanField("çatdırılıb", default=False)
    ordered_at = models.DateTimeField("sifariş tarixi", auto_now_add=True)

    def complete(self):
        if self.completed:
            return

        self.completed = True
        self.save()

        products = [item.product for item in self.items.select_related("product").all()]

        for product in products:
            product.sales += 1

        Product.objects.bulk_update(products, ["sales"])

    @property
    def price(self):
        price = 0

        for item in self.items.all():  # type: ignore
            price += item.price

        return price


class OrderItem(models.Model):
    class Meta:
        verbose_name = "Sifariş məhsulu"
        verbose_name_plural = "Sifariş məhsulları"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.PositiveSmallIntegerField("ölçü")  # Olculere diqqet
    quantity = models.PositiveSmallIntegerField(
        "miqdar", validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    @property
    def price(self):
        return self.product.price_per_gram * self.size * self.quantity
