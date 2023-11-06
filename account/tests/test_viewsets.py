from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from ..factories import UserFactory
from ..models import User


class LoginAPIViewTest(APITestCase):
    def setUp(self):
        self.password = "parol123"
        self.user = UserFactory(password=self.password)

    def test_login(self):
        res = self.client.post(
            reverse("account:login"),
            {"email": self.user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_without_password(self):
        res = self.client.post(
            reverse("account:login"),
            {"email": self.user.email},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_password(self):
        res = self.client.post(
            reverse("account:login"),
            {"email": self.user.email, "password": ""},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_without_email(self):
        res = self.client.post(
            reverse("account:login"),
            {"password": self.password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_email(self):
        res = self.client.post(
            reverse("account:login"),
            {"email": "", "password": self.password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_email(self):
        WRONG_EMAIL = "test"

        res = self.client.post(
            reverse("account:login"),
            {"email": WRONG_EMAIL, "password": self.password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_with_wrong_password(self):
        WRONG_EMAIL = "parol"

        res = self.client.post(
            reverse("account:login"),
            {"email": WRONG_EMAIL, "password": self.password},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class LogoutAPIView(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_logout(self):
        self.client.force_login(self.user)
        res = self.client.post(reverse("account:logout"))
        self.assertEqual(res.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_unauth(self):
        res = self.client.post(reverse("account:logout"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class SignUpCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.password = "parol123"
        self.user = UserFactory.build()

    def test_signup(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        user = User.objects.filter(email=self.user.email).first()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(res.data["email"], self.user.email)
        self.assertFalse("password" in res.data)
        self.assertFalse("conf_password" in res.data)

    def test_signup_without_conf_password(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_empty_conf_password(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": "",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_wrong_conf_password(self):
        WRONG_CONF_PASSWORD = self.password + "123"
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": WRONG_CONF_PASSWORD,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_without_password(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_empty_password(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": "",
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_wrong_password(self):
        SHORT_PASSWORD = "test"
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": SHORT_PASSWORD,
                "conf_password": SHORT_PASSWORD,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("password" in res.data)

    def test_signup_wrong_email(self):
        WRONG_EMAIL = "test"
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": WRONG_EMAIL,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in res.data)

    def test_signup_empty_email(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": "",
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in res.data)

    def test_signup_without_email(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("email" in res.data)

    def test_signup_without_first_name(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("first_name" in res.data)

    def test_signup_empty_first_name(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": "",
                "last_name": self.user.last_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("first_name" in res.data)

    def test_signup_without_last_name(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("last_name" in res.data)

    def test_signup_empty_last_name(self):
        res = self.client.post(
            reverse("account:signup"),
            {
                "email": self.user.email,
                "last_name": "",
                "first_name": self.user.first_name,
                "password": self.password,
                "conf_password": self.password,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("last_name" in res.data)


class IsAuthenticatedAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_is_auth(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("account:is-authenticated"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_authenticated"])

    def test_is_auth_unauth(self):
        res = self.client.get(reverse("account:is-authenticated"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_authenticated"])


class UserRetrieveUpdateAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_retrieve_user(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("account:user-detail"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)

    def test_retrieve_user_unauth(self):
        res = self.client.get(reverse("account:user-detail"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_first_name(self):
        NEW_FIRST_NAME = "Frank"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": self.user.email,
                "first_name": NEW_FIRST_NAME,
                "last_name": self.user.last_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            User.objects.filter(pk=self.user.pk).first().first_name, NEW_FIRST_NAME
        )

    def test_update_user_without_first_name(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": self.user.email,
                "last_name": self.user.last_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_empty_first_name(self):
        NEW_FIRST_NAME = ""
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": self.user.email,
                "first_name": NEW_FIRST_NAME,
                "last_name": self.user.last_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_last_name(self):
        NEW_LAST_NAME = "Frank"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": self.user.email,
                "last_name": NEW_LAST_NAME,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            User.objects.filter(pk=self.user.pk).first().last_name, NEW_LAST_NAME
        )

    def test_update_user_empty_last_name(self):
        NEW_LAST_NAME = ""
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": self.user.email,
                "last_name": NEW_LAST_NAME,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_without_last_name(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_email(self):
        EMAIL = "test@mail.ru"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": EMAIL,
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(pk=self.user.pk).first().email, EMAIL)

    def test_update_user_empty_email(self):
        EMAIL = ""
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": EMAIL,
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_without_email(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_wrong_email(self):
        EMAIL = "test"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:user-detail"),
            {
                "email": EMAIL,
                "last_name": self.user.last_name,
                "first_name": self.user.first_name,
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordUpdateAPIViewTest(APITestCase):
    def setUp(self):
        self.old_password = "parol123"
        self.new_password = "parol1234"
        self.user = UserFactory(password=self.old_password)

    def test_password_update(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            User.objects.filter(pk=self.user.pk)
            .first()
            .check_password(self.new_password)
        )
        self.assertFalse("old_password" in res.data)
        self.assertFalse("new_password" in res.data)
        self.assertFalse("conf_password" in res.data)

    def test_password_update_unauth(self):
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_update_wrong_old_password(self):
        WRONG_PASSWORD = "wrong_password"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": WRONG_PASSWORD,
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("old_password" in res.data)

    def test_password_update_empty_old_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": "",
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("old_password" in res.data)

    def test_password_update_without_old_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "new_password": self.new_password,
                "conf_password": self.new_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("old_password" in res.data)

    def test_update_password_wrong_new_password(self):
        SHORT_PASSWORD = "test"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": SHORT_PASSWORD,
                "conf_password": SHORT_PASSWORD,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("new_password" in res.data)

    def test_update_password_empty_new_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": "",
                "conf_password": self.old_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("new_password" in res.data)

    def test_update_password_without_new_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "conf_password": self.old_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("new_password" in res.data)

    def test_update_password_wrong_conf_password(self):
        WRONG_CONF_PASSWORD = self.new_password + "123"
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": WRONG_CONF_PASSWORD,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("conf_password" in res.data)

    def test_update_password_empty_conf_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
                "conf_password": "",
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("conf_password" in res.data)

    def test_update_password_without_conf_password(self):
        self.client.force_login(self.user)
        res = self.client.put(
            reverse("account:change-password"),
            {
                "old_password": self.old_password,
                "new_password": self.new_password,
            },
        )
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("conf_password" in res.data)
