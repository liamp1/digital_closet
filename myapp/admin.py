from django.contrib import admin
from .models import Item, Category, Color, Brand

# Register your models here.

admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Brand)