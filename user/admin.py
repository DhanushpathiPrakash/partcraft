from django.contrib import admin
from user.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserModelAdmin(BaseUserAdmin):
    list_display = ["email", "name", "tc", "is_admin", "is_edit", "is_delete"]
    list_filter = ["is_admin"]
    fieldsets = [
        ('User Credentials', {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name", "tc",]}),
        ("verification", {"fields": ["is_verified"]}),
        ("Permission", {"fields": ["is_admin", "is_edit", "is_delete"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "tc", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", 'id']
    filter_horizontal = []


admin.site.register(User, UserModelAdmin)