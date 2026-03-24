from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .forms import AdminProfileForm, OrderRequestForm, ScreeningBookingForm
from .models import (
    BlogPost,
    ClinicLocation,
    HomeMetric,
    PatientResource,
    Product,
    ServiceOffering,
    SiteSettings,
    Testimonial,
)


def _get_site_name():
    settings = SiteSettings.objects.first()
    return settings.site_name if settings else "Kuol Health Solutions"


def _is_staff_user(user):
    return user.is_authenticated and user.is_staff


def home(request):
    featured_products = Product.objects.filter(is_active=True).prefetch_related("media_items")[:3]
    featured_posts = BlogPost.objects.filter(is_published=True)[:3]
    featured_testimonials = Testimonial.objects.filter(is_featured=True).prefetch_related("media_items")[:3]

    featured_services = ServiceOffering.objects.filter(is_active=True, is_featured_home=True).prefetch_related("media_items")[:4]
    if not featured_services:
        featured_services = ServiceOffering.objects.filter(is_active=True).prefetch_related("media_items")[:4]

    home_metrics = HomeMetric.objects.filter(is_active=True)[:4]

    featured_locations = ClinicLocation.objects.filter(is_active=True, is_featured_home=True)[:2]
    if not featured_locations:
        featured_locations = ClinicLocation.objects.filter(is_active=True)[:2]

    patient_resources = PatientResource.objects.filter(is_active=True)[:4]

    return render(
        request,
        "home.html",
        {
            "featured_products": featured_products,
            "featured_posts": featured_posts,
            "featured_testimonials": featured_testimonials,
            "featured_services": featured_services,
            "home_metrics": home_metrics,
            "locations": featured_locations,
            "patient_resources": patient_resources,
        },
    )


def about(request):
    service_groups = ServiceOffering.objects.filter(is_active=True)[:4]
    primary_location = ClinicLocation.objects.filter(is_active=True).first()
    site_settings = SiteSettings.objects.first()
    return render(
        request,
        "about.html",
        {
            "service_groups": service_groups,
            "primary_location": primary_location,
            "about_media": site_settings.about_media.all() if site_settings else [],
        },
    )


def contact(request):
    locations = ClinicLocation.objects.filter(is_active=True)[:3]
    return render(request, "contact.html", {"locations": locations})


def services(request):
    service_groups = ServiceOffering.objects.filter(is_active=True).prefetch_related("media_items")
    return render(request, "services.html", {"service_groups": service_groups})


def locations(request):
    locations_data = ClinicLocation.objects.filter(is_active=True)
    return render(request, "locations.html", {"locations": locations_data})


def patient_resources(request):
    resources = PatientResource.objects.filter(is_active=True)
    return render(request, "patient_resources.html", {"resources": resources})


@login_required
@user_passes_test(_is_staff_user, login_url="admin:login")
def admin_account_settings(request):
    profile_success = False
    password_success = False

    profile_form = AdminProfileForm(instance=request.user, prefix="profile")
    password_form = PasswordChangeForm(user=request.user, prefix="password")

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()

        if action == "profile":
            profile_form = AdminProfileForm(request.POST, instance=request.user, prefix="profile")
            if profile_form.is_valid():
                profile_form.save()
                profile_success = True

        elif action == "password":
            password_form = PasswordChangeForm(user=request.user, data=request.POST, prefix="password")
            if password_form.is_valid():
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
                password_success = True
                password_form = PasswordChangeForm(user=request.user, prefix="password")

    return render(
        request,
        "admin_account_settings.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
            "profile_success": profile_success,
            "password_success": password_success,
        },
    )


def products(request):
    q = (request.GET.get("q") or "").strip()
    qs = Product.objects.filter(is_active=True).prefetch_related("media_items")

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(short_description__icontains=q) | Q(description__icontains=q))

    return render(request, "products.html", {"products": qs})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related("media_items"), slug=slug, is_active=True)
    return render(request, "product_detail.html", {"product": product})


def book_screening(request):
    selected_product = None
    product_slug = (request.GET.get("product") or "").strip()
    if product_slug:
        selected_product = Product.objects.filter(slug=product_slug, is_active=True).first()

    success = False

    if request.method == "POST":
        form = ScreeningBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if selected_product:
                booking.related_product = selected_product
            booking.save()
            success = True
            form = ScreeningBookingForm()
    else:
        form = ScreeningBookingForm()

    return render(
        request,
        "book_screening.html",
        {"form": form, "success": success, "selected_product": selected_product},
    )


def blog(request):
    posts = BlogPost.objects.filter(is_published=True)
    return render(request, "blog.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "blog_detail.html", {"post": post})


def testimonials(request):
    items = Testimonial.objects.filter(is_featured=True).prefetch_related("media_items")
    return render(request, "testimonials.html", {"testimonials": items})


def order_request(request):
    selected_product = None
    slug = (request.GET.get("product") or "").strip()
    if slug:
        selected_product = Product.objects.filter(slug=slug, is_active=True).first()

    settings = SiteSettings.objects.first()
    whatsapp_digits = settings.whatsapp_digits if settings else "254784768933"

    success = False
    whatsapp_message = None

    if request.method == "POST":
        form = OrderRequestForm(request.POST)
        if form.is_valid():
            order = form.save()
            success = True

            product_name = order.product.name if order.product else "Not specified"
            whatsapp_message = (
                f"Hello {_get_site_name()}, I would like to place an order.\\n\\n"
                f"Name: {order.full_name}\\n"
                f"Phone: {order.phone}\\n"
                f"Product: {product_name}\\n"
                f"Quantity: {order.quantity}\\n"
                f"Delivery: {order.get_delivery_option_display()}\\n"
                f"Location: {order.delivery_location or 'N/A'}\\n"
                f"Notes: {order.notes or 'N/A'}\\n"
            )

            form = OrderRequestForm(initial={"product": selected_product} if selected_product else None)
    else:
        initial = {"product": selected_product} if selected_product else None
        form = OrderRequestForm(initial=initial)

    return render(
        request,
        "order_request.html",
        {
            "form": form,
            "success": success,
            "selected_product": selected_product,
            "whatsapp_message": whatsapp_message,
            "wa_phone_digits": whatsapp_digits,
        },
    )
