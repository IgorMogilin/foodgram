from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import RequiredFieldsUserCreationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = RequiredFieldsUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar')
        }),
        ('Права доступа', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser'
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2'
            ),
        }),
    )
