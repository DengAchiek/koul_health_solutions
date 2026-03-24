from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import format_html
from django.utils.text import slugify

MEDIA_TYPE_CHOICES = [
    ("image", "Image"),
    ("video", "Video"),
]

MEDIA_FILE_VALIDATOR = FileExtensionValidator(
    allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov", "m4v", "ogg"]
)
IMAGE_FILE_VALIDATOR = FileExtensionValidator(
    allowed_extensions=["jpg", "jpeg", "png", "webp", "gif"]
)


def media_upload_to(instance, filename):
    return f"{instance.media_directory}/{filename}"


class MediaAssetBase(models.Model):
    title = models.CharField(max_length=120, blank=True)
    alt_text = models.CharField(max_length=180, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default="image")
    file = models.FileField(upload_to=media_upload_to, validators=[MEDIA_FILE_VALIDATOR])
    is_primary = models.BooleanField(
        default=False,
        help_text="Use this as the main image/video for cards and previews.",
    )
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["display_order", "created_at"]

    @property
    def is_image(self):
        return self.media_type == "image"

    @property
    def is_video(self):
        return self.media_type == "video"

    def preview_tag(self):
        if not self.file:
            return "No media uploaded"
        if self.is_image:
            return format_html(
                '<img src="{}" alt="{}" style="width:120px;height:90px;object-fit:cover;border-radius:10px;" />',
                self.file.url,
                self.alt_text or self.title or "Preview",
            )
        return format_html(
            '<video src="{}" style="width:160px;height:90px;border-radius:10px;" controls preload="metadata"></video>',
            self.file.url,
        )

    preview_tag.short_description = "Preview"


def single_image_preview(file_field, alt_text="Preview"):
    if not file_field:
        return "No image uploaded"
    return format_html(
        '<img src="{}" alt="{}" style="width:120px;height:90px;object-fit:cover;border-radius:10px;" />',
        file_field.url,
        alt_text,
    )


class Product(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    short_description = models.CharField(max_length=220)
    description = models.TextField()
    price_kes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            i = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def primary_media(self):
        prefetched = getattr(self, "_prefetched_objects_cache", {}).get("media_items")
        if prefetched is not None:
            for item in prefetched:
                if item.is_primary:
                    return item
            return prefetched[0] if prefetched else None
        return self.media_items.filter(is_primary=True).first() or self.media_items.first()

    def __str__(self):
        return self.name


class ScreeningBooking(models.Model):
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    interest = models.CharField(max_length=180)
    notes = models.TextField(blank=True)

    related_product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.preferred_date}"


