from django.contrib import admin
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('item_name', 'city', 'description',)

admin.site.register(Item, ItemAdmin)
