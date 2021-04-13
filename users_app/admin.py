from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users_app.models import CustomUser

admin.site.register(CustomUser, UserAdmin)
