from django.contrib import admin
from account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "get_full_name"]
