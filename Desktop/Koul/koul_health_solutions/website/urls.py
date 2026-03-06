from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("locations/", views.locations, name="locations"),
    path("patient-resources/", views.patient_resources, name="patient_resources"),
    path("admin-account/", views.admin_account_settings, name="admin_account_settings"),
    path("contact/", views.contact, name="contact"),

    path("supplements/", views.products, name="products"),
    path("supplements/<slug:slug>/", views.product_detail, name="product_detail"),

    path("book-screening/", views.book_screening, name="book_screening"),

    # NEW
    path("health-education/", views.blog, name="blog"),
    path("health-education/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("testimonials/", views.testimonials, name="testimonials"),
    path("order/", views.order_request, name="order_request"),
]
