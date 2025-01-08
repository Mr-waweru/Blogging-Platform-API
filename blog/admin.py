from django.contrib import admin
from .models import *

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_superuser", "is_staff", "is_active")

admin.site.register(CustomUser, CustomUserAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_display = ("name",)
admin.site.register(Category)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)

admin.site.register(Tag, TagAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Rating)
