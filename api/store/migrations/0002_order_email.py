# Generated by Django 5.0.4 on 2024-05-03 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.EmailField(default="quluzade.resul13@mail.ru", max_length=254),
            preserve_default=False,
        ),
    ]
