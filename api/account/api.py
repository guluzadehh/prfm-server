from typing import Dict
from django.http import HttpRequest
from django.contrib.auth import aauthenticate, alogin, alogout
from ninja import Router
from ninja.errors import AuthenticationError

from account.models import User

from .helpers import adjango_auth
from .schemas import *

router = Router()


@router.get("/isauth")
async def is_authenticated(request: HttpRequest):
    user = await request.auser()
    return {"is_authenticated": user.is_authenticated}


@router.get("/", auth=adjango_auth, response=UserOutSchema)
async def user_retrieve(request: HttpRequest):
    user = await request.auser()
    return user


@router.post("/login/")
async def user_login(request: HttpRequest, details: LoginSchema):
    user = await aauthenticate(
        request=request, username=details.email, password=details.password
    )

    if user is None:
        raise AuthenticationError

    await alogin(request, user)

    return 200


@router.post("/logout/", auth=adjango_auth, response={204: None})
async def user_logout(request: HttpRequest):
    await alogout(request)
    return 204, None


@router.post("/signup/", response={201: UserOutSchema, 409: Dict, 400: Dict})
async def user_signup(request: HttpRequest, details: SignUpSchema):
    if details.conf_password != details.password:
        return 400, {"details": {"conf_password": "Passwords must match"}}

    if await User.objects.filter(email=details.email).aexists():
        return 409, {
            "details": {
                "email": "Email is already taken",
            }
        }

    user = User(
        email=details.email, first_name=details.first_name, last_name=details.last_name
    )
    user.set_password(details.password)
    await user.asave()
    return 201, user


@router.put("/", auth=adjango_auth, response={200: UserOutSchema, 409: Dict})
async def user_update(request: HttpRequest, details: UserInSchema):
    user = await request.auser()

    if (
        user.email != details.email
        and await User.objects.filter(email=details.email).aexists()
    ):
        return 409, {
            "details": {
                "email": "Email is already taken",
            }
        }

    user.email = details.email
    user.first_name = details.first_name
    user.last_name = details.last_name

    await user.asave()

    return 200, user


@router.put(
    "/change-password/",
    auth=adjango_auth,
    response={200: UserOutSchema, 409: Dict, 400: Dict},
)
async def user_password_update(request: HttpRequest, details: PasswordUpdateSchema):
    if details.conf_password != details.new_password:
        return 400, {"details": {"conf_password": "Passwords must match"}}

    user = await request.auser()

    if not user.check_password(details.old_password):
        return 409, {
            "details": {"old_password": "Wrong old password"},
        }

    user.set_password(details.new_password)
    await user.asave()

    return user
