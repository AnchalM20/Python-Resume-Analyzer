from django.contrib import admin

from .models import registeredUser
from django.contrib.auth.admin import UserAdmin

class ResumeDataAdmin(admin.ModelAdmin):
    search_fields = ["username","email",]
    list_filter = ["username","email"]
    list_display = ["username","email",]


# Register your models here.
admin.site.register(registeredUser, UserAdmin)
