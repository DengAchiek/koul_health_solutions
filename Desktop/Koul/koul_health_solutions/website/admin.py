from django.contrib import admin
from .models import (
    AboutMedia,
    BlogPost,
    ClinicLocation,
    HomeMetric,
    OrderRequest,
    PatientResource,
    Product,
    ProductMedia,
    ScreeningBooking,
    ServiceOffering,
    ServiceMedia,
    SiteSettings,
    Testimonial,
    TestimonialMedia,
)


class ProductMediaInline(admin.StackedInline):
    model = ProductMedia
    extra = 1
    fields = ("title", "alt_text", "media_type", "file", "is_primary", "display_order", "preview_tag")
    readonly_fields = ("preview_tag",)


class TestimonialMediaInline(admin.StackedInline):
    model = TestimonialMedia
    extra = 1
    fields = ("title", "alt_text", "media_type", "file", "is_primary", "display_order", "preview_tag")
    readonly_fields = ("preview_tag",)


class ServiceMediaInline(admin.StackedInline):
    model = ServiceMedia
    extra = 1
    fields = ("title", "alt_text", "media_type", "file", "is_primary", "display_order", "preview_tag")
    readonly_fields = ("preview_tag",)


class AboutMediaInline(admin.StackedInline):
    model = AboutMedia
    extra = 1
    fields = ("title", "alt_text", "media_type", "file", "is_primary", "display_order", "preview_tag")
    readonly_fields = ("preview_tag",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("preview_tag",)
    fields = ("title", "slug", "featured_image", "preview_tag", "excerpt", "content", "is_published", "published_at")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "is_featured", "created_at")
    list_filter = ("is_featured", "rating")
    search_fields = ("name", "role_or_title", "quote")
    inlines = [TestimonialMediaInline]


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
    inlines = [ProductMediaInline]


@admin.register(ScreeningBooking)
class ScreeningBookingAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "preferred_date", "preferred_time", "related_product", "created_at")
    list_filter = ("preferred_date",)
    search_fields = ("full_name", "phone", "email", "interest", "notes")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_phone", "contact_email", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [AboutMediaInline]

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
    inlines = [ServiceMediaInline]


@admin.register(ClinicLocation)
class ClinicLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "hours", "is_active", "is_featured_home", "display_order")
    list_filter = ("is_active", "is_featured_home")
    search_fields = ("name", "address", "phone", "whatsapp", "services_text")
    ordering = ("display_order", "name")
    readonly_fields = ("preview_tag",)
    fields = (
        "name",
        "featured_image",
        "preview_tag",
        "address",
        "phone",
        "whatsapp",
        "hours",
        "maps_url",
        "services_text",
        "is_active",
        "is_featured_home",
        "display_order",
    )


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
    readonly_fields = ("preview_tag",)
    fields = ("value", "title", "featured_image", "preview_tag", "description", "is_active", "display_order")
