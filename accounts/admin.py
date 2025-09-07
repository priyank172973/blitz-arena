from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # show rating in list
    list_display = ("username", "email", "rating", "is_staff", "is_active")
    # quick filter/sort later
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "matches", "peak_rating", "last_rating_change", "last_active")
    search_fields = ("user__username", "user__email")


# Register your models here.
