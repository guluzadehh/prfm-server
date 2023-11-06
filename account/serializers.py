from rest_framework import serializers
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "get_full_name")
        read_only_fields = ("get_full_name",)


class UserPasswordEditSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    old_password = serializers.CharField(
        trim_whitespace=False, max_length=128, write_only=True
    )
    new_password = serializers.CharField(
        trim_whitespace=False, max_length=128, write_only=True
    )
    conf_password = serializers.CharField(
        trim_whitespace=False, max_length=128, write_only=True
    )

    class Meta:
        model = User
        fields = ("old_password", "conf_password", "new_password", "user")

    def validate(self, attrs):
        user = attrs.get("user")
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        conf_password = attrs.get("conf_password")

        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Wrong old password"})

        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        if conf_password is None or new_password != conf_password:
            raise serializers.ValidationError(
                {"conf_password": "Passwords do not match"}
            )

        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data["new_password"]
        instance.set_password(new_password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)  # skip email correctness validation
    password = serializers.CharField(
        trim_whitespace=False, max_length=128, write_only=True
    )


class SignUpSerializer(serializers.ModelSerializer):
    conf_password = serializers.CharField(
        trim_whitespace=False, max_length=128, write_only=True
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password", "conf_password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password = attrs["password"]
        conf_password = attrs.get("conf_password")

        try:
            password_validation.validate_password(password, None)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        if conf_password is None or password != conf_password:
            raise serializers.ValidationError(
                {"conf_password": "Passwords do not match"}
            )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("conf_password", None)
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user
