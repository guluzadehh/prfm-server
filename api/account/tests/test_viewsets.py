from django.test import TestCase
from django.urls import reverse
from ninja.testing import TestClient

from ..factories import UserFactory
from ..models import User
from ..api import router


class NinjaTestCase(TestCase):
    def __init__(self, method_name: str = "runTest"):
        super().__init__(method_name)
        self.client = TestClient(router)


class LoginAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.password = "parol123"
        self.user = UserFactory.create(password=self.password)

    def test_login(self):
        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"email": self.user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)

    def test_login_without_password(self):
        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"email": self.user.email},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_login_with_empty_password(self):
        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"email": self.user.email, "password": ""},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)

    def test_login_without_email(self):
        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"password": self.password},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_login_with_empty_email(self):
        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"email": "", "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)

    def test_login_with_wrong_email(self):
        WRONG_EMAIL = "test"

        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"email": WRONG_EMAIL, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)

    def test_login_with_wrong_password(self):
        WRONG_EMAIL = "parol"

        res = self.client.post(
            reverse("api-1.0.0:user_login"),
            {"email": WRONG_EMAIL, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 401)


class LogoutAPIView(NinjaTestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_logout(self):
        self.client.force_login(self.user)
        res = self.client.post(reverse("api-1.0.0:user_logout"))
        self.assertEqual(res.status_code, 204)

    def test_logout_unauth(self):
        res = self.client.post(reverse("api-1.0.0:user_logout"))
        self.assertEqual(res.status_code, 401)


class SignUpCreateAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.password = "parol123"
        self.user = UserFactory.build()

    def test_signup(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        user = User.objects.filter(email=self.user.email).first()
        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(res.json()["email"], self.user.email)
        self.assertFalse("details" in res.json())

    def test_signup_without_conf_password(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_signup_empty_conf_password(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": "",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_signup_wrong_conf_password(self):
        WRONG_CONF_PASSWORD = self.password + "123"
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": WRONG_CONF_PASSWORD,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_signup_without_password(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_signup_empty_password(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": "",
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_signup_wrong_password(self):
        SHORT_PASSWORD = "test"
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": SHORT_PASSWORD,
                "conf_password": SHORT_PASSWORD,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("password" in res.json()["details"])

    def test_signup_wrong_email(self):
        WRONG_EMAIL = "test"
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": WRONG_EMAIL,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("email" in res.json()["details"])

    def test_signup_empty_email(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": "",
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("email" in res.json()["details"])

    def test_signup_without_email(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("email" in res.json()["details"])

    def test_signup_without_first_name(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("first_name" in res.json()["details"])

    def test_signup_empty_first_name(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": "",
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("first_name" in res.json()["details"])

    def test_signup_without_last_name(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("last_name" in res.json()["details"])

    def test_signup_empty_last_name(self):
        res = self.client.post(
            reverse("api-1.0.0:user_signup"),
            {
                "email": self.user.email,
                "last_name": "",
                "first_name": self.user.first_name,
                "password": self.password,
                "conf_password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertTrue("last_name" in res.json()["details"])


class IsAuthenticatedAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_is_auth(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("api-1.0.0:is_authenticated"))
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["is_authenticated"])

    def test_is_auth_unauth(self):
        res = self.client.get(reverse("api-1.0.0:is_authenticated"))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["is_authenticated"])


class UserRetrieveUpdateAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_retrieve_user(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("api-1.0.0:user_retrieve"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], self.user.email)

    def test_retrieve_user_unauth(self):
        res = self.client.get(reverse("api-1.0.0:user_retrieve"))
        self.assertEqual(res.status_code, 401)

    def test_update_user_first_name(self):
        NEW_FIRST_NAME = "Frank"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": self.user.email,
                "first_name": NEW_FIRST_NAME,
                "last_name": self.user.last_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            User.objects.filter(pk=self.user.pk).first().first_name, NEW_FIRST_NAME
        )

    def test_update_user_without_first_name(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": self.user.email,
                "last_name": self.user.last_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_update_user_empty_first_name(self):
        NEW_FIRST_NAME = ""
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": self.user.email,
                "first_name": NEW_FIRST_NAME,
                "last_name": self.user.last_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_update_user_last_name(self):
        NEW_LAST_NAME = "Frank"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": self.user.email,
                "last_name": NEW_LAST_NAME,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            User.objects.filter(pk=self.user.pk).first().last_name, NEW_LAST_NAME
        )

    def test_update_user_empty_last_name(self):
        NEW_LAST_NAME = ""
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": self.user.email,
                "last_name": NEW_LAST_NAME,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_update_user_without_last_name(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_update_user_email(self):
        EMAIL = "test@mail.ru"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": EMAIL,
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.filter(pk=self.user.pk).first().email, EMAIL)

    def test_update_user_empty_email(self):
        EMAIL = ""
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": EMAIL,
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_update_user_without_email(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_update_user_wrong_email(self):
        EMAIL = "test"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_update"),
            {
                "email": EMAIL,
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)


class PasswordUpdateAPIViewTest(NinjaTestCase):
    def setUp(self):
        self.old_password = "parol123"
        self.new_password = "parol1234"
        self.user = UserFactory.create(password=self.old_password)

    def test_password_update(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 200)
        self.assertTrue(
            User.objects.filter(pk=self.user.pk)
            .first()
            .check_password(self.new_password)
        )

    def test_password_update_unauth(self):
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 403)

    def test_password_update_wrong_old_password(self):
        WRONG_PASSWORD = "wrong_password"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": WRONG_PASSWORD,
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 409)
        self.assertTrue("old_password" in res.json()["details"])

    def test_password_update_empty_old_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": "",
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 409)
        self.assertTrue("old_password" in res.json()["details"])

    def test_password_update_without_old_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 409)
        self.assertTrue("old_password" in res.json()["details"])

    def test_update_password_wrong_new_password(self):
        SHORT_PASSWORD = "test"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": SHORT_PASSWORD,
                "conf_password": SHORT_PASSWORD,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 400)
        self.assertTrue("new_password" in res.json()["details"])

    def test_update_password_empty_new_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": "",
                "conf_password": self.old_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 400)
        self.assertTrue("new_password" in res.json()["details"])

    def test_update_password_without_new_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "conf_password": self.old_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 400)
        self.assertTrue("new_password" in res.json()["details"])

    def test_update_password_wrong_conf_password(self):
        WRONG_CONF_PASSWORD = self.new_password + "123"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": WRONG_CONF_PASSWORD,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 400)
        self.assertTrue("conf_password" in res.json()["details"])

    def test_update_password_empty_conf_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": "",
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 400)
        self.assertTrue("conf_password" in res.json()["details"])

    def test_update_password_without_conf_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("api-1.0.0:user_password_update"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
            },
            content_type="application/json",
        )
        self.assertTrue(res.status_code, 400)
        self.assertTrue("conf_password" in res.json()["details"])
