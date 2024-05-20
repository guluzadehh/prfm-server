from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
import email_validator
from ninja import Field
from ninja.schema import Schema
from django.utils.translation import gettext_lazy as _
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

        assert len(fn) <= MAX_FIRST_NAME_LENGTH, _(
            "The first name cannot exceed %(max_length)d characters."
        ) % {"max_length": MAX_FIRST_NAME_LENGTH}

        assert len(fn) >= MIN_FIRST_NAME_LENGTH, _(
            _("The first name must be at least %(min_length)d characters long.")
            % {"min_length": MIN_FIRST_NAME_LENGTH}
        )

        return fn

    @field_validator("last_name")
    def validate_last_name(cls, ln):
        MAX_LAST_NAME_LENGTH = 50
        MIN_LAST_NAME_LENGTH = 2

        assert len(ln) <= MAX_LAST_NAME_LENGTH, _(
            _("The last name cannot exceed %(max_length)d characters.")
            % {"max_length": MAX_LAST_NAME_LENGTH}
        )

        assert len(ln) >= MIN_LAST_NAME_LENGTH, _(
            _("The last name must be at least %(min_length)d characters long.")
            % {"min_length": MIN_LAST_NAME_LENGTH}
        )

        return ln

    @field_validator("email")
    def validate_email(cls, e):
        MAX_EMAIL_LENGTH = 254

        assert len(e) <= MAX_EMAIL_LENGTH, _(
            _("The email length cannot exceed %(max_length)d characters.")
            % {"max_length": MAX_EMAIL_LENGTH}
        )

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
            raise ValueError(_("".join(e.messages)))


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
            raise ValueError(_("\n".join(e.messages)))
