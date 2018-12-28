from django.contrib import admin
from .models import Item, Ad, Profile


class ItemAdmin(admin.ModelAdmin):
    search_fields = ('item_name', 'city', 'description', 'contact_info',)
    readonly_fields = ('time',)


class AdAdmin(admin.ModelAdmin):
    search_fields = ('city', 'title',)
    readonly_fields = ('time', 'last_update',)


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('contact_info',)

admin.site.register(Item, ItemAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(Profile, ProfileAdmin)
