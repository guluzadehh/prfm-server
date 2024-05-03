from django.http import HttpRequest
from ninja.security import django_auth
from asgiref.sync import sync_to_async


async def adjango_auth(request: HttpRequest):
    return await sync_to_async(django_auth)(request)
