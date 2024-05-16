from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
import email_validator
from ninja import Field
from ninja.schema import Schema

# from ninja.errors import ValidationError
from pydantic import (
    field_validator,
)


class UserOutSchema(Schema):
    email: str
    first_name: str
    last_name: str
    get_full_name: str


class LoginSchema(Schema):
    email: str
    password: str


class UserInSchema(Schema):
    email: str = Field(max_length=254)
    first_name: str
    last_name: str

    @field_validator("first_name")
    def validate_first_name(cls, fn):
        MAX_FIRST_NAME_LENGTH = 50
        MIN_FIRST_NAME_LENGTH = 2

        assert (
            len(fn) <= MAX_FIRST_NAME_LENGTH
        ), f"First name must not exceed {MAX_FIRST_NAME_LENGTH} characters"

        assert (
            len(fn) >= MIN_FIRST_NAME_LENGTH
        ), f"First name should have at least {MIN_FIRST_NAME_LENGTH} characters"

        return fn

    @field_validator("last_name")
    def validate_last_name(cls, ln):
        MAX_LAST_NAME_LENGTH = 50
        MIN_LAST_NAME_LENGTH = 2

        assert (
            len(ln) <= MAX_LAST_NAME_LENGTH
        ), f"First name must not exceed {MAX_LAST_NAME_LENGTH} characters"

        assert (
            len(ln) >= MIN_LAST_NAME_LENGTH
        ), f"First name should have at least {MIN_LAST_NAME_LENGTH} characters"

        return ln

    @field_validator("email")
    def validate_email(cls, e):
        MAX_EMAIL_LENGTH = 254

        assert (
            len(e) <= MAX_EMAIL_LENGTH
        ), f"Email length must not exceed {MAX_EMAIL_LENGTH} characters"

        try:
            email_validator.validate_email(e)
        except email_validator.EmailNotValidError as e:
            raise ValueError(str(e.args[0]))

        return e


class SignUpSchema(UserInSchema):
    password: str
    conf_password: str

    @field_validator("password")
    def validate_password(cls, p):
        try:
            password_validation.validate_password(p)
            return p
        except DjangoValidationError as e:
            raise ValueError("".join(e.messages))


class PasswordUpdateSchema(Schema):
    old_password: str
    new_password: str
    conf_password: str

    @field_validator("new_password")
    def validate_password(cls, p):
        try:
            password_validation.validate_password(p)
            return p
        except DjangoValidationError as e:
            raise ValueError("\n".join(e.messages))
