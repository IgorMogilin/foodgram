from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.authtoken.models import TokenProxy

from .forms import RequiredFieldsUserCreationForm
from .models import User


TokenProxy._meta.verbose_name = 'Токен'
TokenProxy._meta.verbose_name_plural = 'Токены'


admin.site.unregister(TokenProxy)


@admin.register(TokenProxy)
class TranslateTokenAdmin(admin.ModelAdmin):
    pass


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
