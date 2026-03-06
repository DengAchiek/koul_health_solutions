from django import forms
from django.contrib.auth import get_user_model
from .models import OrderRequest, Product, ScreeningBooking


class ScreeningBookingForm(forms.ModelForm):
    class Meta:
        model = ScreeningBooking
        fields = [
            "full_name",
            "phone",
            "email",
            "preferred_date",
            "preferred_time",
            "interest",
            "notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "phone": forms.TextInput(attrs={"placeholder": "e.g. +254 7XX XXX XXX"}),
            "email": forms.EmailInput(attrs={"placeholder": "Optional"}),
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "preferred_time": forms.TimeInput(attrs={"type": "time"}),
            "interest": forms.TextInput(attrs={"placeholder": "What would you like help with?"}),
            "notes": forms.Textarea(attrs={"placeholder": "Any extra info you want the consultant to know..."}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if len(phone) < 9:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone


class OrderRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)

    class Meta:
        model = OrderRequest
        fields = [
            "full_name",
            "phone",
            "email",
            "product",
            "quantity",
            "delivery_option",
            "delivery_location",
            "notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "phone": forms.TextInput(attrs={"placeholder": "e.g. +254 7XX XXX XXX"}),
            "email": forms.EmailInput(attrs={"placeholder": "Optional"}),
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "delivery_location": forms.TextInput(attrs={"placeholder": "If delivery: area/estate/city"}),
            "notes": forms.Textarea(attrs={"placeholder": "Any preferences or questions..."}),
        }

    def clean(self):
        cleaned = super().clean()
        delivery_option = cleaned.get("delivery_option")
        delivery_location = (cleaned.get("delivery_location") or "").strip()

        if delivery_option == "delivery" and not delivery_location:
            self.add_error("delivery_location", "Please enter a delivery location.")
        return cleaned

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if len(phone) < 9:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Admin username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Admin email"}),
        }
