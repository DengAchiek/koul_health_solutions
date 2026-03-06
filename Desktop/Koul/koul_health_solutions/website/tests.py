from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import BlogPost, Product


class PublicRoutesTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Immune Support",
            short_description="Daily supplement",
            description="Supports general wellness.",
            is_active=True,
        )
        self.post = BlogPost.objects.create(
            title="Healthy Habits",
            excerpt="Small changes matter.",
            content="Eat well, sleep well, and move daily.",
            is_published=True,
        )

    def test_static_and_listing_pages_return_200(self):
        names = [
            "home",
            "about",
            "services",
            "locations",
            "patient_resources",
            "contact",
            "products",
            "book_screening",
            "blog",
            "testimonials",
            "order_request",
        ]
        for name in names:
            with self.subTest(route=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_product_detail_route_returns_200(self):
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_route_returns_200(self):
        response = self.client.get(reverse("blog_detail", args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)


class AdminAccountSettingsTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.staff_user = self.user_model.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="OldPass123!",
            is_staff=True,
        )
        self.url = reverse("admin_account_settings")

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_staff_can_open_settings_page(self):
        self.client.login(username="adminuser", password="OldPass123!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_staff_can_update_username_and_email(self):
        self.client.login(username="adminuser", password="OldPass123!")
        response = self.client.post(
            self.url,
            {
                "action": "profile",
                "profile-username": "newadmin",
                "profile-email": "newadmin@example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.username, "newadmin")
        self.assertEqual(self.staff_user.email, "newadmin@example.com")

    def test_staff_can_change_password(self):
        self.client.login(username="adminuser", password="OldPass123!")
        response = self.client.post(
            self.url,
            {
                "action": "password",
                "password-old_password": "OldPass123!",
                "password-new_password1": "NewPass12345!",
                "password-new_password2": "NewPass12345!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.staff_user.refresh_from_db()
        self.assertTrue(self.staff_user.check_password("NewPass12345!"))
