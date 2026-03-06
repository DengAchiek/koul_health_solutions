from django.contrib import admin
from .models import (
    BlogPost,
    ClinicLocation,
    HomeMetric,
    OrderRequest,
    PatientResource,
    Product,
    ScreeningBooking,
    ServiceOffering,
    SiteSettings,
    Testimonial,
)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "is_featured", "created_at")
    list_filter = ("is_featured", "rating")
    search_fields = ("name", "role_or_title", "quote")


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "product", "quantity", "delivery_option", "status", "created_at")
    list_filter = ("status", "delivery_option")
    search_fields = ("full_name", "phone", "email", "notes")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price_kes", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ScreeningBooking)
class ScreeningBookingAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "preferred_date", "preferred_time", "related_product", "created_at")
    list_filter = ("preferred_date",)
    search_fields = ("full_name", "phone", "email", "interest", "notes")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_phone", "contact_email", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ServiceOffering)
class ServiceOfferingAdmin(admin.ModelAdmin):
    list_display = ("title", "cta_name", "is_active", "is_featured_home", "display_order")
    list_filter = ("is_active", "is_featured_home", "cta_name")
    search_fields = ("title", "description")
    ordering = ("display_order", "title")


@admin.register(ClinicLocation)
class ClinicLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "hours", "is_active", "is_featured_home", "display_order")
    list_filter = ("is_active", "is_featured_home")
    search_fields = ("name", "address", "phone", "whatsapp", "services_text")
    ordering = ("display_order", "name")


@admin.register(PatientResource)
class PatientResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "url_name", "label", "is_active", "display_order")
    list_filter = ("is_active", "url_name")
    search_fields = ("title", "description", "label")
    ordering = ("display_order", "title")


@admin.register(HomeMetric)
class HomeMetricAdmin(admin.ModelAdmin):
    list_display = ("value", "title", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("value", "title", "description")
    ordering = ("display_order", "title")