class BlogPost(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=190, unique=True, blank=True)
    featured_image = models.FileField(
        upload_to="blog",
        blank=True,
        validators=[IMAGE_FILE_VALIDATOR],
    )
    excerpt = models.CharField(max_length=260)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            i = 2
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def preview_tag(self):
        return single_image_preview(self.featured_image, self.title)

    preview_tag.short_description = "Preview"

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role_or_title = models.CharField(max_length=120, blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    @property
    def primary_media(self):
        prefetched = getattr(self, "_prefetched_objects_cache", {}).get("media_items")
        if prefetched is not None:
            for item in prefetched:
                if item.is_primary:
                    return item
            return prefetched[0] if prefetched else None
        return self.media_items.filter(is_primary=True).first() or self.media_items.first()

    def __str__(self):
        return f"{self.name} ({self.rating}/5)"


class OrderRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("invoiced", "Invoiced"),
        ("paid", "Paid"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    ]

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    delivery_option = models.CharField(
        max_length=40,
        choices=[("pickup", "Pickup (Nairobi facility)"), ("delivery", "Delivery")],
        default="pickup",
    )
    delivery_location = models.CharField(max_length=180, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OrderRequest: {self.full_name} x{self.quantity}"


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="Kuol Health Solutions")
    meta_description = models.CharField(
        max_length=255,
        default="Preventive care, wellness screening, and natural supplement guidance in Nairobi.",
    )
    hero_background_image = models.FileField(
        upload_to="site",
        blank=True,
        validators=[IMAGE_FILE_VALIDATOR],
        help_text="Optional hero background image shown on the home page.",
    )
    utility_location_label = models.CharField(max_length=120, default="Nairobi Main Clinic")
    utility_hours = models.CharField(max_length=120, default="Mon-Sat 8:00am - 6:00pm")
    contact_phone = models.CharField(max_length=30, default="+254 795 225 892")
    contact_whatsapp = models.CharField(max_length=30, default="+254 784 768 933")
    contact_email = models.EmailField(default="KuolHealthsolutions@gmail.com")
    facility_address = models.CharField(max_length=180, default="JKUAT Towers, Kenyatta Avenue, Nairobi")
    footer_summary = models.TextField(
        default=(
            "Preventive healthcare support through screening, education, and natural supplement guidance. "
            "We help individuals take practical steps toward healthier living."
        )
    )
    home_hero_badge = models.CharField(max_length=120, default="Trusted Preventive Care in Kenya")
    home_hero_title = models.CharField(
        max_length=220,
        default="Better health starts with early screening and guided daily choices.",
    )
    home_hero_description = models.TextField(
        default=(
            "Kuol Health Solutions combines preventive screening, practical consultation, and natural "
            "supplement guidance to support individuals managing chronic and lifestyle conditions."
        )
    )
    about_heading = models.CharField(max_length=150, default="About Kuol Health Solutions")
    about_intro = models.TextField(
        default="A preventive health and wellness organization supporting chronic and lifestyle condition management."
    )
    about_body = models.TextField(
        default=(
            "We provide natural supplements designed to support the body, strengthen immunity, and promote "
            "long-term wellness through early intervention and practical guidance."
        )
    )
    mission_statement = models.TextField(
        default=(
            "To promote preventive healthcare and support chronic and lifestyle condition management through "
            "certified natural supplements, screening, and continuous health education."
        )
    )
    vision_statement = models.TextField(
        default=(
            "To become a trusted leader in preventive health and wellness, empowering communities to live "
            "healthier and more productive lives through natural and science-supported solutions."
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def clean(self):
        if SiteSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Only one Site Settings record is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk and SiteSettings.objects.exists():
            self.pk = SiteSettings.objects.first().pk
        super().save(*args, **kwargs)

    @staticmethod
    def _digits_only(value):
        return "".join(ch for ch in (value or "") if ch.isdigit())

    @property
    def phone_link(self):
        digits = self._digits_only(self.contact_phone)
        return f"tel:+{digits}" if digits else "#"

    @property
    def whatsapp_link(self):
        digits = self._digits_only(self.contact_whatsapp)
        return f"https://wa.me/{digits}" if digits else "#"

    @property
    def whatsapp_digits(self):
        return self._digits_only(self.contact_whatsapp)

    def __str__(self):
        return self.site_name


class ServiceOffering(models.Model):
    CTA_CHOICES = [
        ("book_screening", "Book Screening"),
        ("products", "Supplements"),
        ("order_request", "Order Support"),
        ("blog", "Health Education"),
        ("contact", "Contact"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField()
    cta_name = models.CharField(max_length=40, choices=CTA_CHOICES, default="book_screening")
    is_active = models.BooleanField(default=True)
    is_featured_home = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "title"]

    @property
    def primary_media(self):
        prefetched = getattr(self, "_prefetched_objects_cache", {}).get("media_items")
        if prefetched is not None:
            for item in prefetched:
                if item.is_primary:
                    return item
            return prefetched[0] if prefetched else None
        return self.media_items.filter(is_primary=True).first() or self.media_items.first()

    def __str__(self):
        return self.title


class ClinicLocation(models.Model):
    name = models.CharField(max_length=140)
    featured_image = models.FileField(
        upload_to="locations",
        blank=True,
        validators=[IMAGE_FILE_VALIDATOR],
    )
    address = models.CharField(max_length=220)
    phone = models.CharField(max_length=30)
    whatsapp = models.CharField(max_length=30, blank=True)
    hours = models.CharField(max_length=120)
    maps_url = models.URLField(blank=True)
    services_text = models.TextField(
        blank=True,
        help_text="Enter one service per line for display badges.",
    )
    is_active = models.BooleanField(default=True)
    is_featured_home = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "name"]

    @property
    def services_list(self):
        return [line.strip() for line in self.services_text.splitlines() if line.strip()]

    @property
    def phone_link(self):
        digits = "".join(ch for ch in (self.phone or "") if ch.isdigit())
        return f"tel:+{digits}" if digits else "#"

    @property
    def whatsapp_link(self):
        digits = "".join(ch for ch in (self.whatsapp or "") if ch.isdigit())
        return f"https://wa.me/{digits}" if digits else "#"

    def preview_tag(self):
        return single_image_preview(self.featured_image, self.name)

    preview_tag.short_description = "Preview"

    def __str__(self):
        return self.name


class PatientResource(models.Model):
    URL_CHOICES = [
        ("book_screening", "Book Screening"),
        ("order_request", "Order Support"),
        ("blog", "Health Education"),
        ("contact", "Contact"),
        ("products", "Supplements"),
        ("services", "Services"),
        ("locations", "Locations"),
    ]

    title = models.CharField(max_length=140)
    description = models.TextField()
    url_name = models.CharField(max_length=40, choices=URL_CHOICES, default="book_screening")
    label = models.CharField(max_length=80, default="Open")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title


class HomeMetric(models.Model):
    value = models.CharField(max_length=40)
    title = models.CharField(max_length=100)
    featured_image = models.FileField(
        upload_to="metrics",
        blank=True,
        validators=[IMAGE_FILE_VALIDATOR],
    )
    description = models.CharField(max_length=220, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "title"]

    def preview_tag(self):
        return single_image_preview(self.featured_image, self.title)

    preview_tag.short_description = "Preview"

    def __str__(self):
        return f"{self.value} - {self.title}"


class ProductMedia(MediaAssetBase):
    media_directory = "products"
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media_items")

    class Meta(MediaAssetBase.Meta):
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.product.name} media"


class TestimonialMedia(MediaAssetBase):
    media_directory = "testimonials"
    testimonial = models.ForeignKey(Testimonial, on_delete=models.CASCADE, related_name="media_items")

    class Meta(MediaAssetBase.Meta):
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.testimonial.name} media"


class ServiceMedia(MediaAssetBase):
    media_directory = "services"
    service = models.ForeignKey(ServiceOffering, on_delete=models.CASCADE, related_name="media_items")

    class Meta(MediaAssetBase.Meta):
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.service.title} media"


class AboutMedia(MediaAssetBase):
    media_directory = "about"
    site_settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name="about_media")

    class Meta(MediaAssetBase.Meta):
        ordering = ["display_order", "created_at"]
        verbose_name = "About media"
        verbose_name_plural = "About media"

    def __str__(self):
        return f"{self.site_settings.site_name} about media"
