from django.contrib import admin
from .models import Item, Ad


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('item_name', 'city', 'description', 'contact_info',)
    readonly_fields = ('time',)


class AdAdmin(admin.ModelAdmin):
    search_fields = ('ad_name',)
    readonly_fields = ('time', 'last_update',)

admin.site.register(Item, ItemAdmin)
admin.site.register(Ad, AdAdmin)
