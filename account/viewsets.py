from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    LoginSerializer,
    UserSerializer,
    UserPasswordEditSerializer,
    SignUpSerializer,
)
from .models import User
from .filters import CurrentUserFilter


class UserProfileMixin:
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset)
        self.check_object_permissions(self.request, obj)
        return obj


class UserRetrieveUpdateAPIView(UserProfileMixin, RetrieveUpdateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = [CurrentUserFilter]


class PasswordUpdateAPIView(UserProfileMixin, UpdateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserPasswordEditSerializer
    queryset = User.objects.all()
    filter_backends = [CurrentUserFilter]


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request, username=email, password=password)
        if user is None:
            raise AuthenticationFailed

        login(request, user)
        return Response(status=status.HTTP_200_OK)


class SignUpCreateAPIView(CreateAPIView):
    serializer_class = SignUpSerializer


class LogoutAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class IsAuthenticatedAPIView(APIView):
    def get(self, request):
        return Response({"is_authenticated": request.user.is_authenticated})
