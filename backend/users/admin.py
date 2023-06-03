from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'bio', 'email', 'role')
    list_editable = ('role',)
