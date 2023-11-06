from django.urls import path
from .viewsets import (
    LoginAPIView,
    SignUpCreateAPIView,
    UserRetrieveUpdateAPIView,
    PasswordUpdateAPIView,
    IsAuthenticatedAPIView,
    LogoutAPIView,
)

app_name = "account"

urlpatterns = [
    path("", UserRetrieveUpdateAPIView.as_view(), name="user-detail"),
    path("change-password", PasswordUpdateAPIView.as_view(), name="change-password"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("signup/", SignUpCreateAPIView.as_view(), name="signup"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("isauth/", IsAuthenticatedAPIView.as_view(), name="is-authenticated"),
]
