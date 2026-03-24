from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import AboutMedia, BlogPost, ClinicLocation, HomeMetric, Product, ProductMedia, ServiceMedia, ServiceOffering, SiteSettings, Testimonial, TestimonialMedia


class PublicRoutesTests(TestCase):
    def setUp(self):
        self.site_settings = SiteSettings.objects.first()
        self.product = Product.objects.create(
            name="Immune Support",
            short_description="Daily supplement",
            description="Supports general wellness.",
            is_active=True,
        )
        ProductMedia.objects.create(
            product=self.product,
            media_type="image",
            file="products/immune-support.jpg",
            is_primary=True,
        )
        self.post = BlogPost.objects.create(
            title="Healthy Habits",
            featured_image="blog/healthy-habits.jpg",
            excerpt="Small changes matter.",
            content="Eat well, sleep well, and move daily.",
            is_published=True,
        )
        self.location = ClinicLocation.objects.create(
            name="Nairobi Main Clinic",
            featured_image="locations/nairobi-main.jpg",
            address="JKUAT Towers, Kenyatta Avenue, Nairobi",
            phone="+254 795 225 892",
            whatsapp="+254 784 768 933",
            hours="Mon-Sat: 8:00am - 6:00pm",
            maps_url="https://maps.google.com/?q=JKUAT+Towers+Kenyatta+Avenue+Nairobi",
            services_text="Screening\nConsultation",
            is_active=True,
            is_featured_home=True,
        )
        self.metric = HomeMetric.objects.create(
            value="96%",
            title="Client confidence",
            featured_image="metrics/client-confidence.jpg",
            description="Clients trust our wellness support.",
            is_active=True,
        )
        self.service = ServiceOffering.objects.create(
            title="Preventive Screening",
            description="Proactive care support.",
            cta_name="book_screening",
            is_active=True,
        )
        ServiceMedia.objects.create(
            service=self.service,
            media_type="video",
            file="services/preventive-screening.mp4",
            is_primary=True,
        )
        self.testimonial = Testimonial.objects.create(
            name="Jane Doe",
            role_or_title="Client",
            quote="Helpful and clear guidance.",
            rating=5,
            is_featured=True,
        )
        TestimonialMedia.objects.create(
            testimonial=self.testimonial,
            media_type="image",
            file="testimonials/jane-doe.jpg",
            is_primary=True,
        )
        if self.site_settings:
            AboutMedia.objects.create(
                site_settings=self.site_settings,
                media_type="image",
                file="about/clinic-team.jpg",
                is_primary=True,
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
